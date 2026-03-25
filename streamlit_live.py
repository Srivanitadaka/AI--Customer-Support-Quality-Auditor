import os
import sys
import json
import time
import tempfile
import threading
from pathlib import Path
from datetime import datetime

import streamlit as st
import plotly.graph_objects as go

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

# ── Page config ────────────────────────────────────────
st.set_page_config(
    page_title = "CallAudit Pro — Live",
    page_icon  = "🎧",
    layout     = "wide",
)

# ── Custom CSS ──────────────────────────────────────────
st.markdown("""
<style>
  [data-testid="stAppViewContainer"] { background:#080c14; color:#e2e8f0; }
  [data-testid="stSidebar"]          { background:#0d1320; border-right:1px solid #1e293b; }
  [data-testid="stSidebar"] * { color:#e2e8f0 !important; }
  h1,h2,h3 { color:#38bdf8 !important; }
  .stButton button {
    background:#38bdf8; color:#080c14;
    font-weight:800; border:none; border-radius:8px;
    padding:10px 24px; width:100%;
  }
  .stButton button:hover { opacity:.9; }
  .metric-card {
    background:#0d1320; border:1px solid #1e293b;
    border-radius:12px; padding:20px; text-align:center;
    margin-bottom:12px;
  }
  .viol-card {
    padding:14px; border-radius:8px; margin-bottom:8px;
    border-left:4px solid;
  }
  .critical { border-left-color:#f87171; background:rgba(248,113,113,.1); }
  .high     { border-left-color:#fb923c; background:rgba(251,146,60,.1); }
  .medium   { border-left-color:#f59e0b; background:rgba(245,158,11,.1); }
  .imp-card {
    padding:14px; border-radius:8px; margin-bottom:8px;
    border-left:4px solid #38bdf8; background:rgba(56,189,248,.08);
  }
  .transcript-box {
    background:#111827; border:1px solid #1e293b;
    border-radius:8px; padding:16px; height:300px;
    overflow-y:auto; font-family:monospace; font-size:13px;
  }
  div[data-testid="metric-container"] {
    background:#0d1320; border:1px solid #1e293b; border-radius:8px;
  }
</style>
""", unsafe_allow_html=True)


# ══════════════════════════════════════════════════════
# SESSION STATE
# ══════════════════════════════════════════════════════
if "transcript"    not in st.session_state: st.session_state.transcript    = ""
if "result"        not in st.session_state: st.session_state.result        = None
if "alerts"        not in st.session_state: st.session_state.alerts        = []
if "is_monitoring" not in st.session_state: st.session_state.is_monitoring = False
if "live_chunks"   not in st.session_state: st.session_state.live_chunks   = []


# ══════════════════════════════════════════════════════
# HELPERS
# ══════════════════════════════════════════════════════
def score_color(v, mx=100):
    p = v / mx
    if p >= 0.75: return "#22c55e"
    if p >= 0.55: return "#f59e0b"
    return "#f87171"

GRADE_C = {
    "A": "#22c55e", "B": "#38bdf8",
    "C": "#f59e0b", "D": "#fb923c", "F": "#f87171"
}

def load_env():
    from dotenv import load_dotenv
    load_dotenv(ROOT / "config" / ".env")

def analyze_transcript(text: str) -> dict:
    """Run RAG + LangChain scoring on transcript."""
    try:
        from rag_pipeline.rag_pipeline import RAGPipeline
        from llm.langchain_scorer      import score_with_langchain
        from realtime.alert_engine     import AlertEngine

        pipeline = RAGPipeline(backend="chromadb")
        pipeline.setup()
        enriched = pipeline.enrich(text)
        result   = score_with_langchain(enriched)

        if result:
            alert_engine = AlertEngine(socketio=None)
            alerts       = alert_engine.check_and_alert(result, text)
            result["compliance_alerts"] = alerts or []

        return result

    except Exception as e:
        st.error(f"Scoring failed: {e}")
        return None

def transcribe_audio(file_path: str) -> str:
    """Transcribe audio file using Deepgram."""
    try:
        from transcription.deepgram_processor import process_call_transcript
        return process_call_transcript(file_path)
    except Exception as e:
        st.error(f"Transcription failed: {e}")
        return ""


