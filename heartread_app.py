"""
HeartRead 💕 — AI Relationship Signal Analyzer
Powered by Groq (FREE API) — llama3-70b model

Setup:
    1. pip install streamlit groq python-dotenv
    2. Get free API key at console.groq.com
    3. Create .env file:  GROQ_API_KEY=your-key-here
    4. streamlit run heartread_app.py
"""

import streamlit as st
import os
import json
from datetime import datetime
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

# ── Page config ────────────────────────────────────────────────────────────
st.set_page_config(page_title="HeartRead 💕", page_icon="💕", layout="centered")

st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700;900&family=Crimson+Pro:ital,wght@0,300;0,400;1,300&display=swap');

html, body, [class*="css"] { background-color: #0C0810; color: #E8DDD5; }
.stApp { background-color: #0C0810; }
h1,h2,h3 { font-family:'Playfair Display',serif!important; color:#E8DDD5!important; }
p,label,div,span,li { font-family:'Crimson Pro',Georgia,serif!important; }

.stTextArea textarea,.stTextInput input {
    background-color:#130d10!important; border:1px solid #3a2030!important;
    color:#E8DDD5!important; font-family:'Crimson Pro',Georgia,serif!important;
    font-size:16px!important; border-radius:12px!important;
}
.stSelectbox>div>div {
    background-color:#130d10!important; border:1px solid #3a2030!important;
    color:#E8DDD5!important; border-radius:12px!important;
}
.stButton>button {
    background:linear-gradient(135deg,#8B4567,#C9607A); color:white;
    border:none; border-radius:100px; padding:12px 36px;
    font-family:'Crimson Pro',Georgia,serif!important;
    font-size:16px!important; font-weight:600; width:100%;
}
.stButton>button:hover { opacity:0.85; }
.stTabs [data-baseweb="tab"] {
    font-family:'Crimson Pro',Georgia,serif!important;
    font-size:15px!important; color:#A89090!important;
}
.stTabs [aria-selected="true"] { color:#E8DDD5!important; }

.verdict-card  { border-radius:18px; padding:28px; text-align:center; margin-bottom:20px; }
.flag-chip     { display:inline-block; padding:6px 16px; border-radius:20px; margin:4px; font-size:14px!important; }
.card          { background:#130d10; border:1px solid #2a1a20; border-radius:16px; padding:20px; margin:10px 0; }
.affirmation   { text-align:center; font-style:italic; color:#C9A0A0; font-size:18px!important; margin-top:20px; }
.prog-bg       { background:#2a1a20; border-radius:4px; height:6px; margin:8px 0 20px; }
.prog-fill     { height:6px; border-radius:4px; }
.qnum          { font-size:13px!important; color:#6a4a50; letter-spacing:1px; text-transform:uppercase; margin-bottom:4px; }
.log-entry     { background:#130d10; border:1px solid #2a1a20; border-radius:12px; padding:16px; margin:8px 0; }
.msg-box       { background:#1a0d14; border:1px solid #3a2030; border-radius:14px; padding:20px; margin:10px 0; }
</style>
""", unsafe_allow_html=True)

# ── Constants ──────────────────────────────────────────────────────────────
QUESTIONS = [
    {"key":"who",      "label":"Who is this person to you?",
     "help":"e.g. my classmate, a coworker, a friend I've known 2 years..."},
    {"key":"duration", "label":"How long have you known them?",
     "help":"e.g. 6 months, 3 years, since high school..."},
    {"key":"signs",    "label":"What makes you think they might have feelings for you?",
     "help":"The moments, the looks, things they said or did..."},
    {"key":"doubt",    "label":"What makes you unsure?",
     "help":"What's creating the confusion in your mind?"},
    {"key":"last",     "label":"What was your last meaningful interaction like?",
     "help":"Describe it — what happened, how did it feel?"},
]

VERDICT_CONFIG = {
    "Likely Interested":      {"color":"#6EE7B7","bg":"#1a2e1a","border":"#2a4a2a","emoji":"💚"},
    "Mixed Signals":          {"color":"#FFD700","bg":"#2a2a1a","border":"#4a4a2a","emoji":"💛"},
    "Probably Just Friendly": {"color":"#FF8C69","bg":"#2e1a1a","border":"#4a2a2a","emoji":"🟠"},
    "Hard to Tell":           {"color":"#A78BFA","bg":"#1a1a2e","border":"#2a2a4a","emoji":"💜"},
}

MSG_TONES = ["Casual & light", "Warm & genuine", "Playful & flirty", "Bold & direct"]

MODEL = "llama-3.3-70b-versatile"  # free on Groq, very capable

# ── Session state ──────────────────────────────────────────────────────────
DEFAULTS = {
    "screen":    "intro",
    "current_q": 0,
    "answers":   {},
    "result":    None,
    "log":       [],
    "messages":  [],
}
for k, v in DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v

# ── Helpers ────────────────────────────────────────────────────────────────
def go(screen):
    st.session_state.screen = screen
    st.rerun()

def get_client():
    key = os.environ.get("GROQ_API_KEY", "")
    if not key:
        try:
            key = st.secrets["GROQ_API_KEY"]
        except Exception:
            pass
    return Groq(api_key=key)

def chat(system: str, user: str, max_tokens: int = 1024) -> str:
    client = get_client()
    resp = client.chat.completions.create(
        model=MODEL,
        max_tokens=max_tokens,
        messages=[
            {"role": "system",  "content": system},
            {"role": "user",    "content": user},
        ],
    )
    return resp.choices[0].message.content.strip()

# ── AI functions ───────────────────────────────────────────────────────────
def run_analysis(answers: dict) -> dict:
    context = "\n".join([f"{k}: {v}" for k, v in answers.items()])
    system = """You are a warm, emotionally intelligent relationship advisor.
Analyze the signals described and respond ONLY with valid JSON in this exact format:
{
  "verdict": "Likely Interested OR Mixed Signals OR Probably Just Friendly OR Hard to Tell",
  "confidence": <integer 0-100>,
  "headline": "<one punchy empathetic sentence, max 12 words>",
  "analysis": "<3 paragraphs separated by newlines, honest and warm, specific to their situation>",
  "green_flags": ["<up to 3 positive signals>"],
  "yellow_flags": ["<up to 3 ambiguous signals>"],
  "red_flags": ["<up to 2 cautionary signals, or empty list>"],
  "next_step": "<one specific actionable thing to do this week>",
  "affirmation": "<one short genuine sentence of emotional support>"
}
Return ONLY the JSON object. No markdown. No explanation. No extra text."""

    raw = chat(system, f"My situation:\n{context}")
    # Clean any markdown fences
    raw = raw.replace("```json","").replace("```","").strip()
    # Find the JSON object
    start = raw.find("{")
    end   = raw.rfind("}") + 1
    return json.loads(raw[start:end])


def run_trend(log: list, person: str) -> str:
    entries = "\n".join([
        f"- {e['date']}: warmth {e['warmth']}/10 — {e['desc']} ({e['vibe']})"
        for e in log
    ])
    system = "You are a warm relationship advisor. Analyze these interaction logs and give a 2-3 sentence honest trend: are signals warming up, cooling down, or staying flat? Be specific and kind. Plain text only, no JSON."
    return chat(system, f"Person: {person}\nLogs:\n{entries}\n\nWhat is the trend?", max_tokens=300)


def run_message(answers: dict, result: dict, tone: str, goal: str) -> str:
    ctx = (
        f"Person: {answers.get('who','someone')}\n"
        f"Known for: {answers.get('duration','a while')}\n"
        f"Situation: {answers.get('signs','')}\n"
        f"AI verdict: {result.get('verdict','')}\n"
        f"Suggested next step: {result.get('next_step','')}\n"
        f"Tone requested: {tone}\n"
        f"Goal of message: {goal}"
    )
    system = "You are a witty, emotionally intelligent messaging coach. Write a short natural message this person could actually send. Sound like a real human, not AI. No quotes around the message. Max 3 sentences. Return only the message text, nothing else."
    return chat(system, ctx, max_tokens=150)


# ══════════════════════════════════════════════════════════════════════════
#  REUSABLE COMPONENTS
# ══════════════════════════════════════════════════════════════════════════

def render_tracker():
    log    = st.session_state.log
    person = st.session_state.answers.get("who", "this person")

    with st.form("log_form", clear_on_submit=True):
        desc   = st.text_input("What happened?",
                               placeholder="e.g. They texted me first out of nowhere")
        warmth = st.slider("How warm did it feel?", 1, 10, 5,
                           help="1 = cold/awkward  ·  10 = electric/intimate")
        vibe   = st.selectbox("Who initiated?",
                              ["They did","I did","Mutual","Accidental","Online only"])
        if st.form_submit_button("Log this ♡"):
            if desc.strip():
                st.session_state.log.append({
                    "date":   datetime.now().strftime("%b %d"),
                    "desc":   desc.strip(),
                    "warmth": warmth,
                    "vibe":   vibe,
                })
                st.rerun()
            else:
                st.warning("Describe what happened first.")

    if not log:
        st.markdown(
            "<p style='color:#4a3040;font-style:italic;margin-top:16px;'>"
            "No interactions logged yet. Add your first one above.</p>",
            unsafe_allow_html=True,
        )
        return

    st.markdown("<br>", unsafe_allow_html=True)
    st.line_chart(
        {"Warmth (/10)": [e["warmth"] for e in log]},
        use_container_width=True, height=160, color=["#C9607A"],
    )

    if st.button("🔍 What's the trend?"):
        with st.spinner("Reading the pattern... ♡"):
            trend = run_trend(log, person)
        st.markdown(f"""
        <div class="card">
            <p style="color:#A78BFA;font-size:11px!important;letter-spacing:1px;
               text-transform:uppercase;margin-bottom:8px;">Trend Analysis</p>
            <p style="line-height:1.8;font-size:16px!important;">{trend}</p>
        </div>""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    for entry in reversed(log):
        w   = entry["warmth"]
        clr = "#6EE7B7" if w >= 7 else "#FFD700" if w >= 4 else "#FF8C69"
        st.markdown(f"""
        <div class="log-entry">
            <div style="display:flex;justify-content:space-between;">
                <span style="color:#A89090;font-size:13px!important;">
                    {entry['date']} · {entry['vibe']}</span>
                <span style="color:{clr};font-size:13px!important;font-weight:bold;">
                    warmth {w}/10</span>
            </div>
            <p style="margin:6px 0 8px;font-size:15px!important;">{entry['desc']}</p>
            <div style="background:#2a1a20;border-radius:4px;height:6px;">
                <div style="height:6px;width:{w*10}%;background:{clr};border-radius:4px;"></div>
            </div>
        </div>""", unsafe_allow_html=True)

    if st.button("🗑 Clear log"):
        st.session_state.log = []
        st.rerun()


def render_message_gen():
    result  = st.session_state.result
    answers = st.session_state.answers

    if not result:
        st.info("Complete the signal analysis first so I can craft the right message.")
        if st.button("Go to Analysis →"):
            go("questions")
        return

    tone = st.selectbox("Message tone", MSG_TONES)
    goal = st.text_input(
        "What's the goal?",
        placeholder="e.g. Break the ice, invite them out, reply to their meme...",
    )

    if st.button("✨ Write it for me"):
        if not goal.strip():
            st.warning("Tell me what you want the message to achieve.")
        else:
            with st.spinner("Finding the perfect words... ♡"):
                try:
                    text = run_message(answers, result, tone, goal.strip())
                    st.session_state.messages.insert(0, {
                        "text": text,
                        "tone": tone,
                        "goal": goal.strip(),
                        "ts":   datetime.now().strftime("%H:%M"),
                    })
                    st.rerun()
                except Exception as e:
                    st.error(f"Couldn't generate message: {e}")

    if st.session_state.messages:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            "<p style='color:#6a4a50;font-size:12px!important;letter-spacing:1px;"
            "text-transform:uppercase;'>Generated messages (newest first)</p>",
            unsafe_allow_html=True,
        )
        for m in st.session_state.messages[:5]:
            st.markdown(f"""
            <div class="msg-box">
                <p style="color:#6a4a50;font-size:11px!important;margin-bottom:10px;
                   letter-spacing:1px;text-transform:uppercase;">
                   {m['tone']} · {m['ts']} · {m['goal']}</p>
                <p style="font-size:17px!important;line-height:1.8;color:#E8DDD5;">
                   {m['text']}</p>
            </div>""", unsafe_allow_html=True)

        if st.button("🗑 Clear messages"):
            st.session_state.messages = []
            st.rerun()


# ══════════════════════════════════════════════════════════════════════════
#  SCREENS
# ══════════════════════════════════════════════════════════════════════════

# ── INTRO ──────────────────────────────────────────────────────────────────
if st.session_state.screen == "intro":
    st.markdown(
        "<div style='text-align:center;font-size:52px;margin-bottom:8px;'>♡</div>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<h1 style='text-align:center;font-size:46px;'>HeartRead</h1>",
        unsafe_allow_html=True,
    )
    st.markdown(
        "<p style='text-align:center;color:#A89090;font-size:18px!important;"
        "font-style:italic;'>The 3am thought you can't tell your friends.</p>",
        unsafe_allow_html=True,
    )
    st.markdown("<br>", unsafe_allow_html=True)

    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        if st.button("Read my signals →"):
            go("questions")

    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class="card" style="text-align:center;">
            <div style="font-size:28px;">📊</div>
            <p style="color:#C9A0A0;margin-top:8px;">Signal Tracker</p>
            <p style="color:#6a4a50;font-size:13px!important;">Log interactions, spot the trend</p>
        </div>""", unsafe_allow_html=True)
        if st.button("Open Tracker"):
            go("tracker")

    with col2:
        st.markdown("""
        <div class="card" style="text-align:center;">
            <div style="font-size:28px;">✉️</div>
            <p style="color:#C9A0A0;margin-top:8px;">What to Say</p>
            <p style="color:#6a4a50;font-size:13px!important;">AI-crafted messages for your situation</p>
        </div>""", unsafe_allow_html=True)
        if st.button("Get a Message"):
            go("message" if st.session_state.result else "questions")

    st.markdown(
        "<p style='text-align:center;color:#4a3a40;font-size:12px!important;"
        "margin-top:28px;'>Private · No data saved · Powered by Groq AI (Free)</p>",
        unsafe_allow_html=True,
    )


# ── QUESTIONS ──────────────────────────────────────────────────────────────
elif st.session_state.screen == "questions":
    qi    = st.session_state.current_q
    q     = QUESTIONS[qi]
    total = len(QUESTIONS)
    pct   = int((qi / total) * 100)

    st.markdown(f"""
    <div class="qnum">Question {qi+1} of {total}</div>
    <div class="prog-bg">
        <div class="prog-fill" style="width:{pct}%;
             background:linear-gradient(90deg,#8B4567,#C9607A);"></div>
    </div>""", unsafe_allow_html=True)

    st.markdown(f"### {q['label']}")
    answer = st.text_area(
        "", placeholder=q["help"], height=140,
        key=f"q_{qi}", label_visibility="collapsed",
    )
    st.markdown("<br>", unsafe_allow_html=True)

    is_last = qi == total - 1
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        if st.button("Read my heart 💕" if is_last else "Continue →"):
            if not answer.strip():
                st.warning("Please share something — even a few words helps.")
            else:
                st.session_state.answers[q["key"]] = answer.strip()
                if is_last:
                    with st.spinner("Reading between the lines... ♡"):
                        try:
                            st.session_state.result = run_analysis(st.session_state.answers)
                            go("result")
                        except Exception as e:
                            st.error(f"Something went wrong: {e}")
                else:
                    st.session_state.current_q += 1
                    st.rerun()


# ── RESULT ─────────────────────────────────────────────────────────────────
elif st.session_state.screen == "result":
    result  = st.session_state.result
    verdict = result.get("verdict", "Hard to Tell")
    cfg     = VERDICT_CONFIG.get(verdict, VERDICT_CONFIG["Hard to Tell"])
    conf    = result.get("confidence", 50)

    st.markdown(f"""
    <div class="verdict-card"
         style="background:{cfg['bg']};border:1px solid {cfg['border']};
                box-shadow:0 0 40px {cfg['color']}22;">
        <div style="font-size:44px;">{cfg['emoji']}</div>
        <h2 style="color:{cfg['color']}!important;font-size:30px!important;margin:8px 0;">
            {verdict}</h2>
        <p style="font-style:italic;color:#C8B8B8;font-size:18px!important;">
            "{result.get('headline','')}"</p>
        <div style="background:#00000033;border-radius:4px;height:5px;
                    max-width:200px;margin:14px auto 4px;">
            <div style="height:5px;width:{conf}%;background:{cfg['color']};
                        border-radius:4px;"></div>
        </div>
        <p style="color:#7a6060;font-size:13px!important;">
            Signal confidence: {conf}%</p>
    </div>""", unsafe_allow_html=True)

    tab1, tab2, tab3, tab4, tab5 = st.tabs(
        ["💬 Analysis", "🚩 Signals", "👣 Next Step", "📊 Tracker", "✉️ What to Say"]
    )

    with tab1:
        st.markdown("<br>", unsafe_allow_html=True)
        for para in result.get("analysis", "").split("\n"):
            if para.strip():
                st.markdown(
                    f"<p style='color:#C8B8B8;line-height:1.8;font-size:16px!important;'>"
                    f"{para.strip()}</p>",
                    unsafe_allow_html=True,
                )

    with tab2:
        st.markdown("<br>", unsafe_allow_html=True)

        def show_flags(title, flags, bg, color, border):
            if not flags:
                return
            st.markdown(f"**{title}**")
            chips = " ".join([
                f'<span class="flag-chip" style="background:{bg};color:{color};'
                f'border:1px solid {border};">{f}</span>'
                for f in flags
            ])
            st.markdown(chips, unsafe_allow_html=True)
            st.markdown("<br>", unsafe_allow_html=True)

        show_flags("💚 Promising Signs",  result.get("green_flags",  []), "#1a2e1a","#6EE7B7","#2a4a2a")
        show_flags("🟡 Worth Noting",     result.get("yellow_flags", []), "#2a2a1a","#FFD700","#4a4a2a")
        show_flags("🔴 Be Cautious",      result.get("red_flags",    []), "#2e1a1a","#FF8C69","#4a2a2a")

    with tab3:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"""
        <div class="card">
            <p style="color:#A78BFA;font-size:11px!important;letter-spacing:1.5px;
               text-transform:uppercase;margin-bottom:10px;">Do this week</p>
            <p style="font-size:18px!important;line-height:1.7;">
                {result.get('next_step','')}</p>
        </div>
        <div class="affirmation">♡ {result.get('affirmation','')}</div>
        """, unsafe_allow_html=True)

    with tab4:
        st.markdown("<br>", unsafe_allow_html=True)
        render_tracker()

    with tab5:
        st.markdown("<br>", unsafe_allow_html=True)
        render_message_gen()

    st.markdown("<br><br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns([1, 2, 1])
    with c2:
        if st.button("↩ Start over"):
            st.session_state.result    = None
            st.session_state.answers   = {}
            st.session_state.current_q = 0
            st.session_state.messages  = []
            go("intro")


# ── TRACKER standalone ──────────────────────────────────────────────────────
elif st.session_state.screen == "tracker":
    st.markdown("### 📊 Signal Tracker")
    st.markdown(
        "<p style='color:#A89090;'>Log interactions over time. "
        "I'll tell you if things are warming up or cooling down.</p>",
        unsafe_allow_html=True,
    )
    st.markdown("<br>", unsafe_allow_html=True)
    render_tracker()
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("← Back to Home"):
        go("intro")


# ── MESSAGE standalone ──────────────────────────────────────────────────────
elif st.session_state.screen == "message":
    st.markdown("### ✉️ What to Say")
    st.markdown(
        "<p style='color:#A89090;'>AI-crafted messages tailored to your exact situation.</p>",
        unsafe_allow_html=True,
    )
    st.markdown("<br>", unsafe_allow_html=True)
    render_message_gen()
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("← Back"):
        go("result" if st.session_state.result else "intro")
