# The Question Funnel — Pipeline Spec (v2.12.0, prompt pack 3, taxonomy v2)

How a Slack transcript becomes ranked topics. Design rule throughout: **the
language model is never asked to do the hard open-ended thing.** Embeddings
handle similarity, plain code handles counting/merging/collapsing, and the
LLM only answers small closed questions. Two models share the work:

| Role | Default model | Used for |
|---|---|---|
| Fast (typing) | `llama3.2` (3B) | Question extraction & detection — hundreds of output tokens |
| Quality (judging) | `llama3.1:8b` | Route adjudication, merge verify, group audit, labels, summary, answered — a few tokens each |

All LLM calls use Ollama structured output (`format=<JSON schema>`,
temperature 0, seed 42) — malformed output is impossible at decode time.
Verdicts are cached on disk keyed by (model + full prompt), so re-runs are
free and prompt edits self-invalidate the cache.

---

## Stage 0 — Parse & extract (fast model + code)

1. Transcript parsed into messages (Slack JSON with threads, dashed-separator
   text, or CSV). Markup, code blocks, mentions stripped.
2. **LLM-first extraction** (transcripts ≤ 150 messages; batches of 8):
   the fast model classifies each sentence REAL / RHETORICAL / CONTEXT,
   rewrites every REAL ask as a standalone question, preserves the asker's
   intent verb (HANDLE ≠ BYPASS), and tags each question with its TYPE —
   the second axis, independent of subject: how-to / troubleshooting /
   is-it-possible / feature-request / defect-report (prompt: EXTRACT, below).
3. Safety nets, in order:
   - a failed LLM batch falls back to regex extraction (questions never lost);
   - any message the fast model skipped that regex flags as a question gets a
     second look from the **quality** model; if that fails too, the regex
     version is kept;
   - recoveries identical to an already-extracted question are dropped
     (guards against the fast model crediting the wrong message);
   - **same-message rephrasing collapse** (code): two *different* rewrites
     from one message with ≥ 50% content-word overlap are one ask
     (`SAME_MESSAGE_REPHRASE_OVERLAP=0.5`). Identical text is exempt — that's
     a genuine repeat and occurrence counting owns it.

## Stage 1 — Route into buckets (embeddings + closed-choice LLM)

`taxonomy.json` (v2) defines 8 buckets, each with an `anchor` paragraph and
a fixed `category` (the merge map). **The anchors are the single biggest
routing lever — they're what the embeddings actually match against — and as
of v2 they are written in ASKERS' language (symptoms, goals, the messy way
people describe problems: "the file just sits there"), not documentation
language.** Convention encoded in v2: anything about the Action log lives in
File Handling.

- Every question and every anchor is embedded (`nomic-embed-text`, with the
  `clustering:` task prefix). Each question goes to its nearest anchor.
- Best anchor below `ROUTE_OUTLIER_FLOOR=0.4` → **needs review** (kept,
  amber-flagged; never forced into the closest wrong home).
- Top-2 anchors within `ROUTE_AMBIGUITY_MARGIN=0.03` → the quality model
  adjudicates a closed single-number choice (prompt: ROUTE, below; cap
  `ROUTE_LLM_MAX=20`). Reply `0` = honest abstain → needs review.
- Health stats land in `metadata.routing` (routed / ambiguous /
  llm_adjudicated / needs_review) tagged with the taxonomy version. A rising
  review rate = the taxonomy is missing a bucket.

## Stage 2 — Group inside each bucket (code + embeddings + LLM QC)

Per bucket, in order:

