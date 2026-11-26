# AGENTS.md :: FOSS United Engineering Guide

- Single source of truth for how we build software here. Applies to every human contributor and every AI coding agent (Claude Code, Copilot, Cursor, Codex, etc.).

## 1. Engineer first, not a prompter

- State the problem before asking for a fix: symptom, expected behaviour, actual behaviour, suspected location in code.
- Bad: "the CFP form breaks on mobile". Good: "under 480px, `.cfp-footer`'s `position: fixed` clips the submit button, no safe-area inset".
- An agent executes a solution you understand, or helps you research/narrow the problem. It does not design the solution from a one-line prompt.
- Before asking for a bug fix: read the error, read the code, form a hypothesis. Ask the agent to confirm/falsify it, not "just fix it".
- Before asking for a feature: know which doctype/page/API it touches and why. Ask the agent to implement your design, not invent one.
- Fine: ask an agent to explain code, locate code, lay out options. Not fine: ship a change you can't explain, even if it works.
- Don't know where to start: say so explicitly, ask for problem-study as a step separate from asking for a fix.
- A new feature, DocType, hook, or public API needs a GitHub issue filed before code is written, not after.
- Fix the cause, not the symptom: no guard/try-except patched at the error site. Grep for and fix every copy of a bug, not just the instance you hit.
- Changing a public function/API signature: grep all callers first, across this repo, `dashboard/`, and `bruno-collection/`. New arguments go last, with defaults.

## 2. Reference material

