**FileDropzone** — the entry point of the analyzer: upload a Slack export. Shows a dashed Carbon field that highlights on drag, then a green-accented file chip once a file is chosen.

```jsx
<FileDropzone
  fileName={file?.name}
  onFile={(f) => setFile(f)}
  onClear={() => setFile(null)} />
```

Props: `accept`, `title`, `hint`, `fileName` (chip mode), `onFile`, `onClear`.
