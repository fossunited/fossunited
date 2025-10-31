# Tech Reports for FOSS United Platform

<!-- URLs for reference -->
<!-- https://github.com/fossunited/fossunited/pull/ -->
<!-- https://github.com/fossunited/fossunited/issues -->

📌 **Project Board**: [FOSS United GitHub Project](https://github.com/orgs/fossunited/projects/3/views/1)

<br>

## October 2025

| Metric        | Count |
|---------------|-------|
| Issues Closed | 28    |
| PRs merged    | 31    |

Hey folks,

It was Hack-tober month!
We've a new [**Volunteers Page**](https://fossunited.org/volunteers) and with initiation of **Dark Theme** support was introduced to it, alongside several UI refinements and [documentation](https://docs.fossunited.org) upgrades. Moving on next month, we will be focusing more on IndiaFOSS related issues and hey if you did not know there are many important (Big) events lined up like MangaloreFOSS, MumbaiFOSS, ChennaiFOSS and [more](https://fossunited.org/events/timeline).

---

### PR Highlights

#### Theme & UI Enhancements

- [#1244](https://github.com/fossunited/fossunited/pull/1244) New **Volunteers Page**
  Added a “Wall of Fame” for active Volunteers with filter and sorting by chapter or user's city.
  Credits: [@jeswinjosu](https://github.com/jeswinjosu)
- [#1247](https://github.com/fossunited/fossunited/pull/1247) Add dark theme support for Volunteers page
  Introduced system-based dark/light mode toggling and persistent theme preference using local storage.
  Note: Its currently only for Volunteers page (initiation of redesign 3.0)
- [#1243](https://github.com/fossunited/fossunited/pull/1243) Fix popover z-index for `AutoComplete` in EmailFormTemplate
  Which did not show recipients popup before in events mailing page.

#### CFP & Review System

- [#1246](https://github.com/fossunited/fossunited/pull/1246) Hide others reviews in CFP review tab
  Prevents reviewer bias by showing only the user’s own reviews, reducing cross-influence while keeping public visibility unchanged.
  Related issue: [#1004](https://github.com/fossunited/fossunited/issues/1004)
- [#1239](https://github.com/fossunited/fossunited/pull/1239) Format CFP review content
  Enabled `tailwindcss` typography for better rendering of review text within CFP details page; WYSIWYG!.
- [#1237](https://github.com/fossunited/fossunited/pull/1237) Add CFP Status Filter
  Added dropdown filters and clickable insight grids for CFP proposals, improving reviewer workflows.
  for example: [IndiaFOSS 2025 CFP](https://fossunited.org/dashboard/cfp/all/indiafoss/2025) (click on those grid cards)
- [#1236](https://github.com/fossunited/fossunited/pull/1236) Show CFP reviewer's review status
  Introduced color-coded reviewer status ("Reviewed") and filtering toggles.

#### Jobs & Grants

- [#1227](https://github.com/fossunited/fossunited/pull/1227) Import Job Board from Desk to Codebase
  Migrated job management from the Frappe Desk interface into the platform’s code for better version control and transparency.
  [Explore Jobs](https://fossunited.org/jobs)
- [#1234](https://github.com/fossunited/fossunited/pull/1234) Project Grants enhancements
  Introduced logo and grant type fields to the "Project Grants" doctype, enabling categorization of fellowships and year-based grouping.
  refer: [Grants page](https://fossunited.org/grants)
- [#1240](https://github.com/fossunited/fossunited/pull/1240) Auto "Show Speaker" visibility in events page.
  Show speakers tab only if populated and display speaker info by default for past events.

#### Chapter & Mailing System

- [#1215](https://github.com/fossunited/fossunited/pull/1215) Chapter Mailing Page
  Added support for chapter-level mailing and campaign tracking, mirroring event mailing capabilities with Chapter level email groups.
  Users have choice to either "Subscribe to mailing list" or not via their RSVP forms. They can edit their preference in [Edit RSVP](https://docs.fossunited.org/attend-event/) to update and remove.
- [#1206](https://github.com/fossunited/fossunited/pull/1206) Email Group Subscription via RSVP
  Added `subscribe to chapter mailing` checkboxes on RSVP and ticket forms, ensuring attendees are properly linked to event/chapter mailing groups.

#### Event & RSVP Management

- [#1213](https://github.com/fossunited/fossunited/pull/1213) RSVP toggle improvements
  Users can now toggle RSVP/Un-RSVP directly with updated UI states to let Organizer know that they are "not attending".
- [#1214](https://github.com/fossunited/fossunited/pull/1214) RSVP insights grouping
  Dashboard enhancements now group RSVP data by attendance, improving analytics for event organizers. Shows two groups "Attending" and "Not attending" (not shown by default)

#### Documentation & Developer Tools

- [#1216](https://github.com/fossunited/fossunited/pull/1216) Major Docs overhaul
  Merged and enhanced documentation from the frappe Wiki, now with improved navigation, Docker setup guide, search functionality, and content for volunteering, clubs, and events.
- [#1189](https://github.com/fossunited/fossunited/pull/1189) Vale Docs Linting
  Integrated Vale for consistent doc style and vocabulary validation.
- [#1204](https://github.com/fossunited/fossunited/pull/1204) Simplified RSS feed
  Cleaned up RSS feed to include only blog posts, removing newsletters for better content focus.

  Stay nerdy: https://fossunited.org/rss.xml

#### Internal Improvements & Dependencies

- [#1230](https://github.com/fossunited/fossunited/pull/1230) Bump `prettier-plugin-jinja-template` to v2.1.0
- [#1233](https://github.com/fossunited/fossunited/pull/1233) Bump `globals` from 15.9.0 → 16.4.0
- [#1235](https://github.com/fossunited/fossunited/pull/1235) Batch dependency upgrades (`vite`, `esbuild`, `rollup`, `postcss`, etc.)
- [#1186](https://github.com/fossunited/fossunited/pull/1186) Yarn lock bump
- [#1202](https://github.com/fossunited/fossunited/pull/1202) Expose user fields in `get_session_user_profile` API

---

### New Contributor Spotlight

- [@dependabot[bot]](https://github.com/dependabot) Yea, for Automation of package updates!

---

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
  Implemented a QR code based quick check-in scanner to log check-in details. Both pages `/dashboard/event/.../quick-checkin` and `/dashboard/event/.../checkins` use this component to scan QR.

#### Event Schedule
Could not complete the Schedule re-design, so added some features to enhance UX.

- [#1126](https://github.com/fossunited/fossunited/pull/1126) Search by Speaker in proposal (CFP) page
  Although it has a frappe filter to narrow, it would be convenient to just type and search by speaker name.
- [#1132](https://github.com/fossunited/fossunited/issues/1132) Fix Event Schedule ICS download
  Due to some events having end `datetime` > start `datetime`, the API was throwing an error.
- [#1158](https://github.com/fossunited/fossunited/issues/1158) Search support in Schedule page
  Search whole Event schedule in flat List based on Talk Title, Speaker name, Designation and category. Also card shows Hall and Date as Indicator
- [#1151](https://github.com/fossunited/fossunited/issues/1151) Schedule Download formats
  Schedule can be downloaded in various formats now. CSV | ICS | Orgmode | Markdown and so on.
  Further plan is to make PDF generation in FOSS theme using `Typst`

---
### New Contributor Spotlight
- [@agriyakhetarpal](https://github.com/agriyakhetarpal) made their first contribution:
  - [#1142](https://github.com/fossunited/fossunited/pull/1142): Added Zulip logo for chapters
    With merge of Zulip into svgl, we now have Zulip support into socials link for Chapter Info.
  - Related [PR](https://github.com/fossunited/fossunited/pull/1146) on adding Bluesky and dev.to logo for FOSS user profile page

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

I'm **Dilip G** (also known as *Zororg* on Telegram, or with username `@idlip`), the new Developer for FOSS United. First month on board, after Harsh Tandiya as Developer.
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
  Resolved navigation issues schedule pages now route correctly from both the dashboard and event views.
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
- [#1068](https://github.com/fossunited/fossunited/issues/1068) Doc and guide on setting up FossUnited platform with NixOS. I plan to extend this further more.

#### Job Management
- [#1077](https://github.com/fossunited/fossunited/pull/1077) Added date of posting for each job card and closing for expired ones
