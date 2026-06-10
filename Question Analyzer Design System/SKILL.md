---
name: question-analyzer-design
description: Use this skill to generate well-branded interfaces and assets for the IBM webMethods Question Analyzer, either for production or throwaway prototypes/mocks/etc. Contains essential design guidelines, colors, type, fonts, assets, and UI kit components for prototyping in the IBM Carbon design language.
user-invocable: true
---

Read the `readme.md` file within this skill, and explore the other available files
(`styles.css` and `tokens/` for foundations, `components/` for React primitives,
`guidelines/` for foundation specimens, `ui_kits/analyzer/` for a full app recreation,
`assets/` for the wordmark).

If creating visual artifacts (slides, mocks, throwaway prototypes, etc), copy assets out and
create static HTML files for the user to view — link `styles.css` for the real tokens and
compose the documented components. If working on production code, copy assets and read the
rules here to become an expert in designing with the IBM Carbon language as applied to this
product.

Core rules to honor: sharp corners (no border-radius except pill tags), IBM Blue `#0f62fe` as
the only brand color, IBM Plex Sans for UI / IBM Plex Mono for all numerals and data, an 8px
spacing grid, 1px gray hairlines and 3px left accent bars instead of heavy borders, flat solid
fills (no gradients/imagery), sentence-case copy, and no emoji in product UI.

If the user invokes this skill without any other guidance, ask them what they want to build or
design, ask a few focused questions, and act as an expert designer who outputs HTML artifacts
_or_ production code, depending on the need.
