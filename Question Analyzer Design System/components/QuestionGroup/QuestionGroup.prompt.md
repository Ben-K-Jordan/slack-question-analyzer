**QuestionGroup** — the headline output row of the analyzer. Render a list of these, sorted by `count` descending, to show the most-asked questions. Expands to reveal every underlying occurrence with dates.

```jsx
<QuestionGroup
  rank={1}
  question="How do I configure the webMethods JDBC adapter connection?"
  count={14}
  maxCount={14}
  similarity="91%"
  keywords={['jdbc', 'adapter', 'connection']}
  questions={[{ text: '…', date: 'May 3' }, …]}
  defaultOpen
/>
```

Pass the same `maxCount` (top group's count) to every row so the heat-bars share a scale. Rank 1–3 get the blue heat ramp; lower ranks fade to gray.
