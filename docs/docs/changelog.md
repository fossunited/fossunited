# Tech Reports for FOSS United Platform

<!-- URLs for reference -->
<!-- https://github.com/fossunited/fossunited/pull/ -->
<!-- https://github.com/fossunited/fossunited/issues -->

## FossUnited

📌 **Project Board**: [FOSS United GitHub Project](https://github.com/orgs/fossunited/projects/3/views/1)

### August 2025

| Metric        | Count |
|---------------|-------|
| Issues Closed | 13    |
| PRs merged    | 19    |

Hi everyone,

I'm **Dilip G** (aka *Zororg* on Telegram, or with username `@idlip`), the new Developer for FossUnited. First month on board, replacing Harsh Tandiya as Developer.
This is my first monthly tech report as part of the FossUnited team. I'd love your feedback on the format, content, or anything you'd like to see added in future changelogs. You can share your suggestions via GitHub Issues or drop me an email; whichever works best for you.

---

### 🚀 PR Highlights

#### Jobs & Scheduling

- **[#1080](https://github.com/fossunited/fossunited/pull/1080)** Scheduled expiry for job posts older than 90 days
  Implemented a background scheduler that automatically marks job listings as *expired* after 90 days.
  🔗 Visit: [FossUnited Jobs](https://fossunited.org/jobs)

#### Roles & Permissions

- **[#1087](https://github.com/fossunited/fossunited/pull/1087)** Removed `Lead` role, consolidated under `Core Team Member`.
  Simplified the roles for Chapters and Events. Now, `Core Team Member` has full permissions to manage events and pages.

#### Event Management

- **[#1088](https://github.com/fossunited/fossunited/pull/1088)** Fixed routing to event schedule pages
  Resolved navigation issues—schedule pages now route correctly from both the dashboard and event views.

- **[#1102](https://github.com/fossunited/fossunited/pull/1102)** Auto-close RSVP and CFP forms after event ends
  Extended the event scheduler to automatically close RSVP and Call-for-Proposal forms once the event has concluded.

#### Blog & RSS

- **[#1091](https://github.com/fossunited/fossunited/pull/1091)** RSS feed fixed and enhanced
  The blog's RSS feed is now valid and includes newsletters.
  Thanks to [@captn3m0](https://github.com/captn3m0) for reporting the issue: [#1001](https://github.com/fossunited/fossunited/issues/1001)

#### Timeline Fixes

- **[#1094](https://github.com/fossunited/fossunited/pull/1094)** Prevented crash on `events/timeline` when dates are missing
  Fixed error where events without a start or end date would break the timeline view.

- **[#1109](https://github.com/fossunited/fossunited/pull/1109)** Made event schedule page layout more compact
  Cleaned up visual clutter on the schedule view for easier readability.

#### Team Page & Governance

- **[#1099](https://github.com/fossunited/fossunited/pull/1099)** Updated Teams page with new Governing Board members
  Refreshed the macro logic and added profiles for the newly elected board.
  Announcement: [Meet the first-ever elected community governance board](https://fossunited.org/blog/organization/meet-the-first-ever-elected-community-governance-board-foss-united)

#### Event Metadata Enhancements

- **[#1100](https://github.com/fossunited/fossunited/pull/1100)** Added City and State info for events
  Also reordered social media links to prioritize FOSS and decentralized platforms.

#### Frappe Desk / Office related

- **[#1108](https://github.com/fossunited/fossunited/pull/1108)** Added a scrollbar to long schedule sections
  Improves usability when navigating long lists of proposals.

- **[#1101](https://github.com/fossunited/fossunited/pull/1101)** Introduced "Invited Talk" as a session type
  Enables better support for data related to IndiaFOSS sessions.

---

### 🌟 New Contributor Spotlight

- 🎉 [@HarshPatel5940](https://github.com/HarshPatel5940) made their first contribution:
  - [#1010](https://github.com/fossunited/fossunited/pull/1010): Dynamic user search in Chapter/Events member dashboard
