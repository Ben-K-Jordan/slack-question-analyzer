**Button** — the primary action trigger; use for submit, analyze, export, and navigation actions. Carbon styling: sharp corners, icon pinned to the right edge.

```jsx
<Button variant="primary" icon={<ArrowRight size={16} />} onClick={run}>
  Analyze questions
</Button>
```

Variants: `primary` (blue, main action), `secondary` (dark gray), `tertiary` (blue outline), `ghost` (text-only), `danger` (red destructive). Sizes `sm | md | lg`. Pass `fullWidth` to stretch; `icon` to add a right-pinned glyph.
