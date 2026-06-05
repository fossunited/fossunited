# Fix: Reviewer Features Not Reflected in UI

## Background

The backend (Python/Frappe doctypes, APIs) for three reviewer improvements already exists but is either broken in the UI code or has never been built and deployed to the bench. The dashboard **has no `dist/` folder** — it has never been built, so the browser is served a stale/empty asset bundle. All frontend code changes need a `yarn build` inside the container to take effect.

## Root Cause: Dashboard Never Built

The Vite build output goes to `fossunited/public/dashboard/`. That directory does not exist. Without it, the review page likely serves a 404 or falls back to an older bundle. **Every fix below is worthless until the bundle is rebuilt.**

---

## Identified Issues

### 1. `ReviewCommentBox.vue` — `computed` not imported

`computed` is used on line 44 (`const submissionData = computed(...)`) but is **not in the `import { ref, inject }` from 'vue'** line. This is a runtime error that silently breaks the entire `ReviewCommentBox`.

**Fix:** Add `computed` to the Vue import.

---

### 2. "Save & Next" button — emits `'next'` but `ProposalDetails` never wires it up

`ReviewCommentBox` emits `'next'` on Save & Next/Skip/Abstain. `ReviewSection` **does not** listen for or re-emit `'next'`. `ProposalDetails` **does not** emit `'next'` either. The `ReviewPage` calls `@next="goToNextSubmission"` on `<ProposalDetails>` — but that event never fires.

**Fix:** Thread the `'next'` event through `ReviewSection → ProposalDetails`.

---

### 3. Review Assignments — filter is backend-only, no UI indicator

When `proposal_visibility == "Only Assigned"`, the backend correctly filters proposals but the UI doesn't show the reviewer which proposals are assigned to them (no "Assigned" badge or indicator on list items, no mention in the phase info box beyond the bullet point).

**Fix:** The phase info banner on `ReviewPage` already mentions this. We should also add a small "Assigned" badge on `SubmissionListItem` when in reviewer mode, using the `_is_assigned` flag (which needs to be added to the submissions API response).

---

### 4. Scoring system — categories shown but score is not displayed in "Your Review" card

In `ReviewSection.vue`, the "Your Review" card (the `isReviewOwner` block) shows remarks and approval status, but **never shows the scores the reviewer entered**. The "Other reviewer" block does show scores. This is inconsistent.

**Fix:** Add a scores table to the "Your Review" block in `ReviewSection.vue`.

---

### 5. `ReviewStatsComponent` — doesn't include weighted total score summary

The stats bar shows Approvals/Rejections/Not Sure counts but doesn't show the average weighted score (from `total_score` on `FOSS Event CFP Review`). This makes the improved scoring system invisible.

**Fix:** Extend `get_reviews_for_proposal` to return `total_score`, and add an "Avg. Score" stat to `ReviewStatsComponent`.

---

## Proposed Changes

### Frontend: `dashboard/src/`

#### [MODIFY] [ReviewCommentBox.vue](file:///var/home/james/dev/fossunited-cfps/fossunited/dashboard/src/components/reviewers/ReviewCommentBox.vue)
- Add `computed` to the Vue import (bug fix).

#### [MODIFY] [ReviewSection.vue](file:///var/home/james/dev/fossunited-cfps/fossunited/dashboard/src/components/reviewers/ReviewSection.vue)
- Add `emit('next')` propagation: listen for `'next'` from `ReviewCommentBox` and re-emit it.
- Add scores display to the "Your Review" own-review card (matching the other reviewer card's score table).

#### [MODIFY] [ProposalDetails.vue](file:///var/home/james/dev/fossunited-cfps/fossunited/dashboard/src/components/reviewers/ProposalDetails.vue)
- Add `'next'` to `defineEmits` and forward it from `ReviewSection` → parent.

#### [MODIFY] [ReviewStatsComponent.vue](file:///var/home/james/dev/fossunited-cfps/fossunited/dashboard/src/components/reviewers/ReviewStatsComponent.vue)
- Add "Avg. Score" computed stat using `total_score` from reviews (show only if any reviews have scores).

#### [MODIFY] [SubmissionListItem.vue](file:///var/home/james/dev/fossunited-cfps/fossunited/dashboard/src/components/event/cfp/SubmissionListItem.vue)
- Add an "Assigned" badge when `submission._is_assigned === true` and in reviewer mode.

---

### Backend: `fossunited/`

#### [MODIFY] [reviewer.py](file:///var/home/james/dev/fossunited-cfps/fossunited/fossunited/api/reviewer.py)
- `get_reviews_for_proposal`: already returns `*` fields which includes `total_score` — no change needed.

#### [MODIFY] [cfp.py](file:///var/home/james/dev/fossunited-cfps/fossunited/fossunited/api/cfp.py)
- `get_cfp_submissions`: add `_is_assigned` field to each submission, set to `True` if the current reviewer has an assignment for it (use a bulk query against `CFP Reviewer Assignment`).

---

### Justfile

#### [MODIFY] [Justfile](file:///var/home/james/dev/fossunited-cfps/fossunited/Justfile)
- Update `build-dashboard` recipe to be the canonical way to rebuild and reflect changes.

---

## Verification Plan

### Automated
- `just build-dashboard` — verify no build errors.
- `curl -I http://localhost:8000/dashboard` — verify 200 response after build.

### Manual (browser)
1. Open `http://localhost:8000/dashboard/review` as a reviewer.
2. Open a proposal → Reviews tab → confirm scoring categories render correctly.
3. Submit a review → click **Save & Next** → confirm it advances to the next proposal.
4. Submit a review → go back → confirm your review shows scores in the "Your Review" card.
5. Confirm "Avg. Score" appears in the stats bar when reviews with scores exist.
6. If "Only Assigned" phase is active, confirm only assigned proposals appear with an "Assigned" badge.

> [!IMPORTANT]
> The dashboard must be **rebuilt** (`just build-dashboard`) and **Frappe assets refreshed** (`bench --site fossunited.localhost clear-cache`) after every frontend change for them to appear in the browser.
