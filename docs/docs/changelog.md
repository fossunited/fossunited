# Tech Reports for FOSS United Platform

<!-- URLs for reference -->
<!-- https://github.com/fossunited/fossunited/pull/ -->
<!-- https://github.com/fossunited/fossunited/issues -->

📌 **Project Board**: [FOSS United GitHub Project](https://github.com/orgs/fossunited/projects/3/views/1)

<br>

## September 2025

| Metric        | Count |
|---------------|-------|
| Issues Closed | 10    |
| PRs merged    | 32    |

Hi again,
We had Successfully Concluded our 5th Edition of IndiaFOSS (2025) on 20-21 Sept. This month had most focus on Schedule page.

---
### PR Highlights

#### Event Management

- [#1125](https://github.com/fossunited/fossunited/pull/1125) De-clutter the Events timeline page
  Provided filter to choose Chapter type (City | Club | Conference) and made City filter to show only Cities
  /events pages takes preference to show Only City and Conference, hiding FOSS Club events
  Related issue [#1144](https://github.com/fossunited/fossunited/issues/1144) and PR [#1145](https://github.com/fossunited/fossunited/pull/1145)
- [#1128](https://github.com/fossunited/fossunited/pull/1128) Small Doc on purpose of `event_permalink`
  Some users might confuse with the term permalink, so added some doc to give info that it means page 'route' (alias)


#### Ticket Management

- [#1118](https://github.com/fossunited/fossunited/pull/1118) Make ticket transfer page public
  We noticed that not everyone who bought ticket had FossUnited account, so with added security tests, we made Ticket transfer page public to avoid exploits.
- [#1147](https://github.com/fossunited/fossunited/pull/1147) Added QR code scanner for Ticket Check-ins
  Implemented a QR code based quick check-in scanner to log check-in details. Both pages `/dashboard/event/.../quick-checkin` and `/dashboard/event/.../checkins` utilize this component to scan QR.

#### Event Schedule
Could not complete the Schedule re-design, so added some features to enhance UX.

- [#1126](https://github.com/fossunited/fossunited/pull/1126) Search by Speaker in proposal (CFP) page
  Although it has a frappe filter to narrow, it would be convenient to just type and search by speaker name.
- [#1132](https://github.com/fossunited/fossunited/issues/1132) Fix Event Schedule ICS download
  Due to some events having end datetime > start datetime, the API was throwing an error.
- [#1158](https://github.com/fossunited/fossunited/issues/1158) Search support in Schedule page
  Search whole Event schedule in flat List based on Talk Title, Speaker name, Designation and category. Also card shows Hall and Date as Indicator
- [#1151](https://github.com/fossunited/fossunited/issues/1151) Schedule Download formats
  Schedule can be downloaded in various formats now. CSV | ICS | Orgmode | Markdown and so on.
  Further plan is to make PDF generation in FOSS theme using `Typst`

---
### New Contributor Spotlight
- [@agriyakhetarpal](https://github.com/agriyakhetarpal) made their first contribution:
  - [#1142](https://github.com/fossunited/fossunited/pull/1142): Added Zulip logo for chapters
    With merge of Zulip into svgl, we now have zulip support into socials link for Chapter Info.
  - Related [PR](https://github.com/fossunited/fossunited/pull/1146) on adding Bluesky and dev.to logo for Foss user profile page

- [@arunppsg](https://github.com/arunppsg) made their first contribution:
  - [#1167](https://github.com/fossunited/fossunited/pull/1167): Added more docs
    Complementing to [#1150](https://github.com/fossunited/fossunited/issues/1150), Arun added some missing docs for events, social media and more.


<br>

## August 2025

| Metric        | Count |
|---------------|-------|
| Issues Closed | 13    |
| PRs merged    | 19    |

Hi everyone,

I'm **Dilip G** (aka *Zororg* on Telegram, or with username `@idlip`), the new Developer for FOSS United. First month on board, after Harsh Tandiya as Developer.
This is my first monthly tech report as part of the FOSS United team. I'd love your feedback on the format, content, or anything you'd like to see added in future changelogs. You can share your suggestions via GitHub Issues or drop me an email; whichever works best for you.

---

### PR Highlights

#### Jobs & Scheduling

- [#1080](https://github.com/fossunited/fossunited/pull/1080) Scheduled expiry for job posts older than 90 days
  Implemented a background scheduler that automatically marks job listings as *expired* after 90 days.
  🔗 Visit: [FOSS United Jobs](https://fossunited.org/jobs)

#### Roles & Permissions

- [#1087](https://github.com/fossunited/fossunited/pull/1087) Removed `Lead` role, consolidated under `Core Team Member`.
  Simplified the roles for Chapters and Events. Now, `Core Team Member` has full permissions to manage events and pages.

#### Event Management

- [#1088](https://github.com/fossunited/fossunited/pull/1088) Fixed routing to event schedule pages
  Resolved navigation issues—schedule pages now route correctly from both the dashboard and event views.
- [#1102](https://github.com/fossunited/fossunited/pull/1102) Auto-close RSVP and CFP forms after event ends
  Extended the event scheduler to automatically close RSVP and Call-for-Proposal forms once the event has concluded.

#### Blog & RSS

- [#1091](https://github.com/fossunited/fossunited/pull/1091) RSS feed fixed and enhanced
  The blog's RSS feed is now valid and includes newsletters.
  Thanks to [@captn3m0](https://github.com/captn3m0) for reporting the issue: [#1001](https://github.com/fossunited/fossunited/issues/1001)

#### Timeline Fixes

- [#1094](https://github.com/fossunited/fossunited/pull/1094) Prevented crash on `events/timeline` when dates are missing
  Fixed error where events without a start or end date would break the timeline view.
- [#1109](https://github.com/fossunited/fossunited/pull/1109) Made event schedule page layout more compact
  Cleaned up visual clutter on the schedule view for easier readability.

#### Team Page & Governance

- [#1099](https://github.com/fossunited/fossunited/pull/1099) Updated Teams page with new Governing Board members
  Refreshed the macro logic and added profiles for the newly elected board.
  Announcement: [Meet the first-ever elected community governance board](https://fossunited.org/blog/organization/meet-the-first-ever-elected-community-governance-board-foss-united)

#### Event Metadata Enhancements

- [#1100](https://github.com/fossunited/fossunited/pull/1100) Added City and State info for events
  Also reordered social media links to prioritize FOSS and decentralized platforms.

#### Frappe Desk / Office related

- [#1108](https://github.com/fossunited/fossunited/pull/1108) Added a scrollbar to long schedule sections
  Improves usability when navigating long lists of proposals.
- [#1101](https://github.com/fossunited/fossunited/pull/1101) Introduced "Invited Talk" as a session type
  Enables better support for data related to IndiaFOSS sessions.

---

### New Contributor Spotlight

- [@HarshPatel5940](https://github.com/HarshPatel5940) made their first contribution:
  - [#1010](https://github.com/fossunited/fossunited/pull/1010): Dynamic user search in Chapter/Events member dashboard



<br>

## July 2025

The FOSS United platform was mostly under maintenance mode during this period. This was mostly my scrutiny period with some given tasks for two weeks.

---
### PR Highlights

#### Setup with NixOS
- [#1068](https://github.com/fossunited/fossunited/issues/1068) Doc and guide on setting up FossUnited platform with Nixos. I plan to extend this further more.

#### Job Management
- [#1077](https://github.com/fossunited/fossunited/pull/1077) Added date of posting for each job card and closing for expired ones
