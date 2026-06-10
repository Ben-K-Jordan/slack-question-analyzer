**MetricTile** — single headline statistic for the results summary row (total questions, groups, threshold). Light Carbon numeral, uppercase caption.

```jsx
<MetricTile label="Total questions" value={49} />
<MetricTile label="Threshold" value="85" unit="%" accent="var(--purple-60)" />
```

Props: `label`, `value`, `unit`, `delta` (+/- colored), `accent` (left bar).
