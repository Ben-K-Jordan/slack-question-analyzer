# UI Dashboard Plan - Slack Question Analyzer

## Overview
A modern, interactive web dashboard for analyzing Slack questions with real-time visualization and insights.

---

## Technology Stack Recommendation

### Option 1: Streamlit (Recommended - Fastest)
**Pros**: 
- Pure Python, no HTML/CSS/JS needed
- Built-in components (charts, tables, file upload)
- Auto-refresh, real-time updates
- Deploy in minutes

**Cons**: 
- Less customizable design
- Limited interactivity

**Time to Build**: 4-6 hours

### Option 2: Flask + React
**Pros**:
- Full control over design
- Professional look
- Highly interactive

**Cons**:
- Requires JavaScript knowledge
- More complex deployment

**Time to Build**: 20-30 hours

### Option 3: Gradio (Simplest)
**Pros**:
- Easiest to build
- Great for demos
- Shareable links

**Cons**:
- Limited customization
- Basic UI

**Time to Build**: 2-3 hours

**RECOMMENDATION**: Start with Streamlit, migrate to Flask+React if needed

---

## Dashboard Layout (Streamlit)

```
┌─────────────────────────────────────────────────────────┐
│  🔍 Slack Question Analyzer                    [Settings]│
├─────────────────────────────────────────────────────────┤
│                                                           │
│  📁 Upload Slack Export                                  │
│  ┌─────────────────────────────────────────────────┐   │
│  │  Drag & drop or click to upload                  │   │
│  │  Supported: .txt, .json, .csv                    │   │
│  └─────────────────────────────────────────────────┘   │
│                                                           │
│  ⚙️ Analysis Settings                                    │
│  AI Provider: [Ollama ▼]  Threshold: [0.85 ━━━━━━━]    │
│                                                           │
│  [🚀 Analyze Questions]                                  │
│                                                           │
├─────────────────────────────────────────────────────────┤
│  📊 Analysis Results                                     │
│                                                           │
│  ┌──────────┬──────────┬──────────┬──────────┐         │
│  │ Total    │ Groups   │ Unique   │ Avg      │         │
│  │ 49       │ 8        │ 7        │ 0.87     │         │
│  │ Questions│ Found    │ Questions│ Similarity│         │
│  └──────────┴──────────┴──────────┴──────────┘         │
│                                                           │
│  📈 Question Frequency Chart                             │
│  ┌─────────────────────────────────────────────────┐   │
│  │     ████████████ MFT Configuration (12)          │   │
│  │     ██████████ Antivirus Setup (8)               │   │
│  │     ████████ API Integration (6)                 │   │
│  │     ██████ Monitoring (5)                        │   │
│  │     ████ File Transfer (4)                       │   │
│  └─────────────────────────────────────────────────┘   │
│                                                           │
│  🔍 Question Groups (Expandable)                         │
│  ┌─────────────────────────────────────────────────┐   │
│  │ ▼ Group 1: MFT Configuration (12 questions)      │   │
│  │   Representative: "How do I configure MFT..."    │   │
│  │   Keywords: mft, configuration, setup, install   │   │
│  │   Similarity: 92%                                │   │
│  │                                                   │   │
│  │   Questions in this group:                       │   │
│  │   1. How do I configure MFT for Azure?          │   │
│  │   2. What's the best way to setup MFT?          │   │
│  │   3. Can I configure MFT with containers?       │   │
│  │   [Show all 12 questions]                        │   │
│  │                                                   │   │
│  │ ▶ Group 2: Antivirus Setup (8 questions)        │   │
│  │ ▶ Group 3: API Integration (6 questions)        │   │
│  └─────────────────────────────────────────────────┘   │
│                                                           │
│  📥 Export Results                                       │
│  [JSON] [CSV] [Excel] [PDF Report]                      │
│                                                           │
└─────────────────────────────────────────────────────────┘
```

---

## Key Features

### 1. **File Upload & Processing**
- Drag-and-drop file upload
- Support multiple formats (TXT, JSON, CSV)
- Real-time validation
- Progress bar during analysis

