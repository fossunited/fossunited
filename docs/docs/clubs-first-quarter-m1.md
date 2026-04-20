## Month 1: Discovery and Foundations

The goal of Month 1 is simple: make people aware that your club exists and show them it is relevant to their lives. Do not worry about running perfect events yet. Focus on showing up, listening to your peers, and finding those students who are genuinely excited to build this community with you.

Check out and add to the [contribution ideas](clubs-contribution-ideas.md) along the way.

> **Note:** This is a framework, not a rigid schedule. Your campus has its own rhythms, constraints, and opportunities. Adapt freely.

---

### Step 1: Set Up Your Communication Channels

Before your first event, create the club's communication presence. This gives early interest a place to land.

**Create these in Week 1:**
- A primary group chat (Telegram, Discord, Whatsapp, etc.) for all members
- A private leadership group for your core team. Feel free to add FOSS United team members to it to make communications easier.
- A club email address for official communications (optional)
- Social media accounts (Instagram or LinkedIn works well for campus clubs)
- A public GitHub organisation for the club

---

### Step 2: The Inaugural Event

Your first event sets the tone for everything that follows. We recommend a booth-style format rather than a traditional lecture. Students explore at their own pace, you get rich signal on where interests lie, and it feels like an event rather than a class.

**Suggested format:** a 2-3 hour open exploration session with four or five concurrent stations/booths where students get to explore different tracks under Digital Commons.

> **Tip:** Display a printed QR code that links directly to your Telegram or WhatsApp group during your inaugural event. Ideally, every booth should have one. This is how casual visitors become members.

---

#### Station 1: Contribution Pathways

Many students assume open source is only for expert programmers. This station is about correcting that misconception through conversation, not a form.

Have a club member at this station whose only job is to talk to visitors. Start with two simple questions:

> "What do you study?" and "What do you spend time on outside class?"

From their answers, guide them naturally toward a contribution role that fits. Here is a rough map to help the conversation flow:

| If they say... | Point them toward... |
|---|---|
| CS, coding, any programming | Developer track: code, review, testing |
| Design, arts, media | Designer track: UI/UX, icons, branding |
| Languages, linguistics, humanities | Localisation track: translating software to regional languages |
| Writing, journalism, communication | Documentation and advocacy track |
| Law, policy, social science | Digital rights and policy track |
| Electronics, maker, robotics | Hardware and open source firmware |
| "I just want to be involved" | Community and events track |

The goal is for every visitor to leave knowing there is a specific thing they could contribute, not a vague feeling that open source is "good to know." End each conversation by pointing them to your community group: **"We have a Telegram group where this conversation continues. Scan this QR code to join."**

Also showcase the [list of contribution ideas](clubs-contribution-ideas.md) for students to get a broader understanding.

---

#### Station 2: Technical Hands-On

The terminal does not have to be intimidating. Make it fun. The goal here is demystification through doing something immediately satisfying.

A few ideas that have worked well:

**Option A: Generate ASCII art of your college name**
```bash
sudo apt install figlet
figlet "FOSS United"
```
Students see their college name rendered in giant terminal text in 30 seconds. It is silly and memorable and it gets them comfortable typing commands.

**Option B: Make the terminal talk**
```bash
sudo apt install cowsay fortune
fortune | cowsay
```
A cow dispenses wisdom. Everyone wants a photo.

**Option C: Go through basics of Terminal and commands**

Have a mentor present at all times. The mentor's job is to make the first command feel normal, not to lecture.

---

#### Station 3: Data Privacy - Truth or Myth?

Instead of a discussion panel, run a short self-paced quiz that teaches as it goes. Print 8-10 cards, each with a statement. Visitors guess: **Truth or Myth?** The answer is on the back with a one-line explanation.

**Sample questions:**

| Statement | Answer |
|---|---|
| "Your WhatsApp messages are private from the Indian government." | **Myth.** Under the Telegraph Act, the government can order interception without a court order. |
| "India now has a law that lets you ask companies to delete your data." | **Truth.** The DPDPA 2023 gives you the right to erasure. Full effect from May 2027. |
| "Posting something publicly on Instagram means you gave up all privacy rights." | **Myth.** The right to privacy still applies even in semi-public spaces (per the Puttaswamy judgment). |
| "A company in the US can be held accountable under Indian data protection law." | **Truth.** The DPDPA applies to any entity offering services to people in India, regardless of where the company is based. |
| "You have the right to know exactly what data an app has collected about you." | **Truth.** Under the DPDPA, you can request access to your personal data. |

After the quiz, direct visitors to these plain-language resources to learn more:

- **Internet Freedom Foundation** - [internetfreedom.in](https://internetfreedom.in) - India's leading digital rights organisation. Their tag pages on [Privacy](https://internetfreedom.in/tag/privacy/) and [DPDPA](https://internetfreedom.in/tag/data-protection/) break down every major development in accessible language.

- **India Development Review explainer** - [IDR's breakdown of the DPDP Rules 2025](https://idronline.org/article/rights/indias-new-data-rules-put-the-state-above-citizens/) - a clear-eyed read on what the law actually does and does not protect

---

#### Station 4: Collaborative Mapping with OpenStreetMap

Run a live session to map your own campus on OpenStreetMap. Students see their edits go live on a global map within minutes. No coding experience needed.

**Before the event:**
- Have 2-3 club members create OSM accounts and run through the iD editor tutorial so they can guide others
- Identify 5-10 things on campus that are missing or wrong on OSM (a building, a canteen, a parking area, a gate)
- Prepare a short list of these as "missions" for participants

**At the station:**
1. Visitor creates a free account at [openstreetmap.org](https://openstreetmap.org)
2. They pick one "mission" from your list
3. A mentor walks them through making the edit using the built-in iD editor

**The easiest guide for first-time contributors:** [learnosm.org/en/beginner/start-osm](https://learnosm.org/en/beginner/start-osm/) - step-by-step, browser-based, no installation needed. The iD editor also has a built-in walkthrough that takes about 10 minutes.

For phone-only contributors, [StreetComplete](https://streetcomplete.app/) (Android) is even simpler: it shows you nearby things that can be added by answering plain-language questions, with no map editing knowledge required.

---

#### Station 5 (Optional): Hardware and Maker Corner

If your campus has electronics or maker culture, a Raspberry Pi, Arduino, or open hardware station draws a different audience and creates a memorable anchor. Even just running a Raspberry Pi as a small server with a "Linux runs on everything" sign works well.

---

### Step 3: Immediately After the Inaugural Event


**Two things to do within 48 hours:**

1. **Post-event questionnaire:** Share a short form with everyone who attended. Keep it to 5 questions or fewer: which station interested them most, what they want to learn or contribute, and whether they want to be more involved. This data directly shapes your Month 2 workshop decisions.

2. **Forum thread:** Post a write-up of the event on the FOSS United forum (or your college forum if one exists) by answering the [post event reporting template](clubs-peq.md).
 Also send a follow-up message in your community group thanking them for showing up and the plan for the next event.

3. **Post-event Call with FOSS United team:** If your club is working directly with the FOSS United team, please setup a [follow up call with the team](https://cal.com/team/fossunited/learners-program) for a debrief of the inaugural event and to plan follow up events.

---

### Month 1 Checklist

- [ ] Communication channels created (group chat, email, social media)
- [ ] Inaugural booth-style event planned, promoted, and held
- [ ] Post-event questionnaire shared with attendees
- [ ] Forum thread posted with event write-up and photos
- [ ] [Follow up call](https://cal.com/team/fossunited/learners-program) with FOSS United team scheduled

---
