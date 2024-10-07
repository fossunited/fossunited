from datetime import datetime, timedelta

import frappe
from faker import Faker
from frappe.tests.utils import FrappeTestCase

from fossunited.doctype_ids import HACKATHON, HACKATHON_PARTICIPANT, HACKATHON_TEAM


class TestFOSSHackathonTeam(FrappeTestCase):
    def setUp(self):
        self.faker = Faker()
        self.hackathon = frappe.get_doc(
            {
                "doctype": HACKATHON,
                "hackathon_name": self.faker.name(),
                "permalink": self.faker.slug(),
                "start_date": datetime.now(),
                "end_date": datetime.now() + timedelta(days=1),
                "hackathon_description": self.faker.text(),
                "max_team_size": 2,
            }
        ).insert()

        self.team = frappe.get_doc(
            {
                "doctype": HACKATHON_TEAM,
                "team_name": self.faker.name(),
                "hackathon": self.hackathon.name,
            }
        ).insert()

        self.participants = []
        for _ in range(3):  # since max_team_size is 2, we need 3 participants to test the code
            participant = frappe.get_doc(
                {
                    "doctype": HACKATHON_PARTICIPANT,
                    "full_name": self.faker.name(),
                    "email": self.faker.email(),
                    "hackathon": self.hackathon.name,
                }
            ).insert()
            self.participants.append(participant)

    def tearDown(self):
        self.team.delete()
        for participant in self.participants:
            participant.delete()
        self.hackathon.delete()

    def test_add_member_to_team(self):
        for _ in range(self.hackathon.max_team_size):
            self.team.append("members", {"member": self.participants[_].name})
        self.team.save()
        self.assertEqual(len(self.team.members), self.hackathon.max_team_size)

    def test_add_member_exceeding_max_size(self):
        for _ in range(self.hackathon.max_team_size + 1):
            self.team.append("members", {"member": self.participants[_].name})
        self.assertRaises(frappe.exceptions.ValidationError, self.team.save)
