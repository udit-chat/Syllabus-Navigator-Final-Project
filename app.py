import streamlit as st
import os
import time
from pypdf import PdfReader

st.set_page_config(
    page_title="Syllabus Navigator",
    page_icon="📋",
    layout="wide"
)

st.markdown("""
    <style>
    .flag-high { background-color: #fef2ee; border-left: 4px solid #c8401a; padding: 12px 16px; margin: 8px 0; border-radius: 4px; color: #0f0e0c; }
    .flag-med  { background-color: #fefaee; border-left: 4px solid #b8900a; padding: 12px 16px; margin: 8px 0; border-radius: 4px; color: #0f0e0c; }
    .flag-low  { background-color: #f0f8f0; border-left: 4px solid #2d7a2d; padding: 12px 16px; margin: 8px 0; border-radius: 4px; color: #0f0e0c; }
    .tag-high  { background-color: #c8401a; color: white; padding: 2px 8px; border-radius: 3px; font-size: 11px; font-weight: bold; }
    .tag-med   { background-color: #b8900a; color: white; padding: 2px 8px; border-radius: 3px; font-size: 11px; font-weight: bold; }
    .tag-low   { background-color: #2d7a2d; color: white; padding: 2px 8px; border-radius: 3px; font-size: 11px; font-weight: bold; }
    .summary-box { background-color: #f5f2eb; padding: 20px; border-radius: 8px; margin: 16px 0; color: #0f0e0c; }
</style>
""", unsafe_allow_html=True)

st.title("📋 Syllabus Navigator")
st.markdown("**An Agentic Academic Compliance Auditor** — Upload a syllabus PDF to detect compliance violations automatically.")
st.markdown("---")

POLICY_TEXT = """
NORTHEASTERN UNIVERSITY MGEN PROGRAM - ACADEMIC POLICIES

Late Work Policy:
Students must submit assignments by the deadline in the time zone noted in the syllabus.
Students must communicate with the faculty prior to the deadline if they anticipate work will be submitted late.
Work submitted late without prior communication with faculty will not be graded.
No credit is given for late work submitted without prior faculty communication.

Attendance Policy:
Students are allowed a maximum of 2 absences per course.
Three or more absences result in an automatic F for that course.
Students must inform instructors of absences in advance.

Academic Calendar Spring 2026:
Spring Break is the week of March 2, 2026. No classes during Spring Break.
Classes begin January 5, 2026.
The semester ends in late April 2026.

Weekend Policy:
Classes are not held on weekends - Saturday or Sunday.
Assignment deadlines falling on weekends should be noted as potential scheduling issues.

Grading Transparency Policy:
All assignment weights and due dates must be clearly specified in the syllabus.
Grading breakdowns must sum to 100%.
"""

def extract_text(pdf_file):
    reader = PdfReader(pdf_file)
    text = ""
    for page in reader.pages:
        text += page.extract_text() + "\n"
    return text

def chunk_text(text, chunk_size=500, overlap=50):
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap
    return chunks

def build_vector_store(chunks):
    from langchain_google_genai import GoogleGenerativeAIEmbeddings
    from langchain_community.vectorstores import FAISS
    from langchain_core.documents import Document
    docs = [Document(page_content=chunk) for chunk in chunks]
    embeddings = GoogleGenerativeAIEmbeddings(
    model="models/gemini-embedding-001",
    google_api_key=os.environ["GOOGLE_API_KEY"]
)
    return FAISS.from_documents(docs, embeddings)

def audit_syllabus(syllabus_text, vector_store, course_name):
    from langchain_google_genai import ChatGoogleGenerativeAI
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=os.environ["GOOGLE_API_KEY"],
        temperature=0
    )
    relevant_chunks = vector_store.similarity_search(
        "late work policy attendance deadline grading", k=5
    )
    rag_context = "\n".join([doc.page_content for doc in relevant_chunks])
    prompt = f"""
You are a strict academic compliance auditor for Northeastern University.
Your job is to audit a course syllabus against official university policies.

OFFICIAL UNIVERSITY POLICIES:
{POLICY_TEXT}

ADDITIONAL CONTEXT FROM POLICY KNOWLEDGE BASE (via RAG retrieval):
{rag_context}

SYLLABUS TO AUDIT ({course_name}):
{syllabus_text[:6000]}

Carefully analyze the syllabus and identify ANY of these issues:
1. MISSING INFO: Required fields not present (late work policy, attendance policy, grading breakdown)
2. POLICY CONFLICT: Syllabus rules that contradict university policies
3. DATE ISSUE: Suspicious dates (wrong semester, weekend deadlines, missing dates)
4. GRADING ISSUE: Grading weights that don't add up to 100%, or vague grading descriptions

For each issue found, respond in this exact format:
FLAG [number]: [ISSUE TYPE]
Description: [What exactly is wrong]
Location: [Where in the syllabus this appears]
Severity: [HIGH / MEDIUM / LOW]
---

If no issues are found, write: NO FLAGS FOUND

Be specific. Be critical. Do not make up issues that don't exist.
"""
    response = llm.invoke(prompt)
    return response.content

def parse_flags(audit_text):
    flags = []
    blocks = audit_text.strip().split("---")
    for block in blocks:
        block = block.strip()
        if not block or "NO FLAGS FOUND" in block:
            continue
        lines = block.split("\n")
        flag = {"type": "", "description": "", "location": "", "severity": "LOW", "raw": block}
        for line in lines:
            if line.startswith("FLAG"):
                flag["type"] = line.strip()
            elif line.startswith("Description:"):
                flag["description"] = line.replace("Description:", "").strip()
            elif line.startswith("Location:"):
                flag["location"] = line.replace("Location:", "").strip()
            elif line.startswith("Severity:"):
                flag["severity"] = line.replace("Severity:", "").strip()
        if flag["description"]:
            flags.append(flag)
    return flags