1. **Lexical dedup** (code, no AI): identical normalized text merges; then
   token-Jaccard ≥ `LEXICAL_DEDUP_THRESHOLD=0.9` merges rewordings. Merged
   duplicates COUNT as occurrences (that's the 2× ranking signal).
2. **Bank claims**: the learned topic bank (seeded from 150 curated MFT
   topics, grown by every run) claims questions whose embedding matches a
   known category centroid ≥ `BANK_MATCH_THRESHOLD=0.85`. Two questions
   claiming the same category group directly, regardless of their similarity
   *to each other*. Single-question claims are released back to clustering.
3. **Average-link clustering** at a FIXED bar `IN_BUCKET_THRESHOLD=0.8`.
   No adaptive noise gate inside a bucket — the bucket is topically coherent
   by construction, and the gate (built to keep unrelated topics apart)
   would strangle genuine sub-groups. A user-pinned `SIMILARITY_THRESHOLD`
   overrides the 0.8.
4. **Borderline merge pass**: cluster pairs whose best cross-similarity is
   within `LLM_VERIFY_MARGIN=0.03` of the bar are judged by the quality
   model (prompt: VERIFY; conservative, doubt → false; numeric guard: the
   merged cluster's average must stay ≥ bar − margin; cap `LLM_VERIFY_MAX=10`).
5. **Singleton rescue**: a singleton within `LLM_RESCUE_MARGIN=0.1` of an
   existing group is adjudicated by the verifier against its NEAREST group
   only (never looped against all groups — that would dissolve the uniques
   bucket). Doubt/failure → stays a singleton. Rare ≠ wrong: singletons far
   from every group never reach the LLM. Cap `LLM_RESCUE_MAX=10`.
6. **Group audit (final QC)**: every formed group of any size is checked by
   the quality model (prompt: AUDIT; suspicious of outliers but doubt →
   keep); flagged questions are evicted back to uniques. Biggest groups
   first; cap `LLM_VERIFY_MAX=10`.
7. Representative question = the member closest to the group centroid
   (extractive, never generated). Keywords = group word frequency × inverse
   frequency in the REST of the corpus (corpus-wide words score zero).

## Stage 3 — Name the groups (bank → LLM → keywords)

1. The **bank** names groups whose centroid matches a known category ≥ 0.85
   (stable names across runs, zero LLM calls; "recurring ×N" badge).
2. Unrecognized groups get an **LLM label** (prompt: LABEL; extractive only,
   `NEEDS_REVIEW` abstain). LLM-labeled groups are recorded into the bank —
   this is how the taxonomy of specific topics grows from real traffic.
3. Anything else falls back to keywords — and keyword names are NEVER
   banked (a junk name that sticks is worse than relabeling next time).

## Stage 4 — Merge map & summary (code + one LLM call)

- Each bucket collapses into its fixed `category` from `taxonomy.json` —
  the THEMES strip. Deterministic counts; no model involved.
- The executive summary (prompt: SUMMARY) receives those exact theme totals
  plus the ranked topic counts, and must lead with the themes. It may not
  invent topics, infer counts, or pick a winner among ties;
  `NEEDS_REVIEW` abstain → no summary shown.
- Optional: answer detection over thread replies (prompt: ANSWERED,
  three-way verdict) feeds the "Answered" stat.

---

## All knobs (.env)

| Variable | Default | Meaning |
|---|---|---|
| `SIMILARITY_THRESHOLD` | unset (auto) | pinning it overrides every bar, including in-bucket |
| `IN_BUCKET_THRESHOLD` | 0.8 | fixed grouping bar inside a routed bucket |
| `BANK_MATCH_THRESHOLD` | 0.85 | question/group → known-category match floor |
| `ROUTE_OUTLIER_FLOOR` | 0.4 | below this to every anchor → needs review |
| `ROUTE_AMBIGUITY_MARGIN` | 0.03 | top-2 anchors closer than this → LLM adjudicates |
| `ROUTE_LLM_MAX` | 20 | adjudication call cap per run |
| `LLM_VERIFY_MARGIN` | 0.03 | borderline-merge window below the bar |
| `LLM_VERIFY_MAX` | 10 | verify cap and audit cap |
| `LLM_RESCUE_MARGIN` | 0.1 | singleton-rescue candidacy window below the bar |
| `LLM_RESCUE_MAX` | 10 | rescue adjudication cap per bucket |
| `LEXICAL_DEDUP_THRESHOLD` | 0.9 | token-Jaccard for counting rewordings as repeats |
| `SAME_MESSAGE_REPHRASE_OVERLAP` | 0.5 | collapse bar for two rewrites of one ask |
| `OLLAMA_GENERATION_MODEL` / `OLLAMA_FAST_MODEL` | auto | quality / typing models |
| `LLM_TIMEOUT` | 180 | seconds per LLM call |
| `TAXONOMY_PATH` / `TAXONOMY` | taxonomy.json / on | bucket definitions |
| `DOMAIN_CONTEXT` | unset | appended to every prompt with a preserve-tokens clause |

## The prompts (pack v2, verbatim)

Every prompt also gets, when `DOMAIN_CONTEXT` is set:
`Context: the messages come from <DOMAIN_CONTEXT>. Technical terms, error
strings, API names, product names, and version numbers must be preserved
exactly.`

### EXTRACT (fast model; every batch)

```
If the messages are empty, malformed, or contain no request for help, return {"questions": []} and nothing else. Do not guess.

You extract answerable questions from support chat messages.
Classify each candidate sentence:
- REAL: the writer wants information, a fix, or a yes/no confirmation. KEEP.
- RHETORICAL: shaped like a question but seeks no answer ('Any thoughts?', 'Right?', 'Make sense?', 'Is there any way around this?', 'Anyone?'). DROP.
- CONTEXT: a statement describing their setup, environment, or what they already tried. Not a question — DROP it, but USE its facts to make the REAL questions standalone.
Rewrite every REAL question as a single standalone question.
Standalone test: a reader who never saw the message can answer it without asking what 'it', 'this', 'they', or 'the platform' refers to — pull the subject into the question explicitly. Drop greetings, signatures, and bullet characters.
Rules:
- A message often contains MORE THAN ONE real question: output one entry per REAL question, repeating the message number. Implicit help requests count as REAL.
- Output each distinct ask ONCE. Never output two rewrites of the same ask from one message (asking 'what is the error' and 'why does it fail' about the same failure is ONE ask).
- Enumerated steps of a single workflow or task list ('1. Find the file 2. Move it 3. Merge them') are ONE question about whether the whole workflow is possible — never one question per step.
- Preserve technical tokens exactly as written: error strings, API names, product names, version numbers, file names. Never normalize, paraphrase, or invent them.
- Messages may be in any language: keep each question in its original language.
Respond with JSON only: {"questions": [{"index": <message number>, "question": "<standalone question>"}]}. Use an empty list if none qualify.
```

Few-shot (sent with every batch): a 4-message example covering a
multi-question message, a statement, the real Action-log message (rhetorical
tail dropped, "they" made explicit), and the real file001/file002/Flow-Service
workflow message — plus two labeled DO-NOT wrong answers.

### DETECT (fast model; regex-first mode only)

```
If the messages are empty, malformed, or you cannot proceed with confidence, return {"questions": []} and nothing else. Do not guess.

You find IMPLICIT requests for help — problems stated as complaints or symptoms that imply the writer wants a solution, even with no question mark.
An implicit request exists if the writer describes something broken, blocked, failing, or behaving unexpectedly in a way that implies they want it resolved.
IS an implicit request: 'can't get the copy task to fire, stuck all day', 'metering numbers don't match the report', 'the transfer just hangs'.
NOT an implicit request: announcements ('deployed the fix, all green'), opinions, status updates without a problem, social chat, answers.
Rewrite each implicit request as ONE standalone question. Preserve technical tokens exactly; keep each question in its original language.
Respond with JSON only: {"questions": [{"index": <message number>, "question": "<the rewritten question>"}]}. Use an empty list if none qualify.
```

### ROUTE (quality model; ambiguous routes only; abstain 0)

```
If the question is empty, malformed, or you cannot decide with confidence, reply {"category": 0}. Do not guess.

You sort ONE support question into exactly one category. Reply with only the category number.
If the question fits two categories almost equally, OR fits none of them well, reply 0.
Never invent a number. Never explain.
Respond with JSON only: {"category": <number>}
```

User content lists only the two candidate buckets by id and name.

### VERIFY (quality model; borderline merges; doubt → false)

```
If either group is empty or malformed, answer {"same_topic": false} and nothing else. Do not guess.

You decide whether two groups of support questions are about the SAME topic.
The test: would ONE documentation page, fixing ONE root cause, resolve every question in both groups? If yes -> same topic. If they would need different pages or different fixes -> different topics.
Same product, same feature area, or shared vocabulary do NOT make two groups the same topic — only a shared root cause does. When in doubt, answer false.

Example: Group A asks how the metering agent gets installed; Group B asks how to set up monitoring alerts. Same product, different root causes: {"same_topic": false}
Example: Group A asks where quarantined files go; Group B asks what happens to a file when its virus scan fails. One antivirus-handling page covers both: {"same_topic": true}
Example: Group A asks why Azure container-level token auth fails; Group B asks why SFTP key authentication fails. Both are authentication, but different protocols, different root causes, different fixes: {"same_topic": false}
Example: Group A asks about triggering transfers via REST API; Group B asks about scheduling recurring transfers: {"same_topic": false}

Respond with JSON only.
```

### AUDIT (quality model; every formed group; doubt → keep)

```
If the group is empty or malformed, return {"outliers": []} and nothing else. Do not guess.

You quality-check a group of support questions that were matched as one topic, and flag any that do not belong.
Apply the same test as merging: would ONE documentation page, fixing ONE root cause, resolve the whole group? List the numbers of questions that fall OUTSIDE that page.
A question is an outlier only if it is about a DIFFERENT subject (different feature, different root cause) than the rest. Differences in wording, phrasing, or angle do NOT make a question an outlier.
If every question belongs, or you are unsure, return an empty list.

Example: 1. How do I install the metering agent? 2. How do I set up monitoring alerts? 3. Can monitoring alert on one application? Question 1 is about metering, the rest about monitoring/alerting: {"outliers": [1]}
Example: 1. Any good examples of using e2e monitoring? 2. How are real clients using monitoring/alerting? Same subject, different wording: {"outliers": []}

Respond with JSON only.
```

### LABEL (quality model; groups the bank doesn't know; abstain NEEDS_REVIEW)

```
If the group is empty, malformed, or too mixed to share one honest label, respond {"topic": "NEEDS_REVIEW", "summary": ""} and nothing else. Do not guess.

You name a group of related support questions with a short topic label.
Rules:
- Topic: 2-4 words, Title Case, using words that ACTUALLY APPEAR in the questions — do not introduce new vocabulary.
- The topic must name the SPECIFIC feature, system, or task being asked about.
- Never use vague topics like 'General Questions', 'Help', 'Miscellaneous', 'Various Issues', or 'Technical Questions'.
- Never use the bare product name alone as the topic — name the specific capability inside it.
- Never start the topic with 'How to' — it is a category name, not a question.
- Keep exact product and feature terms from the questions (don't paraphrase technical names).
- Summary: one sentence describing what people are asking.
- Respond with JSON only.
```

Plus three worked examples (antivirus pair, scheduled-action APIs, MFT UI
errors). A rejected/generic answer triggers ONE corrective retry.

### SUMMARY (quality model; once per run; abstain NEEDS_REVIEW)

```
If the topic list is empty or malformed, or you cannot summarize faithfully using only the listed topics and their exact counts, respond {"summary": "NEEDS_REVIEW"} and nothing else. Do not guess.

You write a brief executive summary of support-question analytics for a team lead. 1-2 sentences: the dominant themes, with concrete topic names and counts. No filler, no preamble, no advice.
Rules:
- Mention ONLY topics that appear in the list. NEVER invent or add a topic that is not listed, even to fill out a sentence.
- Use ONLY each topic's own question count exactly as listed. Do not estimate, round, or infer counts. The total question count is NOT a topic's count — never attach it to a topic.
- Mention topics in the order listed (they are ranked).
- If the list has a single topic, summarize that one topic and say the rest of the questions were each asked once.
- If several topics tie, say they are evenly spread rather than calling one dominant.
- If theme totals are provided, LEAD with the top theme(s) and their exact counts, then the top topic.
Example input: 'Total questions analyzed: 12' with topics 'Backups - 2', 'Login Errors - 2'. Example output: {"summary": "The 12 questions are evenly spread, led by Backups (2) and Login Errors (2)."}
Respond with JSON only.
```

### THEMES (quality model; FALLBACK only, when no taxonomy.json)

```
If the list is empty or malformed, return {"themes": []} and nothing else. Do not guess.

You organize support-question topics into broad themes for an executive funnel view. Produce 2 to 6 themes (fewer is better) with short names (1-3 words, Title Case, drawn from the items' own vocabulary). Assign EVERY numbered item to exactly one theme by its number. Group by shared subject area (would the same team own them?), not surface word overlap. Do not invent themes for single stragglers if a broader existing theme fits.
Respond with JSON only: {"themes": [{"name": "...", "items": [1, 4, 7]}]}
```

### ANSWERED (quality model; threads only; abstain unknown)

```
If the thread is empty or malformed, respond {"verdict": "unknown"} and nothing else. Do not guess.

You decide whether a question in a chat thread was actually ANSWERED by the replies.
A question is ANSWERED only if a reply contains specific, actionable information: a setting, a command, an API or endpoint, a config value, a yes/no WITH a reason, or a link to the exact relevant doc.
The following are NOT answers, even if friendly or on-topic: acknowledgments ('thanks', 'good question', 'same here'); promises ('let me check', 'I'll get back to you', 'looping in X'); asking for more details; restating or clarifying the problem; unrelated chatter.
Example: question 'How do I reset my password?', reply 'Settings > Security > Reset, then check your email.': {"verdict": "answered"}
Example: question 'Why did my transfer fail?', reply 'Hmm, let me check with the team.': {"verdict": "unanswered"}
Respond with JSON only: {"verdict": "answered"}, {"verdict": "unanswered"}, or {"verdict": "unknown"}.
```

---

## Regression fixture & evaluation

`fixtures/field_run_2026-06-10.json` freezes the real 2026-06-10 run (17
questions) with correct buckets and groupings. After ANY prompt, anchor, or
threshold change, run:

    slack-analyzer eval

It reports routing accuracy and grouping precision/recall against the
labels, listing every mismatch, missed pair, and wrong pair (exit code 1 on
any miss). The topic bank is excluded so the score measures taxonomy +
clustering + prompts, not learned history.

`metadata.llm_stats` tracks abstain/verdict rates per run (verify
true/false/uncertain, audit evictions, extract empty batches, label
abstains). If the rescue pass makes verify fire constantly, in-bucket
clustering is under-forming upstream — that's the real problem, not a
fuller-looking output.

## Known weak spots (observed in the v2.11.0 run, 2026-06-10 transcript — addressed in v2.12.0, kept for history)

1. **Under-grouping inside buckets.** Three thread-usage questions existed;
   only two grouped ("Thread Scaling" 2×, avg 72%, verifier-approved). The
   third ("Is there any way around the thread use issue in MFT customers
   with high scheduled actions and low threads allocated?") sat in uniques.
   Suspects: its average-link similarity to BOTH members < 0.8 and the
   borderline-merge window (bar − 0.03) too narrow, or the audit evicted it.
   Levers: `IN_BUCKET_THRESHOLD`, `LLM_VERIFY_MARGIN`, or a dedicated
   "absorb singletons into existing groups" verifier pass.
2. **Extraction meaning drift.** "Can the Copy Task to Target System be
   configured to bypass antivirus scanning errors?" — "bypass" was likely
   not the asker's word (handling/diagnosing ≠ bypassing). The
   preserve-verbatim rule covers tokens, not intent verbs. Lever: an
   extraction rule like "never substitute the asker's verb — if they asked
   how to HANDLE an error, do not write 'bypass'/'avoid'."
3. **Routing debatables.** "Is there a way to group Actions and filter by
   group name in wM MFT (SaaS)?" landed in Operations & Performance;
   File Operations is arguable. Lever: fatten the bucket anchors with the
   vocabulary you want them to win (anchors, not prompts, decide routing).
4. **Bucket-name vs category granularity.** The UI shows the merge-map
   category. The finer bucket (e.g. "Monitoring & Alerting" inside
   Operations & Performance) is stored on each group as `bucket` but not
   shown for uniques. Possible UI lever if categories feel too coarse.
