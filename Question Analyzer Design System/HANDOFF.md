# Question Analyzer — Engineering Handoff

Frontend prototype for the **IBM webMethods MFT / IWHI Slack Question Analyzer**.
This package contains the working UI (HTML + React/JSX), the design system it's built
on (CSS tokens + components), and all assets. Everything below the API line is **mocked
client-side** — your job is to replace the mock data with real backend responses.

---

## 1. What runs where

| Path | What it is |
|---|---|
| `ui_kits/analyzer/index.html` | **The app.** Open in a browser to run the full prototype. |
| `ui_kits/analyzer/*.jsx` | App screens & logic (see file map below). |
| `ui_kits/analyzer/app-data.jsx` | **Mock data — replace with API calls.** Defines `DASHBOARD_DATA` and `WEEK_DATA`. |
| `styles.css` + `tokens/` | Design system: CSS custom properties (color, type, spacing, motion) + IBM Plex fonts. Link `styles.css`. |
| `components/<Name>/<Name>.jsx` + `.d.ts` | Reusable UI primitives (Button, Tag, Card, MetricTile, Slider, FileDropzone, QuestionGroup) with TypeScript prop types. |
| `assets/` | Wordmark / mark SVGs (currently unused in-app; the header is text). |
| `guidelines/`, `_ds_*` | Design-system documentation/build artifacts — **not needed for the app**, reference only. |

**App file map** (`ui_kits/analyzer/`):
- `index.html` — loads React 18, Babel, Lucide icons, the component bundle, then the JSX below.
- `app-data.jsx` — **the data layer to replace.**
- `App.jsx` — top-level state: active view, modals, signed-in account.
- `AppHeader.jsx` — Dashboard/Week toggle, Upload transcript, account avatar.
- `DashboardView.jsx` — all-time ranked questions (consumes `DASHBOARD_DATA`).
- `WeekView.jsx` — weekly trend + ranked questions (consumes `WEEK_DATA`).
- `RankedRow.jsx` — the expandable ranked question row.
- `Modals.jsx` — Upload-transcript flow + email-connect/manage flow.
- `anim.jsx` — animation helpers + the SVG area chart.
- `Icon.jsx` — Lucide icon wrapper.

> **Note:** This is a styling/interaction prototype using in-browser Babel (no build step).
> For production, port the JSX into your real React app and call the APIs below.

---

## 2. Data contracts (what the backend must return)

The frontend reads two objects. Match these shapes and the UI works unchanged.

### `GET /api/dashboard` → `DASHBOARD_DATA`
All-time, ranked by occurrence.

```jsonc
{
  "totalQuestions": 136,        // int — all questions logged
  "totalGroups": 10,            // int — distinct topics/clusters
  "resolved": 71,               // int — answered/resolved count
  "topTopic": "Antivirus scanning",
  "groups": [
    {
      "rank": 1,                // int, 1-based, sorted by count desc
      "count": 28,              // int — occurrences (drives ranking + bar)
      "similarity": "92%",      // string — avg intra-cluster similarity (display only)
      "topic": "Antivirus scanning",      // short cluster label
      "question": "How do I configure virus scanning in MFT…?",  // representative question
      "keywords": ["mft", "antivirus", "quarantine"],            // string[]
      "questions": [            // every underlying occurrence
        { "text": "Copy Task to target failing: …", "date": "Jun 5" }
      ]
    }
  ]
}
```

### `GET /api/week?start=2026-06-02` → `WEEK_DATA`
Fixed Mon–Sun calendar week.

```jsonc
{
  "weekLabel": "Jun 2 – 8, 2026",
  "totalThisWeek": 22,
  "totalLastWeek": 18,
  "deltaPct": 18,               // int — % change vs last week (can be negative)
  "newQuestionTypes": 5,        // clusters not seen last week
  "groupsThisWeek": 8,
  "answered": 3,
  "trend": [14, 12, 19, 16, 18, 22],          // last 6 weeks' volumes, oldest→newest
  "trendLabels": ["May 5","May 12","May 19","May 26","Jun 1","Jun 8"],
  "groups": [
    {
      "rank": 1,
      "count": 4,
      "topic": "Antivirus scanning",
      "question": "How do I configure virus scanning in MFT…?",
      "keywords": ["mft", "antivirus", "quarantine"],
      "movement": "new"         // "new"  OR  signed int rank-change vs last week (+2, -1, 0)
    }
  ]
}
```

---

## 3. Transcript upload

The **Upload transcript** button posts the JSON export your Slack bot already produces
(the dated thread blocks of pulled-out questions). Suggested:

```
POST /api/transcripts            // multipart: file=<export.json>
→ 202 { jobId }
GET  /api/transcripts/:jobId     // poll
→ { status: "running"|"done", progress: 0-100,
    summary: { questionsAdded: 22, topics: 8, topTopic: "Antivirus scanning" } }
```

The modal shows a 4-stage progress (parse → extract → embed & group → rank) and a
success summary — wire these to real job status. After import, the dashboard refetches.

**Clustering / ranking is backend work** (embeddings + similarity threshold). The old
Streamlit prototype used a `SIMILARITY_THRESHOLD` (default 0.85) — keep that backend-side;
the UI intentionally exposes **no** provider/threshold controls.

---

## 4. Email digest (sign-in)

The avatar opens "Get your weekly report" — the user connects an email to receive the
**Week-in-Review digest every Monday**. Mock today; suggested:

```
POST /api/subscriptions   { email }      → { ok, nextDigest: "2026-06-15T09:00" }
DELETE /api/subscriptions/:id            // "Disconnect"
```

No real auth is implemented — it's an email-capture + weekly-send subscription.

---

## 5. Design system notes

- **Fonts:** IBM Plex Sans / Mono / Serif via Google Fonts (`tokens/fonts.css`). Self-host the `.woff2` for production.
- **Icons:** currently **Lucide** (CDN) as a stand-in for IBM's `@carbon/icons` — swap to `@carbon/icons` SVGs for production fidelity.
- **Tokens:** all color/spacing/type live as CSS custom properties in `tokens/`. Reference `var(--…)`, don't hardcode hex.
- Carbon language: sharp corners, IBM Blue `#0f62fe`, 8px grid, mono for all numerals, sentence-case copy.
