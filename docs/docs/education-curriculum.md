# Digital Commons: Course Guide

This is a ready-to-adapt structure for a 2-credit elective or embedded module. It is designed to be discipline-agnostic and can run with mixed engineering cohorts. We recommend adapting the readings and tools to your branch and publishing the resulting course materials under [Creative Commons Attribution](https://creativecommons.org/licenses/by/4.0/deed.en).

This framework is inspired by established initiatives like open@RIT, the HFOSS program, Hunter College’s Open Source course, and Dickinson College’s FOSS-integrated curriculum. Specific practices adapted from these institutions are cited throughout the guide.

### On contact hours

A 2-credit course under AICTE norms requires approximately 30 contact hours across a semester (2 hours per week for 15 weeks). The structure below is a full 15-week, 2-credit course. If you want to run a 1-credit version, use only Phase 1 (Weeks 1 to 8).

### How to run this without a FOSS background

Faculty who are not FOSS practitioners can run this course effectively by doing three things.

First, be honest with students that you are learning alongside them. This is itself a demonstration of open collaboration, and students consistently respond better to it than to false expertise.

Second, rely on the readings and community resources rather than lectures. The Fogel book, the contributing guides, and real project documentation are better teaching material than slides. Your job is to facilitate the contribution process, not to lecture about it.

Third, bring in one or two guest speakers from the FOSS community. FOSS United can connect you with practitioners who have spoken at engineering colleges before. Contact foundation@fossunited.org with a date and we will help find someone.

The most important thing the faculty coordinator does in this course is review. Approving or declining contributions before they go upstream, reading learning logs regularly, and having honest conversations about what is and is not working: these are what make the difference between students who make one token contribution and students who come away with a genuine understanding of how open collaboration works.

## Overview

**Course title:** Introduction to Free Software and Digital Commons
**Credits:** 2
**Contact hours:** 30 (2 hours per week for 15 weeks)
**Target students:** All engineering branches, years 2 to 4
**Prerequisites:** None
**Mode:** Weekly 2-hour sessions

#### **Learning outcomes**
By the end of this course, students will be able to:
- Explain what free and open source software is and how it differs from proprietary software
- Use Git and version control workflows to contribute to a shared project
- Identify appropriate open licences for software and content
- Evaluate the health and contributor-friendliness of an open source project before joining it
- Describe the digital commons with real examples from India and globally
- Write publicly about open source for an external audience
- Engage with open source communities online and in person
- Make at least one verifiable, pre-approved contribution to a public open source project or digital commons resource.

### Contribution policy

Before a student begins working on any external project, the faculty coordinator approves the project and the scope of the intended contribution. This is a one-time conversation per student per semester, not a gate on every commit.

The approval conversation happens in Week 8 when students submit their contribution plan. The faculty coordinator reads the plan and either approves it or asks the student to revise it. The question being asked is not "is this contribution technically correct?" It is: "is this contribution substantial enough to be worth a maintainer's time, and is this student capable of completing it?"

>*Example: A student who proposes to add their college to a list of institutions using a FOSS tool should instead write a case study documenting how the tool is used at their college, what problems were encountered during setup, and how they were solved, and submit it as a contribution to the project's documentation.*

This policy is not about quality control on individual commits. Students who have an approved project and scope are responsible for the quality of their own work from that point forward. The faculty coordinator's job in Phase 2 is to support and advise, not to review drafts before they are sent.

The anti AI-slop principle still applies across all written work in the course: learning logs, written assignments, case studies, blog posts, and the final presentation. These are assessed on evidence of genuine thinking and personal engagement with difficult material. If a learning log shows no struggle with a task that should have been hard, that is worth a conversation.

### Pre-approved project list

Before the course begins, the faculty coordinator identifies 4 to 6 FOSS projects suitable for student contributions. This practice comes from the [HFOSS program](hfoss.readthedocs.io), which found that students who choose from a faculty-vetted shortlist spend their time contributing rather than searching for a viable project.

A suitable project has: an active maintainer who responds to issues within a week or two, a labelled list of beginner-friendly issues ("good first issue" or similar), public documentation good enough for a newcomer to understand the codebase, and a community that is welcoming of student contributors.

> **FOSS United can help**: We can help you identify appropriate Indian FOSS projects for this list. Check out [forklore](https://forklore.in).


### Phase 1: Foundations (Weeks 1 to 8)

**Week 1: What is free software and why does it matter?**

Cover the history and philosophy of the free software and open source movements: Richard Stallman's four freedoms, the GNU project, the Linux kernel, the OSI definition. Distinguish between free software and freeware. Discuss why the distinction between "open source" (a development methodology) and "free software" (a political position) exists and why it matters in practice.

***Activity:*** Students list five pieces of software they use daily and research whether each is open source, proprietary, or freeware. Write a 300-word entry in their learning log explaining what surprised them about the results.

***Reading:*** Excerpt from "Free Software, Free Society" by Richard Stallman, available at gnu.org. Short history of Linux at kernel.org.

**Week 2: How open source actually works**

Cover the governance structures of open source projects: maintainers, contributors, code review, issue trackers, release processes. Introduce the concept of a contributor community. Compare a solo developer project, a foundation-governed project (Apache, Linux Foundation), and a community-governed project (Debian). Introduce CHAOSS (Community Health Analytics for Open Source Software), a project under the Linux Foundation that defines metrics for evaluating whether an open source project is healthy enough to be worth contributing to. This is a practical tool students will use when selecting their project in Phase 2.

***Activity:*** Students pick one active open source project from the faculty's pre-approved list, read its CONTRIBUTING.md file, browse its issue tracker for at least 20 minutes, and write a 500-word structured analysis covering: how decisions are made, what kinds of contributions are welcomed, what the barrier to entry looks like, what a first-time contributor would need to know before opening an issue, and whether the project appears healthy by CHAOSS criteria (response time, contributor diversity, recent commits, issue resolution rate).

***Reading:*** Karl Fogel, "Producing Open Source Software" (producingoss.com, Chapters 1 and 2, free online). CHAOSS metrics overview at chaoss.community.

**Week 3: Git, documentation, and working in the open**

Practical session. Every student sets up Git and creates an account on a public code hosting platform. Codeberg (codeberg.org) is a non-profit platform running Forgejo, a free software forge, and is the recommended choice if students are starting fresh. GitLab Community Edition and Gitea can be self-hosted by the institution, which keeps the infrastructure under institutional control. GitHub is widely used across the open source world and is a reasonable choice, particularly when a student's chosen project is hosted there. The platform matters less than getting comfortable with the workflow: commits, branches, pull requests, and code review. Cover these in the session.

*First Flight exercise (adapted from RIT's HFOSS program):* The First Flight has two tasks completed in the same session. They test different things.

**Before Week 3, the faculty coordinator sets up a public course repository** containing a `students/` directory with one Markdown file per student. Each file follows a fixed template. This is the target for Task 1.

**Task 1: The class repository (approximately 30 minutes)**

This task tests that you can navigate the Git workflow from start to finish without getting stuck. The contribution is trivial by design. The process is the point.

1. Fork the course repository.
2. Clone your fork locally: `git clone <your-fork-url>`
3. Create a new branch: `git checkout -b add-[your-name]`
4. Create a file in the `students/` directory named `[branch]-[rollno].md`. Follow the template exactly: your name, your engineering branch, one piece of software you use daily that you discovered is open source in Week 1, and a link to your learning log.
5. Commit the file with a clear message: `git commit -m "Add [your name] to student roster"`
6. Push your branch and open a pull request. The PR description must answer: what is the licence of one tool you use daily, and what does that licence allow someone else to do with the code?

The faculty coordinator reviews all pull requests in class. Common problems (merge conflicts, wrong file names, missing fields) are shown to the group in real time.

***Activity:*** Practice Git and common scenarios and conflicts using free hands-on resources such as [Learn Git Branching](https://learngitbranching.js.org/).

***Reading:*** Scott Chacon and Ben Straub, "Pro Git" (git-scm.com/book, free online, CC BY-NC-SA licensed). Official Git documentation at git-scm.com/docs.

**Week 4: Licences, rights, and the legal layer**

Cover the main open source licences: MIT, Apache 2.0, GPL (v2 and v3), AGPL. Explain copyleft versus permissive licences. Introduce the "viral" property of copyleft: if you distribute code that incorporates a GPL library, the whole distribution must go under the GPL. Introduce Creative Commons for content and explain why a code licence should not be used for documentation and vice versa. Cover AGPL specifically, because many students will encounter it: AGPL closes the "cloud loophole" in GPL by requiring source disclosure even when the software is accessed over a network rather than distributed.

***Activity 1: Rapid-fire compatibility scenarios (15 minutes, class discussion)***

The faculty coordinator reads each question aloud. Students answer with a show of hands, then justify. The point is not to get the right answer immediately; it is to surface assumptions and misconceptions before anyone has committed to a contribution decision in the real world.

1. You want to include an MIT-licensed library inside a GPL-3 project and distribute the combined work. Is that legal?
2. You take GPL-2 code written by someone else and redistribute it under the MIT licence. Is that legal?
3. Your startup uses an AGPL-licensed database entirely internally. No external users, no distribution. Do you have any obligations?
4. The Kerala government puts LibreOffice (MPL-2.0), VLC (GPL-2.0 "or later"), and Python (PSF Licence) on a single USB drive distributed to 14,000 schools. Do they owe anyone money? Do they have any obligations?
5. You contribute code to an Apache-licensed project. Six months later, the maintainer relicenses the whole project to SSPL. Does your contribution change licence?
6. You release a library under MIT. A company builds a proprietary product with it and sells it without mentioning your name anywhere. Have they violated the licence?
7. A researcher uses a CC BY-NC licensed dataset to train a machine learning model. The model is integrated into a commercial product. Legal?
8. Your college publishes final year project reports on its website with "All rights reserved." A student at another college wants to cite and build directly on your methodology. What are their options?

Questions 4 and 8 are worth spending extra time on. Question 4 is a real scenario from Kerala KITE and the answer reveals how licence compatibility actually works in distribution. Question 8 surfaces the institutional knowledge commons problem described in Pillar III of this guide.

***Activity 2: The relicensing debate (20 minutes)***

Several open source projects have switched to more restrictive licences or gone fully closed source, often citing competitive or financial pressures. MongoDB, HashiCorp, Redis, and most recently cal.com (which moved its commercial edition to a closed repository in 2026, citing AI and security risks) are recent examples. In each case, a community that had built on these projects found the ground shifting under them.

***Written work*** Each student picks one of these cases, researches it independently, and writes a 600 to 800-word essay arguing either that the company was justified in making the change, or that it was not. The essay must take a clear position and defend it. Students who argue both sides without committing to one will not receive full marks.

***Reading:*** SFLC.in's free software licensing primer. Creative Commons licence chooser at creativecommons.org. For context on the relicensing debate: the OSI's statement on SSPL at opensource.org.

**Week 5: The digital commons: Wikipedia, OpenStreetMap, open data, OER**

Broaden from software to the digital commons as a wider concept. Cover Wikipedia's governance model. Introduce OpenStreetMap and its significance as a community-built geographic commons. Cover open data (India's data.gov.in, Open Government Data platform) and open educational resources.

#### ***Mandatory Activities***

1. **OpenStreetMap:** Every student maps at least five features of the college campus on OpenStreetMap that are missing or incorrect: building entrances, labs, canteens, cycle stands, accessibility ramps. This is a real contribution to a global commons. The faculty coordinator pre-approves the edits before students submit them. Students document their additions with before-and-after screenshots in their learning log.

2. ***Wikipedia:*** Every student finds the Wikipedia article for their college and either creates it (if it does not exist) or substantially improves it with cited sources: founding year, notable alumni, research output, accreditations. The faculty coordinator reviews the draft before it goes live. Students who cannot find enough cited sources document that problem and explain what sources would need to exist for the article to be written.

***Written work:*** 500-word reflection comparing the experience of contributing to OpenStreetMap and Wikipedia. What did each community's norms and review processes feel like? What would you contribute next?

***Reading:*** Yochai Benkler, "The Wealth of Networks" (Chapter 3 excerpt, free online). Wikipedia's "Five Pillars." OpenStreetMap's Beginner's Guide at wiki.openstreetmap.org.

**Week 6: Open source in India: the landscape and the gaps**

Survey the Indian FOSS ecosystem: Frappe and ERPNext, Zerodha's open source stack, NPTEL, Kerala KITE, India's Digital Public Infrastructure (UPI, Aadhaar, ONDC). Discuss why India produces a disproportionately small number of open source contributors relative to its developer population and what structural factors contribute to this. Cover FOSS United's program: FOSS Hack, the Education Workgroup, the grants program for student-initiated open source projects, and Season of Commits, a program that runs focused contribution sprints to specific FOSS projects over defined periods.

***Activity:*** Students research one Indian FOSS project or organisation and prepare a written case study of 1,200 to 1,500 words covering: what problem it solves, how it is governed, how it is funded, what its contributor community looks like, and what a student could realistically contribute to it. Students present their case study to the class in a 15-minute session with five minutes for questions. Presentations are assessed by peers using a shared rubric agreed upon in Week 2.

***Guest speaker:*** Invite a maintainer of an Indian FOSS project. FOSS United can help identify someone. Ask them to speak specifically about what makes a contribution useful versus a burden.

***Reading:*** Zerodha's open source page at zerodha.com/open-source (covers FLOSS/fund, FOSS United co-founding, and their open source commitments). Zerodha's list of projects built in-house and open-sourced at zerodha.tech/projects/. The Zerodha engineering team's account of those projects at zerodha.com/z-connect/updates/open-source-projects-from-zerodha-tech-team. For the "contribution vs. maintainer" gap: GitHub Octoverse 2024 at github.blog/news-insights/octoverse/octoverse-2024/ (India section). For a critical reading on India's DPI and what "open" actually means in practice: indiastack.in/foss/ (pairs well with the Week 4 Activity 4 discussion and worth revisiting here).

**Week 7: Open source for social impact: public health, governance, and civic life**

Cover organisations that work entirely in the open and use free software to address public problems.
Example:
- **[OpenHealthcare Network](ohc.network)**: A network of developers and healthcare workers building open source clinical tools for India's public health system. All software is freely available and contributions are actively welcomed.
- **[CivicDataLab](https://civicdatalab.in/)**: They build open-source tools and data collaboratives (such as CivicDataSpace) to make public information machine-readable and actionable.

***Activity:*** Students identify one civic or social problem in their own college town or district and write a 1,000-word research note covering: what the problem is, whether an open source tool or organisation already addresses it, and if not, what the gap looks like. The note should be written in a way that could be shared with a civic organisation. Faculty coordinators review these before students share them externally.

**Week 8: Choosing your project and planning your contribution**

Students review the pre-approved project list, complete any remaining First Flight tasks, and choose the project they will contribute to in Phase 2. Where possible, students form teams of two or three working on the same project. Team-based contributions are encouraged because they reflect how open source projects actually work, and team contributions produce better outcomes than individual ones.

Each student or team submits a one-page contribution plan: what project they have chosen, why, what specific issue or area they plan to work on, what their first step is, and what challenges they expect to tackle. The faculty coordinator reads every plan and approves or redirects it. The standard is ambition and genuine usefulness, not always technical sophistication. A student proposing a minor edit to a widely-read page should be redirected toward something that requires sustained work. A student proposing to contribute to infrastructure, tooling, or documentation for a project used by thousands of people is making the right call even if they are nervous about it.

Once the plan is approved, the student owns the execution. The faculty coordinator's role in Phase 2 shifts from gatekeeper to advisor.

***Reading:*** Eric Raymond, "The Cathedral and the Bazaar" (catb.org, free online). This is best read now, after students have had direct experience with contributing, not at the start.

### Phase 2: Sustained contribution (Weeks 9 to 14)

Each Phase 2 session is two hours: one hour of structured check-in and one hour of working time. The faculty coordinator has systematic check-ins with individuals or with teams. The coordinator is also encouraged to look for industry professionals who can mentor students during Phase 2. The goal is to move from lectures to sustained, mentored contribution to a real project.

**Weeks 9 to 12:** Students make their first substantive contribution to their chosen project. This goes beyond the First Flight: it should address a real issue, add meaningful documentation, improve a feature, or fix a genuine bug. Each contribution requires faculty pre-approval before it is submitted upstream. Students update their learning log each week.

**Weeks 13:** Students deepen their engagement with their project community. They should be participating in discussion threads, responding to maintainer feedback, and if their first contribution was accepted, planning for a second one. Students write their first public blog post in Week 13 (see Assessment). Writing for an external audience is a different exercise from writing in a private log.

**Weeks 14:** Students prepare for their final presentation and work toward completing their second contribution. The faculty coordinator holds individual or team reviews to check the quality and documentation of contributions before the final session.

### Phase 3: Final presentations (Week 15)

Each student or team delivers a 30-minute presentation followed by five minutes of questions from faculty and peers. Before the session, students submit a two-page written reflection covering: what they contributed, what was rejected and why, what they learned about working in public, and one concrete thing they plan to do in the next three months.

**Optional**: The summer project pathway could open from here. Students who complete the elective and make at least one meaningful contribution are eligible to apply for a structured 8 to 10 week summer project contributing to a real open source project under the guidance of a maintainer.

> FOSS United can connect students with projects and maintainers. Details on the [FOSS United Forum](https://forum.fossunited.org/t/season-of-commits/2494).

### Assessment

Seven components across three groups, totalling 100%.

| Group | Components | Weight |
|-------|-----------|--------|
| Contributions and engagement | Contribution log, Community engagement, Weekly participation | 35% |
| Written work | Research and writing log, Case study, Public blog post | 45% |
| Presentation | Final 30-minute presentation | 20% |

---

### Contributions and engagement (35%)

**Contribution log (25%)**

A documented record of at least one substantive contribution across the semester, plus the First Flight completed in Week 3. Each entry must include a link to the contribution and a 150-word reflection written after submission. The project and scope were approved in Week 8; individual contributions after that are the student's responsibility.

Contributions rejected upstream are still assessed on quality of the attempt. A contribution rejected because the maintainer said "this is already handled in another issue" is worth full marks if the student can explain what they learned. A large pull request with poor documentation is worth less than a clear, well-scoped bug report.

**Community engagement (5%)**

Documented evidence of engaging with open source or digital commons communities outside class activities. This includes posting on FOSS forums or project discussion boards, attending a FOSS event, or volunteering with an open source organisation. Students submit a brief log with links at the end of semester. Quality of engagement matters more than volume.

**Weekly participation (5%)**

Attendance and active participation in in-class activities across all 15 weeks.

---

### Written work (45%)

**Research and writing log (20%)**

Weekly learning log entries of 250 to 300 words each, one per week for 14 weeks, kept in the class repository. Plus the three structured written assignments from Weeks 2, 3, and 7. Assessed on depth of thinking, honesty about difficulty, and ability to connect course topics to the student's own engineering context. The log is read fortnightly by the faculty coordinator, not only at the end of semester.

**Case study (15%)**

A 1,200 to 1,500-word written case study of one Indian FOSS project researched in Week 6, followed by a 15-minute class presentation assessed by peers using the shared rubric agreed in Week 2. Published under CC BY.

**Public blog post (10%)**

One blog post of 700 to 1,000 words, written in Week 12, about the student's contribution experience. Published publicly and licensed under CC BY. Assessed on clarity, honesty, and whether it would be useful to another student considering the same project. This practice comes from RIT's HFOSS course, where writing publicly about contributions is treated as a contribution in its own right.

---

### Final presentation (20%)

A 30-minute presentation delivered in Week 15, followed by five minutes of questions from faculty and peers. Students submit a two-page written reflection before the session.

The presentation should cover the full arc: what project was chosen and why, what was attempted, what was rejected and why, what was difficult, and what the student plans to do next. The 30-minute length is deliberate. Presentations that pad time rather than reflect honestly on the process will show in the assessment.

---

> **On grading contributions:** The quality of a contribution is not measured by its size or whether it was merged. A well-written bug report that clearly explains the issue and provides reproduction steps is more valuable than a large pull request with poor documentation. Activity and impact are different things.

> **On AI-generated work:** AI tools used to generate code, documentation, translations, or written reflections and submitted as the student's own work are academic dishonesty. The learning log is the best early signal: if it shows no struggle with a task that should have been hard, that is worth a conversation.

### Readings and resources

**Foundational texts (all free online):**
- Richard Stallman, "Free Software, Free Society" (selected essays): [gnu.org](https://www.gnu.org/philosophy/fsfs/rms-essays.pdf)
- Karl Fogel, "Producing Open Source Software": [producingoss.com](https://producingoss.com)
- Eric Raymond, "The Cathedral and the Bazaar": [catb.org](http://www.catb.org/~esr/writings/cathedral-bazaar/)
- Lawrence Lessig, "Free Culture" (Chapter 1): [free-culture.cc](https://www.free-culture.cc)

**India-specific:**
- FOSS United blog: [fossunited.org](https://fossunited.org/blog)
- Kerala KITE case studies: [kite.kerala.gov.in](https://kite.kerala.gov.in)
- Frappe engineering blog: [frappe.io/blog](https://frappe.io/blog)
- Advice for College Students: [frappe.io/blog/engineering/advice-for-college-students](https://frappe.io/blog/engineering/advice-for-college-students)

**Digital commons and social impact:**
- Yochai Benkler, "The Wealth of Networks" (Chapter 3): [free online at benkler.org](http://www.benkler.org/Benkler_Wealth_Of_Networks.pdf)
- OpenHealthcare Network: [ohc.network](https://ohc.network)
- eGov Foundation: [egov.org.in](https://egov.org.in)
- Sunbird documentation: [sunbird.org](https://sunbird.org)
- OpenStreetMap Beginner's Guide: [wiki.openstreetmap.org/wiki/Beginners%27_guide](https://wiki.openstreetmap.org/wiki/Beginners%27_guide)
- Wikipedia "Five Pillars" and contribution guides: [wikipedia.org/wiki/Wikipedia:Five_pillars](https://en.wikipedia.org/wiki/Wikipedia:Five_pillars)

**Licence and legal:**
- SFLC.in's licensing resources: [sflc.in](https://sflc.in)
- Creative Commons licence chooser: [creativecommons.org/choose](https://creativecommons.org/choose/)
- Open Source Initiative's licence list: [opensource.org/licenses](https://opensource.org/licenses)

**Community health and project evaluation:**
- CHAOSS metrics: [chaoss.community](https://chaoss.community)
