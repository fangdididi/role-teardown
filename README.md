**English** | [简体中文](README.zh-CN.md)

# Role Teardown

> Take a job posting apart like a reverse engineer. Rebuild your application from proof, and cut everything else.

Most AI-written applications look the same: they copy the duty list, open with "results-driven team player", list every task you ever did, and sometimes invent a skill to close a gap. Recruiters skim them in seconds and move on.

**Role Teardown** is an agent skill that works the other way round. It first decodes what the hiring team actually needs (the problem behind the posting, not just its keyword list), then mines your real achievements into checkable **proof atoms**, and rebuilds a short, specific application where every line answers the posting with evidence. Three hostile readers (a 7-second skimmer, an ATS parser and a skeptical hiring manager) review the draft before you ever send it. Nothing is fabricated: unknown numbers become visible `[NEED NUMBER]` placeholders, and real gaps are named, not hidden.

It works in English and Chinese, for any field: engineering, product, operations, marketing, research, design.

```text
before  "Responsible for the data platform."            → no result, no number, no match
after   "Handled late-arriving courier GPS pings (up to 2 h late) with Kafka event-time
         windows and a 3 h watermark; next-day reports: revised 1 day in 5 before,
         never in 9 months since."                      → answers the posting's #1 problem
```

## Features

- **Five-layer teardown** of any posting: Stated, Weighted, Implied, Gates, Noise, with every line tagged as quoted, inferred or guessed.
- **Hiring hypothesis**: a three-clause statement of why the role exists, what the hire must achieve, and what the team fears. Everything else points at it.
- **Gate check first**: if a hard requirement (years, degree, location, visa, language) clearly fails, you hear it before any writing starts.
- **Proof atoms** graded A/B/C by whether they carry a number and a receipt, plus a **fit map** that marks each requirement Covered, Thin, Gap or Gate, with an honest move for each gap.
- **Lean build rules**: every line pays rent; the top third of the CV answers the hypothesis; a three-move cover note (their problem, my receipt, first steps).
- **Three-reader red team**: Skimmer, Parser (ATS) and Skeptic, at most three findings each.
- **Interview kit**: 30-second pitch, proof stories in five beats, questions that test the hypothesis, and gap rehearsal.
- **Helper script** (`scripts/teardown.py`, Python 3 standard library): weighted requirement terms and hard gates from the posting, weighted CV coverage with "is it in the top third?", and a lint for stock phrases, duty-style bullets, missing numbers and placeholders, in English and Chinese.
- **Honesty built in**: no invented facts, no hidden keywords, inferred content labelled, nothing sent on your behalf.

## The eight passes

```text
 1 Strip        posting → five layers + gate check
 2 Hypothesize  why this role, why now, what they fear
 3 Probe        ≤ 5 public sources (optional)
 4 Mine         your material → proof atoms (A/B/C)
 5 Map          requirement → atom → Covered / Thin / Gap / Gate
 6 Cut          lean CV + three-move cover note
 7 Voice        specific nouns, numbers, no stock phrases (lint)
 8 Red-team     Skimmer · Parser · Skeptic → fixes → interview kit
```

## Installation

The skill is the folder itself; `SKILL.md` is what the agent reads. Name the folder `role-teardown`.

**Claude Code**

```bash
# for all your projects
git clone https://github.com/fangdididi/role-teardown ~/.claude/skills/role-teardown
# or just for the current project
git clone https://github.com/fangdididi/role-teardown .claude/skills/role-teardown
```

**OpenAI Codex**

```bash
git clone https://github.com/fangdididi/role-teardown ~/.codex/skills/role-teardown
```

**Cursor**

```bash
git clone https://github.com/fangdididi/role-teardown .cursor/skills/role-teardown
```

**Gemini CLI, OpenCode, Windsurf and other agents**

Clone into the agent's skills folder if it has one (often `.agents/skills/`). With the open skills installer you can also run `npx skills add fangdididi/role-teardown`. If your agent has no skill system, add one line to `AGENTS.md`, `CLAUDE.md` or your rules file:

