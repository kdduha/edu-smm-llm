import streamlit as st
import datetime
import src.init as init
import json
import re
import ast

# --- Navigation Bar ---
st.markdown("""
    <style>
        .nav {
            display: flex;
            gap: 2rem;
            font-size: 1.2rem;
            margin-bottom: 2rem;
        }
        .nav a {
            text-decoration: none;
            color: #4A90E2;
            font-weight: bold;
        }
        .nav a.selected {
            border-bottom: 2px solid #4A90E2;
        }
    </style>
    <div class="nav">
        <a href="/Calendar">Plan the content</a>
        <a href="/Generate" class="selected">Generate post</a>
    </div>
""", unsafe_allow_html=True)

if "events" not in st.session_state:
    st.session_state["events"] = []

st.title("Generate a New Post")

# --- AI Generation Section ---
st.subheader("AI Content Plan Generation")
llm_cfg, openai_cfg, ui_cfg = init.config()
chat_model = init.model(llm_cfg, openai_cfg)

with st.form("ai_generate_form"):
    platforms = st.multiselect(
        "Select platforms", ["Instagram", "VK", "Telegram", "YouTube"], default=["Instagram", "Telegram"]
    )
    num_days = st.slider("Number of days", 1, 30, 7)
    topics = st.text_input("Key topics (comma-separated)", "education, technology, tips")
    sources = st.text_input("Material sources (comma-separated)", "vc.ru, habr.com, ted.com")
    user_notes = st.text_area("Additional instructions", "Focus on engaging formats.")
    ai_submitted = st.form_submit_button("Generate with AI")

if ai_submitted:
    today = datetime.date.today()
    dates = [(today + datetime.timedelta(days=i)).isoformat() for i in range(num_days)]
    prompt = (
        "Generate a detailed SMM content plan as JSON only. "
        f"Using sequential dates starting from today ({dates[0]}) for {num_days} days. "
        f"Based on parameters: platforms={platforms}, topics={[t.strip() for t in topics.split(',') if t.strip()]}, sources={[s.strip() for s in sources.split(',') if s.strip()]}, notes={user_notes}. "
        "Output strictly a JSON array of objects (double quotes), each with keys: "
        "day (YYYY-MM-DD), platform, title, content_type, description, source. "
        "Descriptions should be detailed (at least 2-3 sentences). "
        "Respond with no extra text, wrap JSON in ```json ... ``` code block. "
    )
    with st.spinner("Generating with AI..."):
        response = chat_model.invoke([init.HumanMessage(content=prompt)])
        raw = response.content
        match = re.search(r"```json\s*(\[.*?\])\s*```", raw, re.S)
        json_str = match.group(1) if match else raw
        try:
            plan = json.loads(json_str)
        except json.JSONDecodeError:
            try:
                plan = ast.literal_eval(json_str)
            except Exception:
                st.error("Failed to parse JSON plan.")
                st.code(raw)
                plan = []
        # Add generated posts to calendar events
        for item in plan:
            st.session_state["events"].append(item)
        st.success(f"{len(plan)} posts added to calendar!")
        st.switch_page("pages/1_Calendar.py")

# --- Manual Post Creation Section ---
st.subheader("Manual Post Creation")
with st.form("generate_post_form"):
    day = st.date_input("Date", value=datetime.date.today())
    platform = st.selectbox("Platform", ["Instagram", "VK", "Telegram", "YouTube"])
    title = st.text_input("Title")
    content_type = st.selectbox("Content Type", ["Text", "Image", "Video", "Link"])
    description = st.text_area("Description")
    source = st.text_input("Source")
    submitted = st.form_submit_button("Add to Calendar")

if submitted:
    st.session_state["events"].append({
        "day": day.isoformat(),
        "platform": platform,
        "title": title,
        "content_type": content_type,
        "description": description,
        "source": source
    })
    st.success("Post added to calendar!")
    st.switch_page("pages/1_Calendar.py")