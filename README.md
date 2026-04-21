# Syllabus-Navigator-Final-Project
### An Agentic Academic Compliance Auditor

**Udit Chaturvedi · INFO 7375 Prompt Engineering for Generative AI · Northeastern University · Spring 2026**

---

## What It Does

The Syllabus Navigator audits university course syllabi against official academic policies to detect compliance violations — what the project calls **"silent failures."**

A silent failure is an error in an academic document that no one catches until it causes real harm: a student loses marks because a due date listed as "Thursday, October 12th" is actually a Wednesday, or a TA applies the wrong grading scale because the syllabus contradicts the university standard.

This system solves that problem by combining two AI techniques:
- **RAG (Retrieval-Augmented Generation):** Retrieves the most relevant policy chunks before auditing, grounding the model's analysis in verified source documents
- **Prompt Engineering:** A carefully designed audit prompt instructs Gemini to act as a compliance auditor with specific rules, structured output format, and severity ratings

---

## Results

| Metric | Value |
|--------|-------|
| Courses audited | 6 |
| Total flags raised | 34 |
| Confirmed real issues | 21 |
| Recall per course | **100%** |
| Overall precision | 61.8% |

**Every real issue was found. Zero real violations were missed.**

---

## Key Findings

1. **DAMG 6210** — Grading scale conflict: syllabus awards A at 94%+, university policy requires 95%+. Direct GPA impact.
2. **INFO 6105** — Entire course schedule uses Fall 2024 dates in a Spring 2025 syllabus. All 15 weeks misaligned.
3. **INFO 6150** — Class scheduled on 03/03/2025, which is Spring Break. University policy: no classes that week.
4. **INFO 7374** — Week 9 dated 3/4/2025, directly within Spring Break period.
5. **CSYE 7280** — Header reads "Fall 2024" while schedule shows Spring 2025 dates.
6. **INFO 7375** — Late work policy (5%/day deduction) directly contradicts university standard (no credit without prior communication).

---

## Tech Stack

- **Language:** Python 3.12
- **Environment:** Google Colab
- **LLM:** Gemini 2.0 Flash (`gemini-2.0-flash`)
- **Embeddings:** Google `text-embedding-004`
- **Framework:** LangChain
- **PDF Reading:** pypdf
- **Vector Store:** FAISS (Facebook AI Similarity Search)
Note: FAISS (Facebook AI Similarity Search) is used as the vector database. 
While the rubric suggests Pinecone, Weaviate, or Milvus, FAISS provides 
equivalent functionality for local deployment without requiring a cloud database subscription.


---

## Project Structure

```
syllabus-navigator/
│
├── Syllabus_Navigator.ipynb    # Main notebook — run this
│
├── syllabi/                    # Input documents
│   ├── 31754-UIUX.pdf
│   ├── 31876-WEBD.pdf
│   ├── 34365-DMDD.pdf
│   ├── 37910-Prompt.pdf
│   ├── 40302-DSEM.pdf
│   └── 41097-ORM.pdf
│
├── index.html                  # Project web page
└── README.md
```

---

## Setup Instructions

### 1. Open in Google Colab
Upload `Syllabus_Navigator.ipynb` to [colab.research.google.com](https://colab.research.google.com)

### 2. Get a Gemini API Key
Go to [aistudio.google.com](https://aistudio.google.com), sign in, click **Get API key** → **Create API key in new project**

### 3. Add the Key to Colab Secrets
In Colab, click the 🔑 (Secrets) icon in the left sidebar → **Add new secret**
- Name: `GEMINI_API_KEY`
- Value: your API key
- Toggle notebook access ON

### 4. Upload the Syllabus PDFs
Run Cell 3 — a file picker will appear. Upload all 6 PDFs from the `syllabi/` folder.

### 5. Run All Cells
`Runtime → Run all` — the full audit takes approximately 2–3 minutes.

---

## How It Works

```
PDF Syllabi → Text Extraction → Chunking (500 chars, 50 overlap)
                                      ↓
                              Vector Embeddings (text-embedding-004)
                                      ↓
                              FAISS Vector Store
                                      ↓
          Policy Knowledge Base → RAG Retrieval (top 5 chunks)
                                      ↓
                         Gemini 2.0 Flash Audit Prompt
                                      ↓
                    Structured Discrepancy Report + Recall Metrics
```

---

## Evaluation

Performance is measured using **Retrieval Recall** — the fraction of real issues a human reviewer found that the system also found.

Ground truth was established by manually reviewing all 6 syllabi and identifying every genuine compliance issue, independent of what the system flagged.

**Result: 100% recall per course.** The system never missed a real problem.

The 13 false positives share a single root cause: the 6,000-character context window truncates policies that appear later in longer documents. This is a documented, fixable limitation — increasing context window size would eliminate most false positives.

---

## Ethical Considerations

- All syllabi used are real but publicly distributed university documents
- No student data is processed — only instructor-facing policy documents
- The system flags issues for human review; it does not make final determinations
- API calls are made via private key; no document content is used for model training
- This system processes only publicly distributed institutional documents. No student records, personal data, or user-generated content is collected, stored, or transmitted at any point.

---

## Future Improvements

1. Increase context window to full document length to reduce false positives
2. Add university academic calendar as a structured data source for date verification
3. Build a Streamlit web interface for non-technical users
4. Extend to multi-university policy comparison
5. Add fine-tuned evaluation rubric per course type

---
## What This Notebook Does
## Live Demo

Try the interactive auditor here:
**https://syllabus-navigator-final-project-evhm5vjugwk6eneunzxapr.streamlit.app/**

Upload any university syllabus PDF and see compliance flags generated in real time.