```text
When I share a job posting, follow ./role-teardown/SKILL.md and use its scripts/teardown.py.
```

The helper script needs Python 3.8 or newer. The method works without it.

## Usage

Paste a job posting (or a link) and your CV, and ask in plain words:

```text
Here's the JD and my CV. Tear it down and tailor my application.
Is this role a fit? Just strip the posting and map my CV, no writing yet.
I have an interview for this role on Friday. Arm me.
```

The agent asks up to five intake questions at once (aimed at proof your CV is hiding), then writes a teardown kit into `applications/<company>-<role>/`:

```text
teardown.md   layers, hypothesis, probe log, proof atoms, fit map, cut list
cv.md         tailored CV
note.md       cover note or application message
review.md     red-team findings, coverage and lint before → after
interview.md  pitch, proof stories, questions, gap rehearsal
```

You can run the script on your own, too:

```bash
python3 scripts/teardown.py signals  examples/en-data-engineer/posting.md
python3 scripts/teardown.py coverage examples/en-data-engineer/posting.md examples/en-data-engineer/cv.md
python3 scripts/teardown.py lint     examples/en-data-engineer/cv.md
```

## Examples

`signals` on the English example posting (abridged):

```text
TITLE: Senior Data Engineer, Delivery Intelligence (fictional example)

REQUIREMENT SIGNALS (higher = stated harder, earlier, more often)
 score   n  term  [sections]
   6.5   2  pipelines  [duty, must]
   6.0   2  late-arriving  [duty, must]
   5.9   2  Python  [duty, must]
   5.6   2  event-time  [duty, must]
   5.5   2  Airflow  [duty, must]

HARD GATES (check these before writing anything)
  - location: Parcelwise · Rotterdam, hybrid (2 days in office) · Full time
  - experience: 5+ years building production data pipelines in Python and SQL.
  - authorization (offered, from benefits): We sponsor visas for this role.
```

`lint` on the original CV (abridged):

```text
GENERIC (4)
  - results-driven
  - team player
  - passionate about
  - fast-paced environment

DUTY-NOT-RESULT (3)
  - L10: Responsible for the data platform.
  - L11: Worked on Kafka consumers for courier GPS pings.
  - L14: Helped the analytics team with dashboards.
```

| Example | Language | Role | Coverage | Lint issues |
|---|---|---|---|---|
| `examples/en-data-engineer/` | English | Senior data engineer, fictional parcel company | 44% → 94% | 12 → 0 |
| `examples/zh-ai-product-ops/` | Chinese | AI 产品运营, fictional cross-border seller tools company | 40% → 83% | 12 → 0 |

Each example folder contains the posting, the original CV, the full `kit.md` (all eight passes), the tailored CV and the cover note. All companies and people in the examples are invented.

## File structure

```text
role-teardown/
├── SKILL.md                         # the skill (English), read by the agent
├── SKILL.zh-CN.md                   # the skill (Chinese)
├── README.md                        # this file
├── README.zh-CN.md                  # Chinese README
├── LICENSE                          # MIT
├── scripts/
│   └── teardown.py                  # signals / coverage / lint
├── templates/
│   ├── teardown-kit.md              # empty kit skeleton (English)
│   └── teardown-kit.zh-CN.md        # empty kit skeleton (Chinese)
└── examples/
    ├── en-data-engineer/
    │   ├── posting.md  cv.md  kit.md  cv.tailored.md  note.md
    └── zh-ai-product-ops/
        ├── posting.md  cv.md  kit.md  cv.tailored.md  note.md
```

## What it will not do

- Invent experience, numbers, tools or credentials.
- Hide or stuff keywords.
- Submit applications, email recruiters or message anyone for you.
- Upload your CV anywhere.

A high coverage score only means your wording matches the posting. It does not make a claim true, so the skill always values an A-grade proof atom over a keyword.

## License

[MIT](LICENSE) © 2026 fangdididi