# ══════════════════════════════════════════════════════
# SIDEBAR
# ══════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("## 🎧 CallAudit Pro")
    st.markdown("**Live Analysis**")
    st.divider()

    mode = st.radio(
        "Mode",
        ["📁 Upload Audio", "🎤 Live Mic"],
        index = 0
    )

    st.divider()

    if mode == "📁 Upload Audio":
        st.markdown("### Upload Audio File")
        audio_file = st.file_uploader(
            "Drag and drop file here",
            type    = ["mp3", "wav", "m4a", "flac"],
            help    = "Limit 200MB per file"
        )

        if audio_file and st.button("🔍 Analyze Call"):
            with st.spinner("Transcribing audio..."):
                # Save to temp file
                suffix = Path(audio_file.name).suffix
                tmp    = tempfile.NamedTemporaryFile(
                    suffix=suffix, delete=False
                )
                tmp.write(audio_file.read())
                tmp.close()

                transcript = transcribe_audio(tmp.name)
                os.unlink(tmp.name)

            if transcript:
                st.session_state.transcript = transcript
                with st.spinner("Scoring with AI..."):
                    result = analyze_transcript(transcript)
                    if result:
                        st.session_state.result  = result
                        st.session_state.alerts  = result.get(
                            "compliance_alerts", []
                        )
                        st.success("✅ Analysis complete!")
            else:
                st.error("Transcription failed")

    elif mode == "🎤 Live Mic":
        st.markdown("### Live Microphone")
        st.info(
            "Click Start to begin monitoring.\n"
            "Score updates every 30 seconds."
        )

        col1, col2 = st.columns(2)
        with col1:
            start_btn = st.button("▶ Start", type="primary")
        with col2:
            stop_btn  = st.button("⏹ Stop")

        if start_btn:
            st.session_state.is_monitoring = True
            st.session_state.transcript    = ""
            st.session_state.result        = None
            st.session_state.alerts        = []
            st.success("🔴 Live monitoring started!")

        if stop_btn:
            st.session_state.is_monitoring = False
            if st.session_state.transcript:
                with st.spinner("Final scoring..."):
                    result = analyze_transcript(
                        st.session_state.transcript
                    )
                    if result:
                        st.session_state.result = result
                        st.session_state.alerts = result.get(
                            "compliance_alerts", []
                        )
            st.info("⏹ Monitoring stopped")

        if st.session_state.is_monitoring:
            st.markdown(
                "🔴 **LIVE** — speak into microphone",
                unsafe_allow_html=True
            )

    st.divider()

    # Clear button
    if st.button("🗑 Clear Results"):
        st.session_state.transcript    = ""
        st.session_state.result        = None
        st.session_state.alerts        = []
        st.session_state.is_monitoring = False
        st.rerun()


# ══════════════════════════════════════════════════════
# MAIN HEADER
# ══════════════════════════════════════════════════════
st.markdown(
    "<h1 style='font-size:32px;margin-bottom:4px'>"
    "🎧 CallAudit Pro <span style='color:#38bdf8'>Live</span></h1>",
    unsafe_allow_html=True
)
st.markdown(
    "<p style='color:#64748b;margin-bottom:24px'>"
    "AI Customer Support Quality Analyzer — Real-time scoring</p>",
    unsafe_allow_html=True
)

# ── No result yet ──────────────────────────────────────
if not st.session_state.result and not st.session_state.transcript:
    st.markdown("""
    <div style='background:#0d1320;border:1px solid #1e293b;
                border-radius:12px;padding:40px;text-align:center'>
        <div style='font-size:48px;margin-bottom:16px'>🎤</div>
        <div style='font-size:20px;font-weight:700;color:#e2e8f0'>
            Upload data or use live mode
        </div>
        <div style='color:#64748b;margin-top:8px'>
            Use the sidebar to upload an audio file
            or start live microphone monitoring
        </div>
    </div>
    <br>
    <div style='text-align:center;color:#64748b;font-size:13px'>
        🚀 AI Customer Support Quality Analyzer
    </div>
    """, unsafe_allow_html=True)

# ── Show transcript while monitoring ──────────────────
if st.session_state.is_monitoring:
    st.markdown("### 🔴 Live Transcript")
    transcript_placeholder = st.empty()
    transcript_placeholder.markdown(
        f"<div class='transcript-box'>"
        f"{st.session_state.transcript or 'Listening...'}"
        f"</div>",
        unsafe_allow_html=True
    )