### 2. **Interactive Configuration**
- AI provider selection (Ollama/Azure/OpenAI)
- Similarity threshold slider
- Advanced settings (collapsible)
- Save/load configurations

### 3. **Real-Time Analysis**
- Live progress updates
- Streaming results
- Cancel button
- Time estimation

### 4. **Visualizations**
```python
# Charts to include:
1. Bar chart: Question frequency by group
2. Pie chart: Question distribution
3. Heatmap: Similarity matrix
4. Timeline: Questions over time
5. Word cloud: Common keywords
6. Network graph: Question relationships
```

### 5. **Interactive Results**
- Expandable question groups
- Search/filter questions
- Sort by frequency, similarity, date
- Click to see full question details
- Highlight similar questions

### 6. **Export Options**
- JSON (raw data)
- CSV (spreadsheet)
- Excel (formatted)
- PDF (report with charts)
- Markdown (documentation)

### 7. **Settings Panel**
- API key management
- Model selection
- Performance tuning
- Cache management
- Theme selection (light/dark)

---

## Page Structure

### Page 1: Home/Upload
- Welcome message
- Quick start guide
- File upload
- Recent analyses

### Page 2: Analysis
- Configuration
- Run analysis
- Progress tracking
- Results preview

### Page 3: Results
- Summary statistics
- Visualizations
- Question groups
- Export options

### Page 4: Settings
- API configuration
- Performance settings
- Cache management
- About/Help

---

## Implementation Plan

### Phase 1: Basic Streamlit App (4-6 hours)

**File**: `dashboard/app.py`

```python
import streamlit as st
import pandas as pd
import plotly.express as px
from src.analyzer import QuestionAnalyzer

st.set_page_config(
    page_title="Slack Question Analyzer",
    page_icon="🔍",
    layout="wide"
)

# Sidebar
with st.sidebar:
    st.title("⚙️ Settings")
    provider = st.selectbox("AI Provider", ["ollama", "azure", "openai"])
    threshold = st.slider("Similarity Threshold", 0.0, 1.0, 0.85)
    
# Main area
st.title("🔍 Slack Question Analyzer")

uploaded_file = st.file_uploader("Upload Slack Export", type=['txt', 'json', 'csv'])

if uploaded_file:
    if st.button("🚀 Analyze Questions"):
        with st.spinner("Analyzing questions..."):
            # Run analysis
            analyzer = QuestionAnalyzer(provider=provider)
            results = analyzer.analyze_slack_content(uploaded_file.read().decode())
            
            # Display results
            col1, col2, col3, col4 = st.columns(4)
            col1.metric("Total Questions", results['total_questions'])
            col2.metric("Groups Found", results['total_groups'])
            col3.metric("Unique Questions", len(results['ungrouped_questions']))
            col4.metric("Avg Similarity", f"{results['metadata']['similarity_threshold']:.0%}")
            
            # Chart
            st.subheader("📊 Question Frequency")
            chart_data = pd.DataFrame([
                {'Group': g['representative_question'][:50], 'Count': g['count']}
                for g in results['groups'][:10]
            ])
            fig = px.bar(chart_data, x='Count', y='Group', orientation='h')
            st.plotly_chart(fig, use_container_width=True)
            
            # Groups
            st.subheader("🔍 Question Groups")
            for i, group in enumerate(results['groups'], 1):
                with st.expander(f"Group {i}: {group['representative_question'][:80]} ({group['count']} questions)"):
                    st.write(f"**Keywords**: {', '.join(group['keywords'])}")
                    st.write(f"**Similarity**: {group['avg_similarity']:.0%}")
                    st.write("**Questions**:")
                    for q in group['questions']:
                        st.write(f"- {q['text']}")
```

### Phase 2: Enhanced Features (6-8 hours)
- Add more visualizations
- Implement export functionality
- Add search/filter
- Improve styling
- Add caching

### Phase 3: Advanced Features (8-10 hours)
- Real-time updates
- Question comparison
- Trend analysis
- User authentication
- Database storage

---

## Wireframes

