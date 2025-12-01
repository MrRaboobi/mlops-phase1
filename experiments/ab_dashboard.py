from pathlib import Path
import streamlit as st
from io import StringIO
import pandas as pd

# -------------------------
# Paths
# -------------------------
PROJECT_ROOT = Path(__file__).resolve().parents[1]
REPORT_PATH = PROJECT_ROOT / "experiments" / "prompt_report.md"

# -------------------------
# Page Config
# -------------------------
st.set_page_config(
    page_title="Prompt Strategy Evaluation Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# -------------------------
# Custom CSS Styling
# -------------------------
st.markdown(
    """
    <style>
        /* Main container adjustments */
        .main {
            padding: 2rem;
        }

        /* Header styling */
        .title {
            font-size: 2.8rem !important;
            font-weight: 700 !important;
            color: #4F8BF9 !important;
        }

        /* Subheaders */
        .subheader {
            font-size: 1.6rem !important;
            font-weight: 600;
            margin-top: 1.5rem;
            color: #ffffffcc;
        }

        /* Metric cards */
        .metric-card {
            padding: 1rem 1.5rem;
            border-radius: 12px;
            background: #1f2937;
            color: white;
            box-shadow: 0px 4px 12px rgba(0,0,0,0.3);
        }

        .metric-value {
            font-size: 2rem;
            font-weight: 700;
            color: #4F8BF9;
        }

        .metric-label {
            font-size: 1rem;
            font-weight: 500;
            opacity: 0.8;
        }

        /* Markdown improvements */
        .report-markdown h1, .report-markdown h2, .report-markdown h3 {
            color: #4F8BF9 !important;
        }

        .report-markdown table {
            margin-top: 1rem;
        }

        /* Bullet styles */
        ul {
            margin-left: 1.2rem;
        }
    </style>
""",
    unsafe_allow_html=True,
)


# -------------------------
# Title
# -------------------------
st.markdown(
    "<div class='title'>📊 Prompt Strategy A/B Evaluation Dashboard</div>",
    unsafe_allow_html=True,
)

st.write(
    "Compare the performance of Zero-Shot, Few-Shot, and Chain-of-Thought (CoT) prompting strategies "
    "for ECG explanation generation."
)

st.markdown("---")

# -------------------------
# Read Report
# -------------------------
if REPORT_PATH.exists():
    report_text = REPORT_PATH.read_text()
else:
    st.error("⚠️ No report found. Run `python experiments/eval.py` first.")
    st.stop()

# -------------------------
# Parse Metrics from Report
# ------------------------


def extract_table(md_text):
    lines = md_text.splitlines()
    table = []
    start = False
    for line in lines:
        if line.strip().startswith("| Strategy"):
            start = True
        if start:
            table.append(line)
        if start and line.strip() == "":
            break
    return "\n".join(table)


table_md = extract_table(report_text)

df = pd.read_csv(StringIO(table_md.replace("|", ",")))

# Clean column names (VERY IMPORTANT)
df.columns = df.columns.str.strip()

st.write("Columns detected:", df.columns.tolist())

# -------------------------
# Metric Cards (Top KPIs)
# -------------------------
st.markdown("<div class='subheader'>🔥 Key Results</div>", unsafe_allow_html=True)

col1, col2 = st.columns(2)

best_helpfulness = df.loc[df["Helpfulness (1-5)"].idxmax()]
best_factuality = df.loc[df["Factuality (1-5)"].idxmax()]


with col1:
    st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
    st.markdown(
        f"<div class='metric-value'>{best_helpfulness['Strategy']}</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<div class='metric-label'>🏆 Highest Helpfulness Score</div>",
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

with col2:
    st.markdown("<div class='metric-card'>", unsafe_allow_html=True)
    st.markdown(
        f"<div class='metric-value'>{best_factuality['Strategy']}</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<div class='metric-label'>📘 Highest Factuality Score</div>",
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)

st.markdown("---")

# -------------------------
# Full Report
# -------------------------
st.markdown(
    "<div class='subheader'>📑 Full Prompt Evaluation Report</div>",
    unsafe_allow_html=True,
)

with st.expander("Show Report"):
    st.markdown(
        f"<div class='report-markdown'>{report_text}</div>", unsafe_allow_html=True
    )

st.markdown("---")

# -------------------------
# Table
# -------------------------
st.markdown(
    "<div class='subheader'>📊 Detailed Comparison Table</div>", unsafe_allow_html=True
)

st.dataframe(df.style.highlight_max(axis=0, color="#4F8BF966"))

# -------------------------
# Footer
# -------------------------
st.markdown(
    """
<hr>
<center>Built for <b>HEARTSIGHT - ECG Intelligence Platform</b></center>
""",
    unsafe_allow_html=True,
)
