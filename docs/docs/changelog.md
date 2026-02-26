# Tech Reports for FOSS United Platform

<!-- URLs for reference -->
<!-- https://github.com/fossunited/fossunited/pull/ -->
<!-- https://github.com/fossunited/fossunited/issues -->

📌 **Project Board**: [FOSS United GitHub Project](https://github.com/orgs/fossunited/projects/3/views/1)

Please find the TLDR reports for each blog in blog posts and forum thread:

- Blog post: [https://fossunited.org/blog/tech-report](https://fossunited.org/blog/tech-report)
- Forum thread: [https://forum.fossunited.org/t/foss-united-monthly-tech-report/6431](https://forum.fossunited.org/t/foss-united-monthly-tech-report/6431)

## February 2026

| Metric        | Count |
|---------------|-------|
| Issues Closed | 8     |
| PRs merged    | 32    |

Hello,

February was all about **FOSS Hack 2026**! We shipped the redesigned hackathon page, added dark mode support to the dashboard, implemented crucial security fixes, and polished the RSVP experience.

---

### PR Highlights

#### Hackathon Page Redesign

- [#1430](https://github.com/fossunited/fossunited/pull/1430) **Redesigned Default Hackathon Page**
  Complete redesign of default hackathon pages to match the event page design with v3.0 styling. Better visual hierarchy, improved sponsor display, and cleaner navigation. Listing of localhosts, submissions button, mentors and so on.

    Visit: [FOSS Hack 2026](https://fossunited.org/hack/fosshack26)

- [#1429](https://github.com/fossunited/fossunited/pull/1429) **Project Contribution Carousel**
  Added carousel cards showcasing project contributions on the FOSS Hack 2026 page. Highlights partner projects and informs open contribution to FOSS ecosystem.

    Credits: Jeswin Josu for design.
    View carousel: [FOSS Hack 2026 Landing](https://fossunited.org/fosshack)

- [#1417](https://github.com/fossunited/fossunited/pull/1417) **Hackathon Projects Listing Page**
  Enhanced hackathon projects listing page with improved layout and filtering.

- Updated FOSS Hack 2026 content with partner projects, registration stats, localhost information, and carousel images.
- Hackathon registration now shows proper validation when closed or past end date to avoid new participants.
- Added city names for registration convenience.
- Fixed localhost participant counts to show all applied as interested, balanced with accepted counts.

#### Dashboard Dark Mode

- [#1428](https://github.com/fossunited/fossunited/pull/1428) **Dashboard Dark Theme Support**
  Added dark mode support to the entire dashboard using frappe-ui color system! The dashboard now respects system theme preferences and provides a consistent dark mode experience.

- DocsInfo component now has a close button to hide help messages.
- Applied proper color scales and theme-aware styling across all dashboard components importing frappe-ui method of doing things.

    Related issue to address in the future: [#1221](https://github.com/fossunited/fossunited/issues/1221)

#### Security Improvements

- [#1398](https://github.com/fossunited/fossunited/pull/1398) **Rate Limiting & Ticket Transfer Validation**
  Added rate limiting to prevent abuse and fixed ticket transfer validation vulnerabilities.
  Credits: [@ni5arga](https://github.com/ni5arga) (Nisarga Adhikary) and [@kewonit](https://github.com/kewonit) (Kartik Kulloli) for security research

- [#1397](https://github.com/fossunited/fossunited/pull/1397) **Hackathon Participant API Security**
  Hardened `create_participant` API to only act on session user requests, preventing email/profile manipulation.

- [#1401](https://github.com/fossunited/fossunited/pull/1401) **Team Member Validation**
  Implemented team member checks in project creation to prevent unauthorized access.
  Credits: [@ni5arga](https://github.com/ni5arga) (Nisarga Adhikary)

- **XSS Prevention**
  Sanitized text editor content across user profiles, project descriptions, CFP submissions, and bio fields to prevent XSS attacks. Content is now cleaned before saving via `db.set_value`.

- [cb1e74de318476e610f7c0d584d145bbade70419](https://github.com/fossunited/fossunited/commit/cb1e74de318476e610f7c0d584d145bbade70419) **Free Ticket Security**
  Prevented same email from claiming multiple free passes.

#### RSVP Improvements

- [#1419](https://github.com/fossunited/fossunited/pull/1419) **RSVP Success Feedback for Guests**
  Guest users now get clear success feedback after RSVP submission. Submit button is disabled after click to prevent duplicate submissions.

    Although should be taken care via DB-level uniqueness [#1418](https://github.com/fossunited/fossunited/issues/1418)

- [#1405](https://github.com/fossunited/fossunited/pull/1405) **RSVP Insights Table Toggle**
  Added table view toggle in RSVP insights. Manual check-in button now only enabled during event days for better UX.

    Related: [frappe-ui PR #488](https://github.com/frappe/frappe-ui/pull/488).
    Credits to Harsh patel for reporting bad design.

- Adapted RSVP pages to v3 design with improved forms and better visual consistency.
- Simplified feedback messages - logged-in users can edit their responses directly.
- Render field macro now supports required field indicators.

#### Event & Timeline Enhancements

- [#1436](https://github.com/fossunited/fossunited/pull/1436) **Event Grants in Timeline**
  Accepted event grants now appear in the events timeline and RSS feed as upcoming events. Links to external website if provided, otherwise to grants page.

    Visit: [Events Timeline](https://fossunited.org/events/timeline)

- [#1435](https://github.com/fossunited/fossunited/pull/1435) **Compact Agenda with Icons**
  Made event agenda more compact for halls/dates (especially useful for hackathon pages). Uses `talk_video` field for online meeting links when no linked CFP or hall is given.

- Event cards now show "TBA" for location when not specified.
- FOSS user profiles now only show published events and include events where user volunteered.

#### Hackathon Management

- [#1425](https://github.com/fossunited/fossunited/pull/1425) **Email Group Sync Unit Tests**
  Added comprehensive unit tests for hackathon participant email group synchronization.

- [#1424](https://github.com/fossunited/fossunited/pull/1424) **Localhost Email Group Sync**
  Hackathon participants are now automatically synced to localhost email groups based on their localhost status.

- [#1414](https://github.com/fossunited/fossunited/pull/1414) **Hackathon API Unit Tests**
  Added unit tests for hackathon API endpoints to ensure deterministic behavior and catch regressions early.

- [#1415](https://github.com/fossunited/fossunited/pull/1415) **Team & Project Stats**
  Fixed landing page stats to show proper team and project counts with correct localhost attendance numbers.

- [#1412](https://github.com/fossunited/fossunited/pull/1412) **Permission & Controller Updates**
  Added controllers and permission checks for deterministic modification. Prevents participants from joining multiple teams simultaneously.

- [#1411](https://github.com/fossunited/fossunited/pull/1411) **Permission Decorator**
  Introduced decorator utility to wrap functions with permission checks for chapter members and hackathon team participants so we can reuse it for many API endpoints.

- [#1407](https://github.com/fossunited/fossunited/pull/1407) **Localhost Sponsors**
  Added event sponsors table to localhost hackathons for better sponsor management.

- [#1406](https://github.com/fossunited/fossunited/pull/1406) **Localhost Description Field**
  Added description field to localhost hackathons for additional information.

- [#1438](https://github.com/fossunited/fossunited/pull/1438) **Hackathon Button Loading State**
  Disabled buttons during API fetch to enable single request per click and prevent duplicate operations.

- Fixed team join errors due to recent permission updates.
- Localhost pages now use event sponsors for sponsor display.
- Project issue/PR can now be added via frappe-ui documentResource.
- Localhost now properly sets image background and text colors.
- Registration rate limiting added to prevent spam.
- Fixed hackathon test suite to allow registrations properly.

#### Jobs & Grants

- [#1396](https://github.com/fossunited/fossunited/pull/1396) **Job Board Publish Date**
  Added `publish_date` field to job board for better tracking and scheduler handling. Jobs now use publish date consistently across pages.

- Jobs now show publish date information on listing pages.
- Auto-email notifications sent to team when jobs are posted.

#### Code Quality & CI

- [#1423](https://github.com/fossunited/fossunited/pull/1423) **Frappe Semgrep & PR Linter**
  Added Frappe semgrep rules and conventional commit linter checks to CI pipeline for better code quality and consistency.

    Credits: Harsh Tandiya for informing for best practice

#### UI/UX Polish

- [#1408](https://github.com/fossunited/fossunited/pull/1408) **Common Functions Bundle**
  Removed redundant `common_functions.js` includes as it's already bundled in `website.bundle.js` after redesign.

- SearchListView improvements:
  - Set pixel width for columns for uniform display
  - Added text truncation and wrapping for long content
  - Reduced horizontal scrolling
  - Applied consistent styling across ticket insights, project issues, attendee lists

- Breadcrumb macro now:
  - Controls ignoring items from auto-generation
  - Builds dynamic breadcrumbs from macro for localhost pages
  - Uses proper v3 theme colors

- Theme toggle only initializes if present on page to avoid console errors.
- Sponsor tier headings now use v3 text colors.
- Fixed z-index for sponsor card edit buttons.
- Applied v3 select and control themes from grants pages.
- Icon improvements: using `report-search` icon for list search.

#### Templates & Macros

- Render field macro now supports required field indicators.
- Web templates now properly include `custom.css` (fixed Firefox/Chromium compatibility).
- Removed redundant `custom.css` and `common_functions.js` includes from HTML templates.

#### Backend Improvements

- Permission checks ensure only chapter members or localhost organizers can send emails.
- Improved API calls with direct function calls for permission checks.
- Better decorator-based permission validation.
- Direct status filtering for events instead of complex queries.

#### Dependency Updates

- ESLint: 9.39.2 → 10.0.1
- @eslint/js: 9.39.2 → 10.0.1
- eslint-plugin-vue: 10.7.0 → 10.8.0
- globals: 17.1.0 → 17.3.0
- markdown-it: 14.1.0 → 14.1.1
- cryptography: 46.0.3 → 46.0.5

    Planning to bump other dependency manually via [#1437](https://github.com/fossunited/fossunited/issues/1437)

---

### New Contributor Spotlight

- [@ni5arga](https://github.com/ni5arga) (Nisarga Adhikary) made significant security contributions:
  - [#1398](https://github.com/fossunited/fossunited/pull/1398): Rate limiting & ticket transfer validation fixes
  - [#1401](https://github.com/fossunited/fossunited/pull/1401): Team member validation in project creation
  Credits also to [@kewonit](https://github.com/kewonit) (Kartik Kulloli) for security research

---

## January 2026

| Metric        | Count |
|---------------|-------|
| Issues Closed | 14    |
| PRs merged    | 42    |

Hey everyone,

January kicked off with significant improvements focused on **FOSS Hack 2026** preparation, **Events Timeline redesign** (much needed), and **Grants page overhaul**. We've also enhanced the dashboard with better **localhost management**.

---

### PR Highlights

#### Events Timeline Redesign

- [#1375](https://github.com/fossunited/fossunited/pull/1375) **Events Timeline Redesign**
  Complete redesign of the events timeline page with v3.0 design language.
  Visit: [Events Timeline](https://fossunited.org/events/timeline)

- [#1383](https://github.com/fossunited/fossunited/pull/1383) **Split Timeline into Upcoming & Completed**
  Timeline page now splits events into two clear sections - Upcoming and Completed events. Some filters are shown only for completed events.

- [#1380](https://github.com/fossunited/fossunited/pull/1380) **RSS Feed for Events Timeline**
  Added RSS feed support for upcoming events on the timeline page for easy subscription and tracking.
  Feed: [Events Timeline RSS](https://fossunited.org/events/timeline/rss.xml)
  More [to be added](https://github.com/fossunited/fossunited/issues/1357) for other pages.

- Lazy loading implemented for event banner images to improve page load performance.

#### Grants Page

- [#1347](https://github.com/fossunited/fossunited/pull/1347) **Grants Landing Page Redesign**
  Complete redesign of the main grants page with updated content and v3 styling.
  Visit: [Grants](https://fossunited.org/grants)

- [#1348](https://github.com/fossunited/fossunited/pull/1348) **Individual Grants Details Page**
  New dedicated page for each grant type (Project Grants & Event Grants) with detailed information and filters.

- [#1349](https://github.com/fossunited/fossunited/pull/1349) **Grants Directory Redesign**
  Redesigned grants directory page for better discoverability and filtering via project tags.

- [#1350](https://github.com/fossunited/fossunited/pull/1350) **Improved Grant Directory Listing**
  Enhanced listing page with better sorting and categorization via pagination of 50 items per page.

- [#1356](https://github.com/fossunited/fossunited/pull/1356) **Grantees Page**
  New page showing all grant recipients across different grant types indicating total amount disbursed.
  Visit: [Grantees](https://fossunited.org/grantees)

- [#1379](https://github.com/fossunited/fossunited/pull/1379) **Event Grant Doctype Updates**
  Added new fields (`event_description`, status options like "Ongoing" and "Disbursed") to Event Grant doctype for better tracking via web forms.

- [#1387](https://github.com/fossunited/fossunited/pull/1387) **Event Grant Amount Migration**
  Migrated grant amount field from Data to Currency type for proper formatting and calculations.

#### Hackathon & Localhost Management

- [#1345](https://github.com/fossunited/fossunited/pull/1345) **Hackathon Participant Counts**
  Added team and participant count display on hackathon index pages.

- [#1358](https://github.com/fossunited/fossunited/pull/1358) **Hackathon Dashboard Layout Fix**
  Fixed layout issues in hackathon dashboard pages for better UX.

- [#1360](https://github.com/fossunited/fossunited/pull/1360) **Localhost Attendees with SearchListView**
  Hackathon localhost attendee acceptance now uses SearchListView component with team-based grouping for better organisation.

- [#1361](https://github.com/fossunited/fossunited/pull/1361) **Edit Localhost Page**
  Added dedicated page to edit localhost hackathon data with proper validation ensuring only organisers can access.

- [#1365](https://github.com/fossunited/fossunited/pull/1365) **Localhost Layout as Parent**
  Localhost hackathon pages now use consistent parent layout for better navigation.

- [#1366](https://github.com/fossunited/fossunited/pull/1366) **Localhost Email Group Integration**
  Accepted hackathon participants are automatically added to localhost email groups for communications.

- [#1368](https://github.com/fossunited/fossunited/pull/1368), [#1369](https://github.com/fossunited/fossunited/pull/1369) **Common Mailing Component**
  Refactored mailing functionality into reusable component. Added mailing feature for localhost hackathons.

- [commit 4c0698163efa228cc4a568e2b6a5146fbfc47034](4c0698163efa228cc4a568e2b6a5146fbfc47034): Redesigned hackathon project page in v3 style.

#### Event Check-ins & RSVP Improvements

- [#1359](https://github.com/fossunited/fossunited/pull/1359) **RSVP Insights Error Messages & Docs**
  Added error message display and documentation info component to help organisers troubleshoot issues.

- [#1374](https://github.com/fossunited/fossunited/pull/1374) **Waiting List Info**
  Events page now shows waiting list information. Attending counts only show accepted RSVPs.

- [#1392](https://github.com/fossunited/fossunited/pull/1392) **Ticket Check-ins SearchListView**
  Ticket check-in dashboard now uses SearchListView for faster searching and better performance.

- [#1393](https://github.com/fossunited/fossunited/pull/1393) **Ticket Check-in Insights by Event Days**
  Ticket check-in insights now show data grouped by event days, similar to RSVP check-ins.

- [commit 8a9a74](8a9a7424c711c7fba7f2e47d78be46e53e778b5c): RSVP page now shows "RSVP Closed" message if form is unpublished and removed RSVP button to avoid 404 page.
- Added docs link to event RSVP pages for user guidance.
- Schedule page now defaults to current day's date for better UX.

#### Event Management

- [#1342](https://github.com/fossunited/fossunited/pull/1342) **Edit Event Button for Concluded Events**
  Added "Edit Event" button visible to organisers even for concluded events. Uses proper permission checks via `check_if_chapter_or_event_core_member`.
  Credits: [@Pranav1921](https://github.com/Pranav1921)

- [#1382](https://github.com/fossunited/fossunited/pull/1382) **Event Publishing Toggle**
  Dashboard now has toggle button to publish/unpublish events directly from event details page.
  This has been added akin to [#1364](https://github.com/fossunited/fossunited/issues/1364) to allow deleting event.

- [#1354](https://github.com/fossunited/fossunited/pull/1354) **Sponsor Sorting Enhancement**
  Event sponsors now sorted with Industry Partners (patrons) appearing first, then by date of confirmation within each tier, or alphabetically.

- MyChapters component now ignores events without end dates to prevent display issues.
- MyChapters now uses API function to show events for better data consistency.

#### Dashboard UI Components

- [#1370](https://github.com/fossunited/fossunited/pull/1370) **Common Save Action Bar**
  Multiple dashboard pages now use unified sticky save action bar at bottom for consistent UX across:
  - Event details editing
  - Chapter details
  - RSVP forms
  - Hackathon configuration

- SearchListView component enhancements:
  - Added support for preferred export columns for CSV download.
  - Used across ticket insights, free coupons, RSVP insights, and check-ins.
  - Improved performance and code reusability.

#### Payment & Tickets

- Razorpay payment capture now includes event name and ID in description for easier filtering in razorpay dashboard.

#### User Profiles

- **OpenGraph Support for FOSS Profiles**
  Added meta_block for user profiles to generate OG images for better social media sharing.

#### Templates & Macros

- [#1362](https://github.com/fossunited/fossunited/pull/1362) **Common V3 Navbar & Theme Toggle**
  Introduced reusable `v3_navbar` macro with theme toggle for consistent navigation across redesigned pages.
  - Breadcrumb macro now builds crumbs automatically if not passed (useful for simplified paths)
  - Applied across grants, events, volunteers, and other v3 pages

#### Documentation

- Added [FOSS Hackathon information](https://docs.fossunited.org/fosshack/) to docs.
- Updated docs with event check-in system information for RSVP insights dashboard.
- Added screenshots for check-in insights workflow.
- Dashboard pages now include DocsInfo component with help links.

#### Performance

- Lazy loading implemented for event timeline banner images.
- Event cards now use lazy loading for better initial page load.
- Reduced unnecessary API calls via refactored functions.

---

### New Contributor Spotlight

- [@Pranav1921](https://github.com/Pranav1921) made their first contribution:
  - [#1342](https://github.com/fossunited/fossunited/pull/1342): Added edit event button for concluded events with proper permission checks

---

## December 2025

| Metric        | Count |
|---------------|-------|
| Issues Closed | 10    |
| PRs merged    | 37    |

Hi everyone,

December was a quieter but productive month as we wrapped up the year amidst holidays and year-end slowdowns. This month focus has been early groundwork for upcoming **FOSS Hack 2026**, ensuring the platform enters the New Year in a more stable and maintainable state.

---

### PR Highlights

#### New Page & Announcement

- [#1337](https://github.com/fossunited/fossunited/pull/1337) **FOSS Hack 2026 page**
  Introduced the initial FOSS Hack 2026 landing page directly in the codebase.
  - Designed to be fully open for community contributions
  Visit: https://fossunited.org/fosshack/2026

#### Tickets

- [#1300](https://github.com/fossunited/fossunited/pull/1300) Redirect /tickets to buy-ticket page or RSVP page.
  In fossunited platform typical event page link is in the format of `https://fossunited.org/chapter/event`
  - Now, `https://fossunited.org/chapter/event/tickets` -> redirects to buy-ticket page if its an paid event or else send you to rsvp page. /rsvp, /cfp and /schedule works over the permalink.

- [#1301](https://github.com/fossunited/fossunited/pull/1301) Apply custom field to each attendee in buying ticket
  Previously we had custom field applied to all attendees ticket, but these custom field data can act as survey to collect preferred choice. Given a switch toggle this can apply to all or each ticket.

<!-- - [#1307](https://github.com/fossunited/fossunited/pull/1307) Grab your tickets page -->
<!--   A dedicated page to download tickets for an event. Input by ticket ID or email. Coupon ID (organisation) can also be provided to download all tickets claimed from it in single PDF. -->
<!--   Refer: https://fossunited.org/get-tickets -->

- [#1310](https://github.com/fossunited/fossunited/pull/1310) Ticket insights with Custom fields
  Ticket insights in dashboard will now also show custom fields data. Now ListView is grouped based on tier and whole data can be downloaded as CSV.

- [#1319](https://github.com/fossunited/fossunited/pull/1319) Searchable ticket insights list
  Ticket insights dashboard now uses the shared searchable ListView component.
  - Faster filtering for large events
  - Cleaner UI and reduced redundant code

- API refactor simplified ticket insight data retrieval using query builder for better maintainability.
  refer: https://frappe.io/blog/engineering/evolving-frappes-orm-for-security-and-flexibility

#### Events

- Added missing projects showcase and community partner cards just like sponsor cards.
- [#1304](https://github.com/fossunited/fossunited/pull/1304) Hide markdown format comments in description
  Using `<!-- Some text -->` will now be hidden via CSS rule in event description.
  Note: It still might appear in page SEO (meta).

- [#1304](https://github.com/fossunited/fossunited/pull/1304) Show OSM preview for event map link
  Show map preview for the `map_link` provided. Works with gmaps (maps.app.goo.gl) and OSM links.
  We use [Leaflet via CDN](https://leafletjs.com/) to show the preview image.

- [#1321](https://github.com/fossunited/fossunited/pull/1321) Event map preview improvements
  Introduced `map_coordinate` field for events.
  - Cleaner handling of empty or invalid map links
  - Enables consistent preview rendering without repeated parsing

#### RSVP

- [#1302](https://github.com/fossunited/fossunited/pull/1302) Refactor getting RSVP data
  Was kinda over-complicated before, now made simplified to just work as intended.

#### RSVP Insights

- [#1327](https://github.com/fossunited/fossunited/pull/1327) Simplified RSVP insights API
  Refactored RSVP insights backend to use a flat, deterministic data structure.

- [#1328](https://github.com/fossunited/fossunited/pull/1328) Searchable RSVP insights with CSV export
  Reused the generic `searchListView` component to:
  - Client-side search RSVP responses
  - Export filtered data directly as CSV

- [#1343](https://github.com/fossunited/fossunited/pull/1343) Event check-in via attendee list view
  Organisers can now **manually check-in attendees** directly from the RSVP insights dashboard.
  - Useful for bulk or assisted check-ins
  - Complements self check-in flow without backend changes
  - Includes undo option for same-day check-ins

#### CFP & Reviews

- [#1309](https://github.com/fossunited/fossunited/pull/1309) Notify Chapter members if an approved proposal has been withdrawn
  A nudge email is sent to notify if only an approved proposal was withdrawn by the proposers.
  Note: Email is only sent to chapter members, proposer is not involved.

- [#1312](https://github.com/fossunited/fossunited/pull/1312) Proposal review notifications
  Introduced email notifications when a proposal receives a **new review or updated remarks**.
  - Notifies proposers and CCs speaker emails
  Credits: Aryak for previous work (#982)

- [#1339](https://github.com/fossunited/fossunited/pull/1339) Increase reference link length for CFP submissions
  Long reference links (Google Docs, slides, blogs) are now fully supported.
  - Increased limit to 250 characters

- Desk improvement: CFP submissions without session categories can now be edited via desk UI

#### Grants

- [#1344](https://github.com/fossunited/fossunited/pull/1344) Optimised Grants Directory manifest updates
  Reduced server load by updating grant manifests only when changes are detected.
  - Removed scheduler dependency
  - Uses lightweight triggers on page visit
  - Clear distinction between `last_updated` and actual manifest changes

- [#1340](https://github.com/fossunited/fossunited/pull/1340) Complete redesign of Suite of Grants pages
  - New Grants page design with more structural and uniform design

#### Performance & UI Components

- Searchable ListView optimisations:
  - Added debounced search
  - Cached rows using `WeakMap` for faster filtering on large datasets (>2000 rows)

- Multi-select component now handles empty data gracefully and improves required-field error visibility.

#### Accessibility

- [#1308](https://github.com/fossunited/fossunited/pull/1308): Improved keyboard navigation and ARIA labelling across:
  - Proposal lists
  - Dashboard sidebar navigation
  - My Proposals page
  Credits: @grittyuffy (Keerthana)

- [#1306](https://github.com/fossunited/fossunited/pull/1306): Added missing `alt` text to images across dashboard and main site, improving screen reader support.
  Credits: @ig-imanish (Manish Kumar)


### New Contributor Spotlight

- [@RuchikaByte](https://github.com/RuchikaByte) made their first contribution:
  - [#1275](https://github.com/fossunited/fossunited/pull/1275): docs: add information on event mailing functionality

- [@grittypuffy](https://github.com/grittypuffy) made their first contribution:
  - [#1308](https://github.com/fossunited/fossunited/pull/1308): a11y: Improve keyboard navigation for proposals in dashboard and sidebar navigation
  - Continued accessibility improvements across dashboard and proposal flows.

- [@Praneel7015](https://github.com/Praneel7015)
  - [#1314](https://github.com/fossunited/fossunited/pull/1314): Added speaker support and online event options for chapter events

- [@ig-imanish](https://github.com/ig-imanish) made their first contribution:
  - [#1306](https://github.com/fossunited/fossunited/pull/1306): Improve accessibility: Add missing alt text to all images across dashboard and main site

## November 2025

| Metric        | Count |
|---------------|-------|
| Issues Closed | 19    |
| PRs merged    | 40    |

Hi everyone,

November brought some major additions to the platform! We've introduced a **Grants Funding Directory** inspired by floss.fund, implemented **RSVP Check-ins** for better event management, and launched **Host Approval workflow** for RSVPs. The new **Events Page redesign** with v3.0 design is now live, alongside the [**First Commit**](https://fossunited.org/first-commit) initiative page. We've also added comprehensive **Free Ticket management** for organisers.

---

### PR Highlights

#### Events Page Redesign & First Commit

- [#1265](https://github.com/fossunited/fossunited/pull/1265) **Events Page Redesign**
  Complete redesign of events page with v3.0 design language, dark mode support, and better visual hierarchy. Features improved event cards, sponsor display, speaker sections, and social links.
  Note: From now on event banner will be in aspect ratio of 1:1 only. Suggested resolution is 280×280px

Eg: https://fossunited.org/c/mumbai/minidebconf2025

- [#1271](https://github.com/fossunited/fossunited/pull/1271) **First Commit Page**
  Added dedicated page for First Commit initiative.
  https://fossunited.org/first-commit

Credits: [@jeswinjosu](https://github.com/jeswinjosu)

#### Grants Funding Directory

- [#1283](https://github.com/fossunited/fossunited/pull/1283) **Grants Funding Directory**
  Introduced funding directory inspired by floss.fund using `funding.json` manifest schema. Projects can submit their funding information via JSON schema validation.
  [Explore Grants Directory](https://fossunited.org/grants/directory)

- [#1284](https://github.com/fossunited/fossunited/pull/1284) **Grants JSON Schema Validation**
  Added unit tests to ensure robust validation of funding.json against the schema using `floss.fund/api/validate` endpoint.

- [#1294](https://github.com/fossunited/fossunited/pull/1294) **Grants Thesis Page**
  Added grants thesis template page with v3 design for detailed project information.

#### RSVP Self Check-in System

- [#1286](https://github.com/fossunited/fossunited/pull/1286) **RSVP Check-in doctype**
  Added check-in table to RSVP submissions allowing attendees to check-in during event timeline.

- [#1287](https://github.com/fossunited/fossunited/pull/1287) **Self Check-in Frontend**
  Attendees can now check-in via their RSVP edit page during event hours. Shows "Checked for today" status after check-in. Includes automatic handling of custom questions added after initial RSVP.
  [Documentation](https://docs.fossunited.org/attend-event/)

- [#1288](https://github.com/fossunited/fossunited/pull/1288) **Check-in Insights Dashboard**
  Event organisers can view check-in data grouped by dates in a dedicated insights page with download functionality.

#### RSVP Host Approval

- [#1282](https://github.com/fossunited/fossunited/pull/1282) **Host Approval Workflow**
  Added host-requires-approval feature for RSVP forms. Organisers can approve or reject RSVPs directly from insights page with email notifications. Includes confirmation dialog for rejections.
  Related issue: [#676](https://github.com/fossunited/fossunited/issues/676)

#### Free Ticket Management

- [#1259](https://github.com/fossunited/fossunited/pull/1259) **Free Ticket doctype**
  Imported free ticket code and application doctype from desk into codebase. Includes validation, count tracking, and server-side checks for coupon redemption. Added comprehensive unit tests.

- [#1260](https://github.com/fossunited/fossunited/pull/1260) **Free Ticket Dashboard**
  Event organisers can now manage free ticket codes directly from dashboard. Create, edit, delete, and view coupon IDs for distribution to organisations.

- [#1261](https://github.com/fossunited/fossunited/pull/1261) **Permission Controls**
  Only chapter team members can modify their event's free ticket codes, preventing cross-injection attacks.

- [#1262](https://github.com/fossunited/fossunited/pull/1262) **Auto-set Event**
  Free ticket form now automatically sets event based on coupon code, making it generic for all events.

- [#1258](https://github.com/fossunited/fossunited/pull/1258) **Free Pass Insights**
  Ticket insights now show free pass holders in attendee list and counts.

- [#1257](https://github.com/fossunited/fossunited/pull/1257) **Ticket Transparency**
  Buy ticket page now shows disabled and expired tickets for transparency. Added proper validity checks for date and count.
  Closes: [#1183](https://github.com/fossunited/fossunited/issues/1183)

#### CFP & Schedule Enhancements

- [#1268](https://github.com/fossunited/fossunited/pull/1268) **Talk Licensing**
  Added license field to CFP submissions with acknowledgment checkbox. Proposers can specify talk licenses upfront.

- [#1266](https://github.com/fossunited/fossunited/pull/1266) **Talk Video Links**
  Added `talk_video` field to link recorded talks in schedule and CFP pages. Shows video links for past sessions and "Add to calendar" only for upcoming sessions. This video link will be shown in schedule page as well as in CFP linked page.

- [#1270](https://github.com/fossunited/fossunited/pull/1270) **CSV Download for Proposals**
  Reviewers and organisers can now download all proposals in CSV format for analysis. Includes custom answers if marked public.
  [#1274](https://github.com/fossunited/fossunited/pull/1274) Moved CSV generation to frontend to reduce backend load, properly escaping content to avoid CSV injection.

- [#1269](https://github.com/fossunited/fossunited/pull/1269) **Schedule Management Filters**
  Enhanced event schedule modification page with better filtering options to reduce cognitive load (especially useful for large events like IndiaFOSS).

#### UI/UX Improvements

- [#1281](https://github.com/fossunited/fossunited/pull/1281) **Web Accessibility**
  Improved accessibility with proper ARIA labels for events page and render fields. Replaced div with nav for breadcrumb items.
  Partially addresses: [#788](https://github.com/fossunited/fossunited/issues/788)

- [#1293](https://github.com/fossunited/fossunited/pull/1293) **Mobile Responsiveness**
  Adjusted mobile adaptiveness for grants directory, RSVP insights, drawer components, and comment box icons.

- [#1292](https://github.com/fossunited/fossunited/pull/1292) **Events Grid CSS**
  Fixed events card grid to display uniformly without breaking.
  Thanks to Nihal for reporting in telegram.

- [#1280](https://github.com/fossunited/fossunited/pull/1280) **Comment Review Retention**
  Review comments are now retained locally even after page reload using localStorage.
  Closes: [#968](https://github.com/fossunited/fossunited/issues/968)

- [#1276](https://github.com/fossunited/fossunited/pull/1276) **Email Drawer UX**
  Fixed opacity issues and improved UX for email dialog and scheduling components.

- [#1273](https://github.com/fossunited/fossunited/pull/1273) **Text Wrapping**
  Fixed word-wrap for long links and text content. Added livestream link to event about section.

- [#1272](https://github.com/fossunited/fossunited/pull/1272) **V3 CSS Standardization**
  Applied v3 design CSS across multiple pages. Updated event banner to 1:1 aspect ratio (280×280px).

- [#1263](https://github.com/fossunited/fossunited/pull/1263) **Profile Activity Placement**
  Moved profile activity card below "about" section for better prominence. Hid work tab temporarily.

#### Documentation

- [#1289](https://github.com/fossunited/fossunited/pull/1289) **RSVP & Event Docs**
  Added comprehensive documentation for RSVP check-ins, event schedule, and related features with screenshots.

#### Refund Policy

- [#935](https://github.com/fossunited/fossunited/pull/935) **Refund Policy Acceptance**
  Users must now accept refund policy before purchasing tickets.
  Closes: [#898](https://github.com/fossunited/fossunited/issues/898)

#### User Profile

- [#1278](https://github.com/fossunited/fossunited/issues/1278) Temporarily hid the **Projects**, **Education**, and **Resume** tabs on user profiles until we redesigned profile page. For now, only the **About** and **Activity** sections will be shown.

---

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
  Users can now toggle RSVP/Un-RSVP directly with updated UI states to let Organiser know that they are "not attending".
- [#1214](https://github.com/fossunited/fossunited/pull/1214) RSVP insights grouping
  Dashboard enhancements now group RSVP data by attendance, improving analytics for event organisers. Shows two groups "Attending" and "Not attending" (not shown by default)

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
  Announcement: [Meet the first-ever elected community governance board](https://fossunited.org/blog/organisation/meet-the-first-ever-elected-community-governance-board-foss-united)

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
