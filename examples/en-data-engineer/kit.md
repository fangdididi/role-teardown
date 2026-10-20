# Teardown kit: Parcelwise, Senior Data Engineer (fictional example)

Inputs: `posting.md` (the job ad), `cv.md` (Alex's general CV), plus four intake answers from Alex.
Outputs: this file, `cv.tailored.md`, `note.md`.

## 0. Intake answers (asked once, up front)

1. *Is there anything in your past that looks like "events arriving late"?* Yes: courier phones buffer GPS pings when offline; they arrive up to 2 h late. I set up event-time windows with a 3 h watermark in Kafka Streams.
2. *Did late data ever change a published number?* Next-day delivery reports used to be revised about 1 day in 5. Not once in the last 9 months.
3. *Backfills?* 18 months of history after a schema change, 6 partitioned runs, row-count checks, no dashboard downtime.
4. *Hard limits?* Needs visa sponsorship; happy with 2 office days in Rotterdam.

## 1. Strip: five layers of the posting

| Layer | What the posting says | Tag |
|---|---|---|
| Stated | Python + SQL pipelines, dbt, Airflow, BigQuery on GCP, streaming / late data, data quality ownership, mentoring | [Q] |
| Weighted | "late-arriving" and "event-time" appear in both duties and requirements; the late-scan problem is the second bullet and the only one with a number (6 hours) | [Q] |
| Implied | The ETA shown at checkout is wrong often enough to hurt; the ETA team can't fix it alone because the training data is incomplete | [I] |
| Gates | 5+ years; hybrid Rotterdam 2 days; written English. Visa sponsorship is *offered* (benefits section) | [Q] |
| Noise | "fast-paced, fun team", "cares about our planet", salary and perks | [Q] |

`teardown.py signals` agreed: top terms were pipelines, late-arriving, Python, event-time, Airflow, dbt, data quality, ETA.

## 2. Hiring hypothesis

> They are hiring because **checkout ETAs are trained on days that are not finished yet** [I].
> The person must **make late depot scans land in the right day and stop bad data reaching training** [Q+I] within **the first quarter** [G].
> Their biggest fear is **a senior who only knows batch and cron, and repeats the current mess in Airflow** [I].

Confidence: medium. Two of three clauses rest on quoted text.

## 3. Probe log (≤ 5 public sources)

| Source | Finding | Effect on hypothesis |
|---|---|---|
| Parcelwise engineering blog (example) | 2026 post on moving to BigQuery; mentions "ETA complaints" in support tickets | Strengthens "ETA is hurting" |
| Other open roles (example) | An "ML Engineer, ETA" role opened the same week | Confirms a paired ETA push; mention collaboration |

## 4. Proof atoms (from CV + intake)

| # | Did | What | Result | Receipt | Grade |
|---|---|---|---|---|---|
| P1 | Handled | Late GPS pings with event-time windows, 3 h watermark | Report revisions 1 in 5 days → 0 in 9 months | Intake answer, Rotafresh | A− (number, no link) |
| P2 | Rebuilt | Order-to-doorstep pipeline, Python + SQL | 3h10 → 40 min | CV | B |
| P3 | Added | dbt tests + Slack alerting on 120 models | Caught before hours 30% → 85% | CV | B |
| P4 | Backfilled | 18 months history | 6 runs, zero downtime | Intake | B |
| P5 | Migrated | 14 cron jobs → Airflow 2 | Failed runs ~6/month → 1 | CV + intake | B |
| P6 | Mentored | Junior engineer to solo on-call | 5 months; ~15 PR reviews a month | CV + intake | B |

## 5. Fit map

| Requirement | Best atom | Grade | Plan |
|---|---|---|---|
| Late-arriving / event-time data | P1 | Covered | Lead with it in summary and note |
| Python + SQL pipelines, 5+ yrs | P2, 6 yrs | Covered | Say "6 years" in the summary |
| dbt + Airflow | P3, P5 | Covered | Name both in bullets, not only in skills |
| Data quality ownership incl. incident review | P3 | Covered | Add "ran the incident review" (true per intake) |
| BigQuery / GCP | none | Gap | Bridge: Snowflake + current GCP labs; say it plainly once |
| Mentoring, code review | P6 | Covered | Keep one bullet |
| Logistics / IoT (nice) | Rotafresh is delivery | Thin | Implicit; do not inflate |
| Terraform (nice) | none | Gap | Leave out |

Gate check: years ✔, English ✔, location ✔ (willing), authorization ✔ (sponsored).

## 6. Cut list (what left the CV, and why)

- "Results-driven … team player … fast-paced environment": generic, maps to nothing.
- "Responsible for the data platform": a duty, no result; replaced by P2 and P3.
- "Helped the analytics team with dashboards": no requirement asks for it.
- Skills list kept short; BigQuery appears only as "learning", never as a skill.

## 7. Red-team review

| Reader | Finding | Fix applied |
|---|---|---|
| Skimmer (7 s) | First read: "data engineer… GPS… Kafka". Title didn't say Senior | Headline now "Senior Data Engineer"; P1 moved into summary |
| Parser | "pipeline" vs posting's "pipelines", no "event-time", no "GCP" | Exact forms used once each; "Google Cloud Platform (GCP)" spelled out |
| Skeptic | "How do you know reports stopped being revised?" | Added the 9-month window; Alex can show the revision log |
| Skeptic | "BigQuery gap: hiding it?" | Stated once in skills and once in note, with what he is doing about it |

Script check, before → after:

| Check | `cv.md` | `cv.tailored.md` |
|---|---|---|
| `coverage` weighted | 44% | 94% |
| `lint` issues | 12 (4 generic, 3 duty bullets, 5 without numbers) | 0 |
| `lint note.md --max 200` | n/a | clean, 171 words |

## 8. Interview kit

**30-second pitch.** "I make delivery data trustworthy when events show up late. At Rotafresh that meant GPS pings up to two hours late; I used event-time windows and a watermark so published reports stopped changing. Your depot scans are the same problem with a longer tail, and I'd like to solve it with your ETA team."

**Proof stories** (situation · hard part · action · number · would do differently)

1. Late GPS pings · picking the watermark without delaying reports · measured lateness for 3 weeks, set 3 h · revisions 1 in 5 → 0 · would set it per region, not globally.
2. Cron to Airflow · jobs with hidden dependencies · drew the dependency graph first · failures 6 → 1 a month · would add data checks at the same time, not after.
3. 120 dbt tests · alert fatigue in week one · tiered alerts by business impact · 30% → 85% caught early · would involve analysts in choosing tests.
4. 18-month backfill · not breaking dashboards · partitioned runs + row counts · zero downtime · would script the verification.
5. Mentoring · she was afraid of on-call · paired shadow rotations · solo in 5 months · would write the runbook with her, not for her.

**Questions to ask (each tests the hypothesis)**

- "How late is the 99th percentile depot scan today, and does it vary by depot?"
- "When the ETA model retrains, what decides that a day is complete?"
- "What did the last attempt to fix late scans try, and why did it stall?"

**Gap rehearsal.** "BigQuery: I haven't run it in production. The concepts I rely on (partitioning, clustering, incremental dbt models) carry over from Snowflake, and I'm doing the Google Cloud labs now. I'd expect to be productive on it within the first month."