- `https://github.com/frappe/skills` default standard for Frappe-flavoured agent skills. Check first for doctypes, permissions, hooks, REST/RPC.
- `Frappe_Claude_Skill_Package` (local skill) / `https://github.com/Impertio-Studio/Frappe_Claude_Skill_Package` fallback only, for gaps in the above.
- `development/frappe-semgrep-rules/rules/` (`code_quality`, `frappe_correctness`, `hooks`, `security`, `translate`, `ux`) run before any non-trivial Python/JS PR. Fix the code on failure, don't suppress the rule.
- Unsure how to structure something Frappe-specific: check Frappe core. Disagree with their pattern: raise it explicitly, don't invent a third way silently.
- `https://lawsofsoftwareengineering.com` (data: `https://lawsofsoftwareengineering.com/api.json`) catalogues named engineering laws (Conway's Law, Hyrum's Law, YAGNI, DRY, the Boy Scout Rule, Second-System Effect, Postel's Law, Technical Debt, and more). Apply the relevant ones wherever they fit a decision at hand. Spot one being violated in a way worth the team's attention: open a GitHub issue naming the law and the tension, don't just silently pick a side.

## 3. Code taste

- Reuse existing helpers/composables/macros/includes before writing a near-duplicate.
- Use standard APIs and existing repo helpers before adding custom logic.
- Watch for N+1 queries: a loop calling `frappe.get_doc`/`frappe.db.get_value` per row. Fetch in bulk (`frappe.get_all` with the fields you need, or a single query) instead.
- Default direction: reduce code and technical debt. Bigger cleanup out of scope: open a GitHub issue, don't do it unreviewed inside an unrelated PR.
- Small, single-purpose functions. Explicit over clever. Write code as docs.
- Object-oriented structure only where it maps the domain (`Event`, `Ticket`, `Chapter`), not as a goal itself.
- No abstraction for a hypothetical future need. Three similar lines beat a premature helper.
- No abbreviations in names (`exclude_ended_events`, not `excl_ended`).
- Match existing naming/layout conventions. Think a convention is wrong: raise it separately, don't silently fix it mid-change.
- Fail loudly near the bug. Don't swallow or paper over a broken state behind a wide try/except or a silent fallback.
- Validate only at boundaries (user input, external APIs, webhooks). Trust internal functions and framework guarantees everywhere else.
- One clear owner for any piece of state. Two places holding the same fact will eventually drift, pick a single source of truth.
- Prefer the platform's native behaviour (browser, Frappe, Bootstrap) over a custom reimplementation. Only override it when it's proven broken for our actual users, and say why.
- Build the smallest working version first, then iterate. Don't design for a requirement nobody has asked for yet.

## 4. Comments and docstrings

- Default: no comment. Add one only for a non-obvious constraint, a workaround for a specific bug, or a reason a seemingly-wrong choice is correct.
- Never restate what the code already says.
- Docstrings: one or two lines max, what it does + what a caller needs to know. No change-history in docstrings, that's for commit messages.
- Good names and small functions are the real documentation.
- Before opening a PR, re-read your own diff and remove any comment that narrates the change itself ("fixed the null check here").

## 5. Tests

- Any doctype, controller `.py`, or API method touched needs a test covering the changed behaviour. No exceptions for "small or obvious change".
- Keep tests precise and minimal: essential paths and realistic edge cases only, no padding for appearance of thoroughness.
- A test that doesn't fail when the named behaviour breaks is worse than no test.
- A new feature's test must fail without the change, that's what proves it tests the right thing. A bug-fix test is skippable only if the bug is obvious and hasn't recurred.
- Never weaken a test just to make it pass. Fix the code or admit the test caught something real.
- Use the module's existing factory/helper pattern for fixtures. Avoid raw `frappe.get_doc({...}).insert()` unless no helper exists.
- Run the relevant test module (or have the human run `bench run-tests`, agents can't run `bench` here) before calling a change done.

## 6. Commits and PRs

- Atomic commits only: one purpose per commit, one fix per PR. Never sweep several unrelated changes into one large commit or PR, split them, each one its own record.
- Commit messages: bullet points, short, plain English. State what changed, why, and what state it leaves things in, not just a diff restatement.
- Write good commit description, developers intend to check git blame on why certain change was made, state purpose and reason of a change.
- PR description reasoning comes from the author's own understanding. An agent may tidy wording, never invent the justification.
- Reference the related GitHub issue/discussion when one exists.
- UI changes include before/after screenshots in the PR description. Target `develop`, use Conventional Commits for the PR title (`fix:`, `feat:`, `refactor:`, `perf:`, `chore:`, `!` for breaking).

## 7. AI agents specifically

- This bench runs in Docker. Never run `bench serve/build/migrate/execute/clear-cache/console`. Hand the exact command to the human, wait for their output. Plain `python3` scripts are fine to run directly.
- Never edit doctype `*.json` directly. Ask the human to change it via Desk. Reading a doctype JSON for a fieldname/type/options lookup: prefer targeted `grep`/`python3 -c` over reading the whole file.
- Never commit scratch planning/plan markdown files into the repo.
- Never `git commit` on the human's behalf unless explicitly asked for that specific commit.
- Unsure how Frappe solves something: check Frappe/ERPNext core first. Still unsure: say "I don't know, author should decide", don't guess confidently.
- Never claim to have run or reproduced something you did not actually run.
- Don't refactor broadly across the repo unless explicitly asked, even if the opportunity is obvious.
- Review your own diff before handing it to the human, same "engineer first" bar as section 1 applies to an agent's own output.

## 8. Security and permissions

- Principle of least privilege: a whitelisted method exposes the minimum it needs. Don't default a new API to `allow_guest=True` for simplicity, justify it explicitly when guest access is genuinely required.
- Check the caller's role/permission inside the method itself (a decorator, or an explicit `frappe.has_permission`/role check), don't rely on the frontend or the caller to gate access.
- Never use `ignore_permissions=True` or a blanket role grant to patch around a permission bug, that's the symptom, fix the actual permission/role setup instead.
- Rate-limit any public or guest-accessible endpoint that can be hit repeatedly (ticket purchase, CFP submission, coupon checks, and similar).
- Treat every new whitelisted or guest API as a security review item: check it against `development/frappe-semgrep-rules/rules/security`, and add Bruno API tests covering the permission boundary, not just the happy path.
- Never commit inside a `doc_events` hook.

## 9. Docs style (`docs/docs/*.md`)

- British English. Simple, precise sentences, no filler ("ensures a smoother experience").
- Add screenshots/diagrams for any multi-screen flow.
- Cross-link to existing docs pages instead of re-explaining a concept covered elsewhere.
- Add more reference links to cover topic knowledge for readers.

## 10. Accessibility (WCAG)

- WCAG 2.2 AA minimum on every new/changed HTML surface, checked before visual polish. Long-term goal: 100% WCAG across the platform.
- Semantic HTML over `<div role="...">`. Real `<button>`, `<ul>/<li>`, `<fieldset>/<legend>` for new code, not ARIA-retrofitted divs.
- Recurring pitfalls: collapse toggles must be real `<button>`; never `role="listitem"` directly on `<a href>` (wrap it instead); `aria-hidden="true"` must never be the only copy of real content; live regions must announce zero-result states too; toggle/filter buttons need `aria-pressed`; aria-labels read as sentences ("12 Award Nominations"), not fragments ("Award Nominations: 12").
- Dashboard colour tokens: frappe-ui's gray ramp only has two tiers that reliably clear AAA contrast, and some Tailwind config aliases resolve to undefined vars and render nothing. Verify any colour utility against the compiled CSS before relying on it, don't assume from the config file.

## 11. Frontend stack

- Jinja pages (`www/`, `templates/`): Bootstrap 4 first, `fossunited/public/css/custom.css` only when BS4 has no equivalent (e.g. `.gap-1`-`.gap-8`, `.text-xs`-`.text-4xl`).
- Tailwind: `dashboard/` only, purged out of Jinja builds. Never use it in a `.html` Jinja template.
- Dashboard: frappe-ui-centric. Prefer frappe-ui components/composables (`useCall`, `useList`, `useDoc`) over hand-rolled forms or `createResource`.
- Dev commands (hand these to the human, agents can't run `bench` here): `bench serve`, `bench build --app fossunited`, `npm run build-tailwind`, `bench clear-cache`.

### v3 / m-* design system

- `v3-*` is the base system, used site-wide: `.v3-page` enables dark mode, `.v3-container` (840px)/`.v3-container-wide` (1024px) center content, `.v3-card`, `.v3-btn` (+ `-dark`/`-secondary`/`--sm`), `.v3-pill`, `.v3-tag`, `.v3-status`, `.v3-badge.v3-badge-{sm/md/lg}.v3-badge--{subtle/solid/outline/ghost}-{colour}`.
- `m-*` is a specialised palette/component layer built on `.v3-page`, for Maintainer-branded pages only.
- Dark mode: `[data-theme="dark"]`. A page needs the toggle macro (`{{ theme_toggle() }}` or `{{ v3_navbar() }}`) present, or `common_functions.js` forces light mode.
- Colour values (OKLCH, `--m-*`) live in `custom.css` as the single source of truth. Don't copy exact values into docs or code comments, they drift, read the file instead.
- Custom 840px breakpoint, not BS4's 768/992px, scoped under `.m-page`: mobile-first default, `@media (min-width: 840px)` for desktop.
- Known CSS quirks (image rounding, hover colour on dark surfaces, BS4 `!important` utility fights) are easy to rediscover the hard way. Check `custom.css` and existing components for the established fix before re-deriving one.

### Visual/UX design taste

- Consistency beats personal preference: reuse an existing `v3-*`/`m-*` pattern before inventing a new visual treatment for the same kind of element.
- Design mobile-first, verify desktop second.
- Prefer a native HTML/Bootstrap control over a custom-built widget unless the native one is proven to fail for our users (and then document why, don't just swap it quietly).
- Restraint on motion and decoration: a transition or animation should clarify state change, not decorate it.
- Any new colour, spacing, or component choice should trace back to the existing design system or a documented reason it doesn't fit, not a one-off aesthetic call.

### Key files

| Path | What it is |
| --- | --- |
| `fossunited/public/css/custom.css` | Main CSS, `m-*` suite near the bottom |
| `fossunited/templates/macros/breadcrumb.html` | `v3_navbar()` + `theme_toggle()` |
| `fossunited/templates/macros/maintainer_event_card.html` | Event card macro |
| `fossunited/templates/macros/indiafoss.html` | `if_header()` / `if_footer()` |
| `fossunited/templates/foss_base.html` | Base layout template |
| `dashboard/src/` | Vue 3 dashboard app (Tailwind OK here) |
| `development/indiafoss/*.html` + `*_context.py` | Staging copies of hand-pasted Web Page content, never auto-deployed |
