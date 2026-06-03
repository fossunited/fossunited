# Context
India produces approximately 1.5 million engineering graduates each year.<sup>[1]</sup> Of those, roughly 390,000 are from computer science and allied branches, about one in three.<sup>[2]</sup>. India's contribution to global open source projects remains disproportionately small relative to this scale. Most graduates leave college without having knowingly contributed to a single open source project, inspected the source code of a tool they used every day, or built the skills to participate in the communities behind the software the world runs on.

FOSS United believes that gap closes in the classroom, not after graduation. This guide is primarily written for everyone inside an engineering institution: faculty who want to change what they teach, administrators who want to reduce costs and align with national policy, and students who want to understand why any of this matters. At the end of this guide, we have also listed down ways for [non-engineering educational institutions](education-cross-disciplinary.md) to get involved.

### How to navigate?

You do not need to read this front to back. Use the [self-assessment](education-start-here.md) to find where your institution sits today, then follow the path it points to. Each section stands on its own.

> **A note on FOSS United's role:** This guide is designed for institutions to use independently. Every recommendation here can be acted on without involving us. That said, FOSS United runs programs, maintains a network of colleges, and has people in the community who have done this before. Wherever we can help, we have noted it.

<!-- ---


### Your progress tracker

Use this as a living checklist. The order below is recommended: coordination first, then tooling, then education, then research infrastructure.

