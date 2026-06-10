**Tag** — compact pill for keywords, categories, similarity badges, and statuses. Use soft fills by default; reserve `outline` for secondary/filter contexts.

```jsx
<Tag color="blue">authentication</Tag>
<Tag color="green" dot>Resolved</Tag>
<Tag color="gray" onDismiss={() => remove(id)}>timeout</Tag>
```

Colors: `gray | blue | green | red | purple | teal | magenta | cyan`. Sizes `sm | md`. `dot` adds a status dot; `onDismiss` adds a × button.