# ══════════════════════════════════════════════════════
# RESULTS DASHBOARD
# ══════════════════════════════════════════════════════
if st.session_state.result:
    r     = st.session_state.result
    grade = r.get("grade", "?")
    score = r.get("overall_score", 0)
    gc    = GRADE_C.get(grade, "#64748b")
    sat   = r.get("satisfaction", {})
    dims  = r.get("dimension_scores", r.get("scores", {}))
    aq    = r.get("agent_quality", {})

    # ── Overview KPIs ──────────────────────────────────
    st.markdown("### 📊 Overall Performance")
    c1, c2, c3, c4 = st.columns(4)

    c1.metric(
        "Overall Score",
        f"{score}/100",
        delta = f"Grade {grade}"
    )
    c2.metric(
        "Satisfaction",
        f"{sat.get('rating', 0):.1f}/5"
    )
    c3.metric(
        "Call Outcome",
        r.get("call_outcome", "Unknown")
    )
    c4.metric(
        "Violations",
        len(r.get("violations", []))
    )

    st.divider()

    # ── Compliance Alerts ──────────────────────────────
    alerts = st.session_state.alerts
    if alerts:
        st.markdown(f"### 🚨 Compliance Alerts ({len(alerts)})")
        for a in alerts:
            lvl = (a.get("level") or "warning").lower()
            cls = "critical" if lvl=="critical" else "high" if lvl=="high" else "medium"
            st.markdown(
                f"<div class='viol-card {cls}'>"
                f"<strong>[{a.get('level','')}]</strong> "
                f"{a.get('message','')}"
                f"</div>",
                unsafe_allow_html=True
            )
        st.divider()

    # ── Two columns ────────────────────────────────────
    col_left, col_right = st.columns(2)

    with col_left:
        # Dimension scores radar chart
        st.markdown("### 🎯 Dimension Scores")
        DIM_LABELS = {
            "empathy":                  "Empathy",
            "professionalism":          "Professionalism",
            "compliance":               "Compliance",
            "resolution_effectiveness": "Resolution",
            "communication_clarity":    "Clarity",
        }
        dim_names = list(DIM_LABELS.values())
        dim_vals  = [dims.get(k, 0) for k in DIM_LABELS.keys()]

        fig = go.Figure()
        fig.add_trace(go.Bar(
            x           = dim_names,
            y           = dim_vals,
            marker_color= [score_color(v,10) for v in dim_vals],
            text        = [f"{v}/10" for v in dim_vals],
            textposition= "outside",
        ))
        fig.update_layout(
            plot_bgcolor  = "#0d1320",
            paper_bgcolor = "#0d1320",
            font_color    = "#e2e8f0",
            yaxis_range   = [0, 10],
            height        = 280,
            margin        = dict(l=0,r=0,t=20,b=0),
            showlegend    = False,
        )
        fig.update_xaxes(gridcolor="#1e293b")
        fig.update_yaxes(gridcolor="#1e293b")
        st.plotly_chart(fig, use_container_width=True)

    with col_right:
        # Agent quality bars
        st.markdown("### 👔 Agent Quality")
        metrics = [
            ("Language Clarity",    aq.get("language_clarity",   0), 20),
            ("Professionalism",     aq.get("professionalism",    0), 20),
            ("Time Efficiency",     aq.get("time_efficiency",    0), 20),
            ("Response Efficiency", aq.get("response_efficiency",0), 20),
            ("Empathy Score",       aq.get("empathy_score",      0), 10),
        ]
        for label, val, mx in metrics:
            col_a, col_b = st.columns([3,1])
            col_a.markdown(
                f"<div style='font-size:12px;color:#94a3b8;"
                f"margin-bottom:4px'>{label}</div>",
                unsafe_allow_html=True
            )
            col_b.markdown(
                f"<div style='font-size:12px;color:{score_color(val,mx)};"
                f"text-align:right'>{val}/{mx}</div>",
                unsafe_allow_html=True
            )
            st.progress(int(val/mx*100))

    st.divider()

    # ── Violations + Improvements ──────────────────────
    col_v, col_i = st.columns(2)

    with col_v:
        viols = r.get("violations", [])
        st.markdown(f"### ⚠ Violations ({len(viols)})")
        if viols:
            for v in viols:
                sev = (v.get("severity") or "medium").lower()
                cls = "critical" if sev=="critical" else "high" if sev=="high" else "medium"
                st.markdown(
                    f"<div class='viol-card {cls}'>"
                    f"<strong>{(v.get('type') or '').replace('_',' ').title()}</strong>"
                    f"<span style='font-size:10px;margin-left:8px;"
                    f"color:#94a3b8'>[{sev.upper()}]</span><br>"
                    f"<span style='font-size:12px;color:#94a3b8'>"
                    f"{v.get('explanation','')[:120]}</span>"
                    f"{f'<br><em style=chr(34)color:#f87171;font-size:11px{chr(34)}>{v.get(chr(39)quote{chr(39)},chr(34){chr(34)})[:80]}</em>' if v.get('quote') else ''}"
                    f"</div>",
                    unsafe_allow_html=True
                )
        else:
            st.success("✅ No violations detected")

    with col_i:
        imps = r.get("improvements", [])
        st.markdown(f"### 💡 Improvements ({len(imps)})")
        if imps:
            for i in imps:
                st.markdown(
                    f"<div class='imp-card'>"
                    f"<strong style='color:#38bdf8;font-size:11px'>"
                    f"{(i.get('area') or '').replace('_',' ').upper()}</strong><br>"
                    f"<span style='font-size:13px'>{i.get('suggestion','')[:150]}</span>"
                    f"{'<br><em style=chr(34)color:#64748b;font-size:11px{chr(34)}>💬 ' + i.get('example','')[:100] + '</em>' if i.get('example') else ''}"
                    f"</div>",
                    unsafe_allow_html=True
                )
        else:
            st.success("✅ No improvements needed")

    st.divider()

    # ── Summary ────────────────────────────────────────
    st.markdown("### 📝 AI Summary")
    st.info(r.get("summary", "No summary available"))

    # ── Transcript viewer ──────────────────────────────
    if st.session_state.transcript:
        with st.expander("📄 View Transcript"):
            lines = st.session_state.transcript.split("\n")
            for line in lines:
                if line.strip():
                    if line.lower().startswith("agent:"):
                        st.markdown(
                            f"<div style='background:#0d1f30;"
                            f"border-left:3px solid #38bdf8;"
                            f"padding:8px;margin:4px 0;border-radius:4px;"
                            f"font-size:13px'>"
                            f"<strong style='color:#38bdf8'>Agent</strong> "
                            f"{line[6:]}</div>",
                            unsafe_allow_html=True
                        )
                    elif line.lower().startswith("customer:"):
                        st.markdown(
                            f"<div style='background:#1a1020;"
                            f"border-left:3px solid #a78bfa;"
                            f"padding:8px;margin:4px 0;border-radius:4px;"
                            f"font-size:13px'>"
                            f"<strong style='color:#a78bfa'>Customer</strong> "
                            f"{line[9:]}</div>",
                            unsafe_allow_html=True
                        )
                    else:
                        st.markdown(
                            f"<div style='font-size:13px;color:#64748b;"
                            f"padding:4px 0'>{line}</div>",
                            unsafe_allow_html=True
                        )

    # ── Download buttons ───────────────────────────────
    st.divider()
    st.markdown("### ⬇ Download Reports")
    dl1, dl2 = st.columns(2)

    with dl1:
        try:
            from reports.pdf_report import generate_pdf
            pdf_bytes = generate_pdf(
                r, filename="live_analysis.json"
            )
            st.download_button(
                label     = "⬇ Download PDF Report",
                data      = pdf_bytes,
                file_name = f"callaudit_report_{datetime.now().strftime('%Y%m%d_%H%M')}.pdf",
                mime      = "application/pdf"
            )
        except Exception as e:
            st.warning(f"PDF not available: {e}")

    with dl2:
        try:
            result_json = json.dumps(r, indent=2)
            st.download_button(
                label     = "⬇ Download JSON",
                data      = result_json,
                file_name = f"callaudit_{datetime.now().strftime('%Y%m%d_%H%M')}.json",
                mime      = "application/json"
            )
        except Exception as e:
            st.warning(f"JSON not available: {e}")