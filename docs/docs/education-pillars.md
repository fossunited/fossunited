## The four pillars

Every institution can act on all four of these pillars - [Open Software](#pillar-i-open-software), [Open Education](#pillar-ii-open-education), [Open Knowledge and Research](#pillar-iii-open-knowledge-and-research), and [Open Culture and Community](#pillar-iv-open-culture-and-community). The scale and sophistication of what you do will depend on your size and resources, but nothing here requires a large budget or a specialised team to begin.

---

## Pillar I: Open Software

Replace proprietary tools with FOSS equivalents in labs, classrooms, and where possible in institutional operations.

### Why it matters

A student who graduates having only used licensed software has not learned the underlying discipline; they have learned a vendor's interface. When the licence expires or the vendor changes pricing, the institution is stuck. Open source software removes that trap: the tool is owned by no one and available to everyone, permanently.

FOSS tools are used extensively in industry and research. Python, Linux, Git, QGIS, KiCad, OpenFOAM, FreeCAD: these are not second-best options. They are what professionals actually use. Beyond individual tools, the practice of running open infrastructure teaches students that technology is something you can inspect, modify, and contribute to.

### Getting started

- **Audit first:** Have students survey every software licence the institution pays for and calculate the total annual cost. This gives leadership a financial case and gives students their first meaningful contribution.

- **Migrate one lab:** Start with Linux (Ubuntu or Fedora) in one computer lab. Kerala's KITE distribution (based on Ubuntu) is a reference for how this was done across 14,000 schools.<sup>[3]</sup> Document what worked and what did not, and share it with FOSS United's network.

- **Standardise version control:** Require Git and a version control workflow in at least one course. This applies equally to a civil engineering student managing CAD files and a CS student writing code.

- **Replace proprietary tools:** Use the [tools table](education-foss-alternatives.md) to find FOSS equivalents for your branch's most common proprietary software.

### Going further

- **File storage:** Replace shared proprietary cloud storage with a self-hosted Nextcloud instance. Students should interact with a system that respects their data and that they can actually inspect and contribute to. A shared Nextcloud installation also teaches students about cloud infrastructure from the inside.

- **Collaboration and communication tools:** Mattermost is a self-hostable alternative to Slack and Teams. Running it on your own server is straightforward and gives students a real deployment to maintain.

- **Institutional administration:** A mid-size institution switching from a proprietary ERP to self-hosted open source alternative saves lakhs annually and gains a system students can actually inspect and modify as a learning exercise.[ERPNext, built by Frappe in India](https://frappe.io/erpnext/for-education), covers admissions, attendance, finance, HR, and more. Zero licence fees if you can self-host or avail educational discounts.

- **Package Mirror:** Most college networks in India have limited bandwidth. A server that mirrors common repositories (apt, pip, npm, CRAN) removes a daily friction point for every student and faculty member on campus. Students run and maintain it as a live sysadmin exercise. The cost is modest: one server with reasonable storage. IIT Bombay has run one of the most-used Linux mirrors in India at [cc.iitb.ac.in](https://www.cc.iitb.ac.in/page/ftpmirrordistributions) for years and it is regularly cited as a reason the institution is trusted in open source circles. Other colleges that depend on your mirror will know your institution by name. That is a low-cost, high-signal way to build a reputation outside your own campus.

> **FOSS United can help:** We can connect you with institutions or volunteers that have already done lab migrations and are willing to share their experience. We also connect you with volunteers who can host workshops on specific FOSS tools. Write to foundation@fossunited.org.

---

## Pillar II: Open Education

Produce and use educational material that anyone can read, reuse, and improve.

### Why it matters

A faculty member who writes a good set of lecture notes and distributes them only to enrolled students has limited their reach to one batch, one year. The same notes published under a Creative Commons licence become a contribution to every student and teacher who finds them. MIT's OpenCourseWare demonstrated in 2001 that this model works at scale.<sup>[4]</sup> NPTEL did the same for India.

### Getting started

- **Replace one textbook:** Identify one course where a freely available open textbook can replace a paid one. Check NPTEL, OpenStax, or the OER Commons repository. A Penn State pilot found that faculty who made this switch reported higher student engagement and would recommend the change to colleagues.<sup>[6]</sup>

- **Publish your materials:** License your course notes and slides under Creative Commons Attribution (CC BY) and upload them to a public repository or your institutional repository.

- **Credit contributions:** Open source contribution as an assessed deliverable: a pull request, a bug report, a documentation improvement, or a translation. Students who do this are doing engineering work. Treat it as such.

### Curriculum integration

- **Introduce a FOSS module:** A 1 to 2 credit module on open source and digital commons, open to all engineering branches. This does not have to sit inside CS. A mechanical engineering student understanding why OpenFOAM exists and how to contribute to it is as valuable as a CS student understanding the same about Linux. See the [Digital Commons Course Guide](education-curriculum.md#digital-commons-course-guide) for a complete structure ready to adapt.

<!-- **Capstone projects:** Similar to the model piloted at [Saint Louis University](https://oss-slu.github.io/), undergraduates in a capstone course collaborate with postgraduate students on a real open source product development project, guided by faculty with open source expertise.<sup>[7]</sup> -->

- **Summer projects:** Design a structured summer project program where students spend 4 to 8 weeks contributing to a real open source project under the guidance of a maintainer or mentor. The key elements are: a live project, a real maintainer who reviews their work, a public record of their contribution, and a stipend or credit that makes it worth their time.

> **FOSS United can help:** We can help connect students with projects and maintainers, if you do not have existing relationships. We piloted a version of this with students from IIIT Delhi; details and lessons learned are on the [FOSS United forum](https://forum.fossunited.org/t/foss-and-software-engg-education/4934). Contact [foundation@fossunited.org](mailto:foundation@fossunited.org).

---

## Pillar III: Open Knowledge and Research

Make the research and intellectual output of your institution publicly available and permanently accessible.

### Why it matters

Research that sits in a closed journal or an institutional hard drive does not accumulate citations, does not invite collaboration, and cannot be built upon. Research published openly is cited 50% more on average.<sup>[12]</sup> It is also more likely to attract industry collaboration and international partnerships.

For institutions in India, where most faculty produce knowledge directly relevant to local problems, the public benefit argument for open publication is particularly strong.

### Getting started

- **Institutional repository:** Set up a repository using DSpace or EPrints (both FOSS) to store everything the institution produces: syllabi, previous year question papers, student projects, theses, dissertations, faculty publications, and technical reports. This is institutional memory, not just an archive.

- **Creative Commons default:** Adopt CC BY as the default licence for new faculty publications and course materials. This is the standard recommended by UNESCO's 2019 OER Recommendation.<sup>[10]</sup>

- **Preprint habit:** Deposit preprints of journal articles in open repositories (arXiv for engineering and sciences, Zenodo for datasets and software) before or alongside formal publication.

### Going further

- **Reproducible research:** Publish datasets and code alongside papers. UC Santa Cruz's Open Source Research Experience (OSRE) program has built an entire fellowship around making computational research reproducible, connecting students with faculty and industry mentors over the summer.<sup>[8]</sup>

- **Policy alignment:** For government-funded institutions, the Government of India's 2015 open source policy creates a policy context that extends naturally to publicly funded research outputs. Research produced with public funding has a reasonable expectation of being publicly accessible.

> **FOSS United can help:** We can connect faculty with the broader FOSS community for peer review of open source research tools and host research outputs on the FOSS United platform where appropriate.

---

## Pillar IV: Open Culture and Community

Everything else in this guide depends on whether people inside the institution actually believe in and practise openness. Culture is not a slogan. It is what happens when no one is watching.

### Why it matters

FOSS tools installed in a lab that no one knows how to use are just files on a server. The institutions that have made the most progress on open source adoption, from Johns Hopkins to Kerala's KITE schools, did so because someone inside the institution decided to be a champion and found others to join them. That person is often faculty, sometimes a student, occasionally an administrator. It starts with one person.

### Getting started

- **Find your champion:** Identify a faculty member, an honorary expert, or a hired program manager who will be the institution's open source point of contact. See [Who should run this program](education-program-manager.md) for what to look for. This person is the starting point for everything else.

- **Start a FOSS Club:** A small group of students with a written charter, a faculty advisor, and a clear purpose. FOSS United has a template charter and can connect your cell to the broader national community.

- **Go to where the community is:** Send students to IndiaFOSS (the annual national FOSS conference organised by FOSS United), city community events, and maintainer meetups. Exposure to people who have built open source projects changes how students think about what is possible.

### Building momentum

- **Host a local FOSS event:** FOSS United's flagship hackathon (FOSS Hack) and conference formats can be hosted locally. You can find more details on [hosting events](clubs-hosting-events.md) under FOSS Clubs documentation.

- **Summer projects:** Structure a summer program where students spend 4 to 8 weeks on a real FOSS project with a real maintainer. FOSS United can connect your institution with open source projects looking for contributors and maintainers willing to mentor. The IIIT Delhi pilot showed this produces both technical skills and a lasting sense of community belonging. [Read about it on the forum.](https://forum.fossunited.org/t/foss-and-software-engg-education/4934)

- **Join the Education Workgroup:** This is work in progress but FOSS United's Education Workgroup will be where faculty, administrators, and practitioners work collectively on curriculum frameworks, event formats, and shared resources for open source in Indian higher education.

> **FOSS United can help:** FOSS Clubs, City Communities, IndiaFOSS, FOSS Hack and Season of Commites are all active programs. Your institution can plug into any of these with a single email to foundation@fossunited.org.

---
