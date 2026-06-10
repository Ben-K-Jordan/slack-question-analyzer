**Slider** — continuous range control. Primary use: the similarity threshold that tunes how aggressively questions are grouped.

```jsx
<Slider label="Similarity threshold" value={85} min={0} max={100}
        format={(v) => `${v}%`} onChange={setThreshold} />
```

Props: `value`, `min`, `max`, `step`, `onChange`, `label`, `format` (function for readout + rail labels).