def render_flag(flag):
    sev = flag["severity"].upper()
    if sev == "HIGH":
        css_class = "flag-high"
        tag_class = "tag-high"
    elif sev == "MEDIUM":
        css_class = "flag-med"
        tag_class = "tag-med"
    else:
        css_class = "flag-low"
        tag_class = "tag-low"

    st.markdown(f"""
    <div class="{css_class}">
        <span class="{tag_class}">{sev}</span>
        <strong style="margin-left:8px">{flag['type']}</strong><br>
        <span style="font-size:14px">{flag['description']}</span><br>
        <span style="font-size:12px; color:#7a7670">📍 {flag['location']}</span>
    </div>
    """, unsafe_allow_html=True)

# ── SIDEBAR ──
with st.sidebar:
    st.markdown("### About")
    st.markdown("Built by **Udit Chaturvedi**")
    st.markdown("INFO 7375 — Northeastern University")
    st.markdown("Spring 2026")
    st.markdown("---")
    st.markdown("### How it works")
    st.markdown("1. Upload a syllabus PDF")
    st.markdown("2. System chunks and embeds the text (RAG)")
    st.markdown("3. Gemini 2.5 Flash audits against policy")
    st.markdown("4. Flags appear with severity ratings")
    st.markdown("---")
    st.markdown("### Tech stack")
    st.markdown("- Gemini 2.5 Flash")
    st.markdown("- text-embedding-004")
    st.markdown("- FAISS vector store")
    st.markdown("- LangChain")
    st.markdown("- pypdf")

# ── MAIN ──
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("Upload Syllabus")
    uploaded_file = st.file_uploader(
        "Choose a PDF file",
        type="pdf",
        help="Upload any university course syllabus PDF"
    )
    course_name = st.text_input(
        "Course name (optional)",
        placeholder="e.g. CSYE 7280 — UX Design",
        value=""
    )
    audit_button = st.button("🔍 Audit Syllabus", type="primary", use_container_width=True)

with col2:
    st.subheader("What gets checked")
    st.markdown("""
    | Issue Type | Example |
    |-----------|---------|
    | **Missing Info** | No late work policy present |
    | **Policy Conflict** | Grading scale contradicts university standard |
    | **Date Issue** | Class scheduled during Spring Break |
    | **Grading Issue** | Weights don't sum to 100% |
    """)

st.markdown("---")

if audit_button and uploaded_file:
    name = course_name if course_name else uploaded_file.name.replace(".pdf", "")

    with st.spinner("Reading PDF..."):
        text = extract_text(uploaded_file)
        st.success(f"Extracted {len(text):,} characters from {len(PdfReader(uploaded_file).pages)} pages")

    with st.spinner("Building vector store (RAG)..."):
        try:
            chunks = chunk_text(text)
            vector_store = build_vector_store(chunks)
            st.success(f"Indexed {len(chunks)} chunks into FAISS vector store")
        except Exception as e:
            st.error(f"""
            **Failed to build vector store.**
            This usually means the API key is invalid or the embedding quota is exceeded.
            Error: {str(e)[:200]}
            """)
            st.stop()

    with st.spinner("Auditing against policy knowledge base... (this takes 30-60 seconds)"):
        start = time.time()
        try:
            audit_result = audit_syllabus(text, vector_store, name)
            elapsed = round(time.time() - start, 1)
        except Exception as e:
            error_msg = str(e).lower()
            if "quota" in error_msg or "429" in error_msg or "resource_exhausted" in error_msg:
                st.error("""
                **API quota exceeded.**
                The free tier Gemini API allows a limited number of requests per day.
                Please wait a few minutes and try again, or try with a shorter document.
                """)
            elif "api_key" in error_msg or "authentication" in error_msg:
                st.error("""
                **API key error.**
                The Gemini API key is missing or invalid.
                Please check the app configuration.
                """)
            else:
                st.error(f"""
                **Something went wrong during the audit.**
                Error: {str(e)[:200]}
                Please try again or use a different PDF.
                """)
            st.stop()

    flags = parse_flags(audit_result)
    high = sum(1 for f in flags if f["severity"].upper() == "HIGH")
    med  = sum(1 for f in flags if f["severity"].upper() == "MEDIUM")
    low  = sum(1 for f in flags if f["severity"].upper() == "LOW")

    st.subheader(f"Audit Results — {name}")
    st.markdown(f"""
    <div class="summary-box">
        <strong>Total flags: {len(flags)}</strong> &nbsp;|&nbsp;
        <span class="tag-high">HIGH: {high}</span> &nbsp;
        <span class="tag-med">MEDIUM: {med}</span> &nbsp;
        <span class="tag-low">LOW: {low}</span> &nbsp;|&nbsp;
        Completed in {elapsed}s
    </div>
    """, unsafe_allow_html=True)

    if flags:
        for flag in flags:
            render_flag(flag)
    else:
        st.success("No compliance issues found.")

elif audit_button and not uploaded_file:
    st.warning("Please upload a PDF file first.")

st.markdown("---")
st.markdown(
    "<div style='text-align:center; color:#7a7670; font-size:12px'>"
    "Syllabus Navigator · Udit Chaturvedi · INFO 7375 · Northeastern University · Spring 2026"
    "</div>",
    unsafe_allow_html=True
)