### Mobile View
```
┌─────────────┐
│ ☰  Settings │
├─────────────┤
│ 📁 Upload   │
│ [Browse]    │
├─────────────┤
│ ⚙️ Config   │
│ Provider: ▼ │
│ Threshold:  │
│ ━━━━━━━━━  │
├─────────────┤
│ [Analyze]   │
├─────────────┤
│ 📊 Results  │
│ Total: 49   │
│ Groups: 8   │
├─────────────┤
│ 📈 Chart    │
│ [View Full] │
└─────────────┘
```

### Tablet/Desktop View
```
┌────────────────────────────────────────┐
│ Sidebar    │ Main Content              │
│            │                            │
│ Settings   │ Upload & Configure         │
│ Provider   │ ┌────────────────────┐    │
│ Threshold  │ │ Drag & Drop        │    │
│            │ └────────────────────┘    │
│ [Analyze]  │                            │
│            │ Results Dashboard          │
│ History    │ ┌──────┬──────┬──────┐   │
│ - Run 1    │ │ 49   │ 8    │ 7    │   │
│ - Run 2    │ └──────┴──────┴──────┘   │
│            │                            │
│ Export     │ Charts & Groups            │
│ [JSON]     │ ████████████              │
│ [CSV]      │ ██████████                │
│ [Excel]    │ ████████                  │
└────────────────────────────────────────┘
```

---

## Color Scheme

### Light Mode
- Primary: #4A90E2 (Blue)
- Secondary: #50C878 (Green)
- Background: #FFFFFF
- Text: #333333
- Accent: #FF6B6B (Red for alerts)

### Dark Mode
- Primary: #64B5F6
- Secondary: #81C784
- Background: #1E1E1E
- Text: #E0E0E0
- Accent: #FF8A80

---

## Dependencies

```python
# dashboard/requirements.txt
streamlit>=1.28.0
plotly>=5.17.0
pandas>=2.0.0
altair>=5.1.0  # Alternative charting
streamlit-aggrid>=0.3.4  # Interactive tables
streamlit-option-menu>=0.3.6  # Better navigation
```

---

## Deployment Options

### 1. **Streamlit Cloud** (Easiest)
- Free hosting
- Auto-deploy from GitHub
- HTTPS included
- URL: `your-app.streamlit.app`

### 2. **Docker** (Flexible)
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
EXPOSE 8501
CMD ["streamlit", "run", "dashboard/app.py"]
```

### 3. **Heroku/Railway** (Simple)
- One-click deploy
- Custom domain
- Scalable

---

## Security Considerations

1. **API Key Protection**
   - Never expose keys in UI
   - Use environment variables
   - Encrypt stored keys

2. **File Upload Validation**
   - Check file size limits
   - Validate file types
   - Scan for malicious content

3. **Rate Limiting**
   - Limit analyses per user
   - Prevent abuse
   - Queue long-running tasks

4. **Authentication** (Optional)
   - User login
   - Role-based access
   - Usage tracking

---

## Success Metrics

- **Performance**: Page load < 2s, Analysis < 30s
- **Usability**: 90% task completion rate
- **Reliability**: 99% uptime
- **Adoption**: 50+ active users in first month

---

## Next Steps

1. **Week 1**: Build basic Streamlit app (Phase 1)
2. **Week 2**: Add visualizations and export (Phase 2)
3. **Week 3**: Polish and deploy (Phase 3)
4. **Week 4**: Gather feedback and iterate

**Total Time**: 3-4 weeks part-time
**Result**: Production-ready web dashboard

---

## Alternative: Quick Prototype (2 hours)

For immediate testing, use Gradio:

```python
import gradio as gr
from src.analyzer import QuestionAnalyzer

def analyze(file, provider, threshold):
    analyzer = QuestionAnalyzer(provider=provider)
    results = analyzer.analyze_slack_content(file.decode())
    return results

demo = gr.Interface(
    fn=analyze,
    inputs=[
        gr.File(label="Upload Slack Export"),
        gr.Dropdown(["ollama", "azure", "openai"], label="Provider"),
        gr.Slider(0, 1, 0.85, label="Threshold")
    ],
    outputs=gr.JSON(label="Results"),
    title="Slack Question Analyzer"
)

demo.launch()
```

This gives you a working UI in 30 minutes!