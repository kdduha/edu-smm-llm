import json
import re
import ast
import datetime
import streamlit as st
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage

import src.init as init


def setup_ui(logo_link: str) -> None:
    st.set_page_config(page_title="EDU LLM SMM Planner", layout="centered")
    header_html = f"""
    <div style="display: flex; align-items: center; gap: 10px;">
        <img src="{logo_link}" alt="Logo" width="50"/>
        <h1 style="margin: 0;">EDU LLM SMM Planner</h1>
    </div>
    """
    st.markdown(header_html, unsafe_allow_html=True)
    st.markdown("<p style='color:gray;'>AI-powered SMM content planner for educational channels</p>", unsafe_allow_html=True)


def init_session() -> None:
    if "content_plan" not in st.session_state:
        st.session_state.content_plan = None


def sidebar_inputs() -> dict:
    st.sidebar.header("Content Plan Settings")
    platforms = st.sidebar.multiselect(
        "Select platforms", ["Instagram", "VK", "Telegram", "YouTube"], default=["Instagram", "Telegram"]
    )
    num_days = st.sidebar.slider("Number of days", 1, 30, 7)
    topics = st.sidebar.text_input("Key topics (comma-separated)", "education, technology, tips")
    sources = st.sidebar.text_input("Material sources (comma-separated)", "vc.ru, habr.com, ted.com")
    user_notes = st.sidebar.text_area("Additional instructions", "Focus on engaging formats.")
    return {
        "platforms": platforms,
        "num_days": num_days,
        "topics": [t.strip() for t in topics.split(",") if t.strip()],
        "sources": [s.strip() for s in sources.split(",") if s.strip()],
        "notes": user_notes
    }


def generate_plan(chat_model: ChatOpenAI, params: dict) -> list:
    today = datetime.date.today()
    dates = [(today + datetime.timedelta(days=i)).isoformat() for i in range(params['num_days'])]
    base = {k: v for k, v in params.items()}
    prompt = (
    "Generate a detailed SMM content plan as JSON only. "
    f"Using sequential dates starting from today ({dates[0]}) for {params['num_days']} days. "
    f"Based on parameters: platforms={params['platforms']}, topics={params['topics']}, sources={params['sources']}, notes={params['notes']}. "
    "Output strictly a JSON array of objects (double quotes), each with keys: "
    "day (YYYY-MM-DD), platform, title, content_type, description, source. "
    "Descriptions should be detailed (at least 2-3 sentences). "
    "Respond with no extra text, wrap JSON in ```json ... ``` code block. "
)

    response = chat_model.invoke([HumanMessage(content=prompt)])
    raw = response.content
    match = re.search(r"```json\s*(\[.*?\])\s*```", raw, re.S)
    json_str = match.group(1) if match else raw
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        try:
            return ast.literal_eval(json_str)
        except Exception:
            st.error("Failed to parse JSON plan.")
            st.code(raw)
            return []


def display_plan(plan: list) -> None:
    if not plan:
        st.info("No content plan to display.")
        return
    st.subheader("Generated Content Plan")
    for item in plan:
        with st.expander(f"{item['day']} — {item['platform']}"):
            st.markdown(f"**Title:** {item['title']}")
            st.markdown(f"**Format:** {item['content_type']}")
            st.markdown(f"**Description:** {item['description']}")
            st.markdown(f"**Source:** {item['source']}")
    st.download_button("Download JSON", json.dumps(plan, indent=2), "content_plan.json", "application/json")


if __name__ == "__main__":
    llm_cfg, openai_cfg, ui_cfg = init.config()
    chat_model = init.model(llm_cfg, openai_cfg)
    setup_ui(ui_cfg.get("logo_url", ""))
    init_session()
    params = sidebar_inputs()

    if st.sidebar.button("Generate Content Plan"):
        with st.spinner("Generating..."):
            st.session_state.content_plan = generate_plan(chat_model, params)

    if st.session_state.content_plan is not None:
        display_plan(st.session_state.content_plan)