| Done | Action | Then go to |
|------|--------|-----------|
| [ ] | **Identify a lead:** Find a faculty champion, an honorary expert, or hire a program manager who can run this on the ground. See [Who should run this program](#who-should-run-this-program) for guidance on what to look for. | [Pillar IV](education-pillars.md#pillar-iv-open-culture-and-community) |
| [ ] | **Set up coordination:** Launch an OSPO or equivalent coordination function around this person. | [Playbooks](#institution-playbooks) |
| [ ] | **Know your costs:** Have the finance and procurement team survey every educational software licence the institution currently pays for and calculate the total annual cost. Once the report exists, students can lead the FOSS tool and Linux installations as their first real contribution. | [Pillar I](education-pillars.md#pillar-i-open-software) |
| [ ] | **Open one textbook:** Identify one course where a freely available open textbook can replace a paid one. | [Pillar II](education-pillars.md#pillar-ii-open-education) |
| [ ] | **Credit contributions:** Add open source contribution as an assessed activity in at least one course: a pull request, a bug report, documentation, or a translation counts. | [Pillar II](education-pillars.md#pillar-ii-open-education) |
| [ ] | **Design a summer project:** Create a structured summer project program where students work on real open source software. FOSS United can connect you with projects and maintainers. | [Pillar IV](education-pillars.md#pillar-iv-open-culture-and-community) |
| [ ] | **Build institutional memory:** Set up an institutional repository to store everything the institution produces: syllabi, previous year question papers, student projects, theses, and faculty research. | [Pillar III](education-pillars.md#pillar-iii-open-knowledge-and-research) |
| [ ] | **Open your research:** Adopt a Creative Commons default for new faculty publications and course materials. | [Pillar III](education-pillars.md#pillar-iii-open-knowledge-and-research) |
| [ ] | **Teach it formally:** Introduce a dedicated FOSS elective or open source module, open to all engineering branches. See the [Digital Commons Course Guide](education-curriculum.md#digital-commons-course-guide) for a ready-to-use structure. | [Pillar II](education-pillars.md#pillar-ii-open-education) |
| [ ] | **Formalise student activity:** Establish a FOSS Cell with a written charter and at least one faculty advisor. | [Pillar IV](education-pillars.md#pillar-iv-open-culture-and-community) |
| [ ] | **Join the network:** Sign up for FOSS United's Education Workgroup. | fossunited.org |

--- -->

## References

The numbered references below correspond to citations in the text.

**[1]** TeamLease Services. "Only 10% of India's 1.5 mn engineering graduates to secure jobs this year." *Business Standard*, 16 September 2024. business-standard.com/finance/personal-finance/only-10-of-india-s-1-5-mn-engineering-graduates-set-to-secure-jobs-this-yr-124091600127_1.html

**[2]** All India Council for Technical Education (AICTE). BTech admissions and enrolment data, 2024-25. Reported in "BTech Admissions Surge with Computer Science in Lead." *Education Today*, 2024.

**[3]** Kerala Infrastructure and Technology for Education (KITE). "How switching to Linux-based free OS is saving Kerala govt schools Rs 3,000 crore." *The News Minute*. thenewsminute.com/kerala/how-switching-linux-based-free-os-saving-kerala-govt-schools-rs-3000-crore-101844

**[4]** MIT OpenCourseWare. ocw.mit.edu | ERPNext vs SAP Business One India pricing: SAP B1 licence cost Rs 8 to 75 lakhs for SMEs; ERPNext zero licence, Frappe Cloud from Rs 410/month. Source: dexciss.io/blog/educational-6/erpnext-vs-sap-business-one.

**[5]** National Programme on Technology Enhanced Learning (NPTEL). Course catalogue and YouTube statistics. Also cited in Class Central: "8000+ OpenCourseWare Courses from Top Institutions," October 2025. nptel.ac.in | classcentral.com/report/ocw-courses/

**[6]** Penn State University Libraries. "Students, faculty report benefits of open-source resources, study finds." *Penn State News*, 21 October 2025. psu.edu/news/university-libraries/story/students-faculty-report-benefits-open-source-resources-study-finds

**[7]** Ithaka S+R. "University Open Source Program Offices." August 2025. Describes the Saint Louis University capstone model. sr.ithaka.org/publications/university-open-source-program-offices/

**[8]** UC Santa Cruz Open Source Program Office. Open Source Research Experience (OSRE) and Summer of Reproducibility program. ucsc-ospo.github.io

**[9]** Ithaka S+R. "Open Source Program Offices." February 2024. Documents Johns Hopkins as the first US university OSPO and Sloan Foundation funding of 12 institutions. sr.ithaka.org/blog/open-source-program-offices/

**[10]** UNESCO. Recommendation on Open Educational Resources. 40th session of the General Conference, Paris, 2019. unesco.org/en/open-solutions/open-educational-resources

**[11]** Linux Foundation. "10th Annual Open Source Jobs Report." linuxfoundation.org/research/the-10th-annual-open-source-jobs-report

**[12]** Archambault et al. "Research impact of paywalled versus open access papers." Analysis of 3.3 million papers, 2007-2016. Cited in Eger et al. (2021), *Managerial and Decision Economics*. "OA papers of either type received 50% more citations than strictly paywalled papers." digitalcommons.unl.edu/scholcom/29/

### Institutional sources and platforms

| Resource | URL |
|----------|-----|
| FOSS United Foundation | fossunited.org |
| FOSS United Forum | forum.fossunited.org |
| Johns Hopkins OSPO | ospo.library.jhu.edu |
| CMU Libraries OSPO | library.cmu.edu/services/ospo |
| George Washington University OSPO | ospo.gwu.edu |
| UC Santa Cruz OSPO | ucsc-ospo.github.io |
| Kerala KITE | kite.kerala.gov.in |
| NPTEL | nptel.ac.in |
| SWAYAM | swayam.gov.in |
| SFLC India (GoI OSS Policy) | sflc.in/policies-and-cases |
| ERPNext pricing and comparisons | frappe.io/erpnext/pricing |
| Frappe engineering blog | frappe.io/blog/engineering/advice-for-college-students |
| Agami | agami.in |
| IFF | internetfreedom.in |
| iSPIRT | ispirt.in |
| VizChitra | vizchitra.com |
| Diagram Chasing | diagramchasing.fun |
| Reap Benefit | reapbenefit.org |
| Takshashila GCPP | takshashila.org.in |
| YLAC | ylac.org |
| Wikimedia India | wikimedia.in |
| OER Commons | oercommons.org |
| Creative Commons | creativecommons.org |
| Open Source Initiative | opensource.org |

---

*Published by FOSS United Foundation | Version 1.0 | foundation@fossunited.org | fossunited.org*

*This guide is published under [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). You are free to share, adapt, and build on it with attribution to FOSS United Foundation.*
