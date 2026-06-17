import frappe
from frappe.tests.utils import FrappeTestCase

from fossunited.api.tickets import (
    bulk_create_speaker_coupons,
    get_speaker_coupon_preview,
)
from fossunited.doctype_ids import CHAPTER, EVENT, FREE_TICKET_CODE, PROPOSAL
from fossunited.tests.factories import (
    FOSSChapterEventFactory,
    FOSSChapterFactory,
    FOSSEventCFPFactory,
    FOSSEventCFPSubmissionFactory,
    FreeTicketCodeFactory,
    UserFactory,
)


def _speaker(email, name="Speaker"):
    return {
        "full_name": name,
        "email": email,
        "designation": "Speaker",
        "organization": "alwaysFOSS",
        "bio": "Touch Grass and watch OnePiece",
    }


class TestSpeakerCoupons(FrappeTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        frappe.set_user("Administrator")
        cls.team_member = UserFactory.create("with_foss_website_user_role")
        cls.chapter = FOSSChapterFactory.create("with_members", members=[cls.team_member.name])
        cls.event = FOSSChapterEventFactory.create(chapter=cls.chapter.name)
        cls.cfp = FOSSEventCFPFactory.create(event=cls.event.name)

    @classmethod
    def tearDownClass(cls):
        frappe.set_user("Administrator")
        frappe.db.delete(FREE_TICKET_CODE, {"event": cls.event.name})
        for name in frappe.get_all(PROPOSAL, filters={"event": cls.event.name}, pluck="name"):
            frappe.delete_doc(PROPOSAL, name, force=True, ignore_missing=True)
        cls.cfp.delete(force=True)
        frappe.delete_doc(EVENT, cls.event.name, force=True)
        frappe.delete_doc(CHAPTER, cls.chapter.name, force=True)
        super().tearDownClass()

    def tearDown(self):
        frappe.set_user("Administrator")
        frappe.db.delete(FREE_TICKET_CODE, {"event": self.event.name})
        for name in frappe.get_all(PROPOSAL, filters={"event": self.event.name}, pluck="name"):
            frappe.delete_doc(PROPOSAL, name, force=True, ignore_missing=True)

    def _approved(self, speakers):
        return FOSSEventCFPSubmissionFactory.create(
            "with_approved_status",
            linked_cfp=self.cfp.name,
            event=self.event.name,
            speakers=speakers,
        )

    def test_creates_coupon_for_approved_speaker(self):
        self._approved([_speaker("alice@test.com")])
        frappe.set_user(self.team_member.name)

        result = bulk_create_speaker_coupons(event=self.event.name, max_count=1)

        self.assertEqual(result["created"], 1)
        self.assertTrue(
            frappe.db.exists(
                FREE_TICKET_CODE,
                {"event": self.event.name, "mapped_email": "alice@test.com"},
            )
        )

    def test_multi_talk_speaker_gets_multiplied_max_count(self):
        # Same speaker, two approved proposals
        self._approved([_speaker("bob@test.com")])
        self._approved([_speaker("bob@test.com")])
        frappe.set_user(self.team_member.name)

        bulk_create_speaker_coupons(event=self.event.name, max_count=2)

        max_count = frappe.db.get_value(
            FREE_TICKET_CODE,
            {"event": self.event.name, "mapped_email": "bob@test.com"},
            "max_count",
        )
        self.assertEqual(int(max_count), 4)  # 2 per talk * 2 talks

    def test_idempotent_skips_existing(self):
        self._approved([_speaker("carol@test.com")])
        frappe.set_user(self.team_member.name)

        bulk_create_speaker_coupons(event=self.event.name, max_count=1)
        result = bulk_create_speaker_coupons(event=self.event.name, max_count=1)

        self.assertEqual(result["created"], 0)
        self.assertEqual(result["skipped"], 1)

    def test_non_approved_proposals_excluded(self):
        # Status defaults to "Review Pending" — no approved proposals
        FOSSEventCFPSubmissionFactory.create(
            linked_cfp=self.cfp.name,
            event=self.event.name,
            speakers=[_speaker("pending@test.com")],
        )
        frappe.set_user(self.team_member.name)

        result = bulk_create_speaker_coupons(event=self.event.name, max_count=1)

        self.assertEqual(result["created"], 0)

    def test_preview_reflects_state(self):
        self._approved([_speaker("diana@test.com")])
        self._approved([_speaker("eve@test.com")])
        FreeTicketCodeFactory.create(
            event=self.event.name,
            mapped_email="diana@test.com",
            tier="Speaker/Workshop Host",
        )
        frappe.set_user(self.team_member.name)

        preview = get_speaker_coupon_preview(event=self.event.name)

        self.assertEqual(preview["total"], 2)
        self.assertEqual(preview["already_has"], 1)
        self.assertEqual(preview["will_create"], 1)
