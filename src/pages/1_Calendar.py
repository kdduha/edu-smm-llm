import streamlit as st
import calendar
import datetime

# --- Platform Colors ---
PLATFORM_COLORS = {
    "Instagram": "#F58529",
    "VK": "#4C75A3",
    "Telegram": "#229ED9",
    "YouTube": "#FF0000",
    # fallback
    "default": "#E3F2FD"
}

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
        .legend {
            display: flex;
            gap: 1.5rem;
            margin-bottom: 1.5rem;
            align-items: center;
        }
        .legend-item {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            font-size: 1rem;
        }
        .legend-color {
            width: 18px;
            height: 18px;
            border-radius: 4px;
            display: inline-block;
        }
        .dot {
            display: inline-block;
            width: 10px;
            height: 10px;
            border-radius: 50%;
            margin-left: 2px;
            margin-right: 2px;
        }
        /* Remove outline only from calendar day buttons */
        .calendar-day-btn button {
            border: none !important;
            outline: none !important;
            box-shadow: none !important;
            background: none !important;
            color: inherit !important;
            font-weight: bold;
            font-size: 1em;
            cursor: pointer;
            padding: 0;
            margin: 0;
        }
    </style>
    <div class=\"nav\">
        <a href=\"pages/1_Calendar.py\" class=\"selected\">Plan the content</a>
        <a href=\"pages/2_Generate.py\">Generate post</a>
    </div>
""", unsafe_allow_html=True)

# --- Color Legend ---
st.markdown('<div class="legend">' +
    ''.join([
        f'<span class="legend-item"><span class="legend-color" style="background:{color}"></span>{platform}</span>'
        for platform, color in PLATFORM_COLORS.items() if platform != "default"
    ]) +
    '</div>', unsafe_allow_html=True)

# --- Calendar State ---
if "events" not in st.session_state:
    st.session_state["events"] = []  # Each event: {day, platform, title, content_type, description, source}

# --- Calendar Controls ---
today = datetime.date.today()
year = st.sidebar.number_input("Year", min_value=2020, max_value=2100, value=today.year)
month = st.sidebar.number_input("Month", min_value=1, max_value=12, value=today.month)

# --- Calendar Grid ---
st.title(f"{calendar.month_name[month]} {year}")
cal = calendar.Calendar()
days = list(cal.itermonthdays(year, month))

# --- Render Calendar ---
def get_events_for_day(day):
    return [e for e in st.session_state["events"] if e["day"] == datetime.date(year, month, day).isoformat()]

cols = st.columns(7)
for i, weekday in enumerate(["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]):
    cols[i].markdown(f"**{weekday}**")

for week in calendar.monthcalendar(year, month):
    cols = st.columns(7)
    for i, day in enumerate(week):
        if day == 0:
            cols[i].markdown("")
        else:
            events = get_events_for_day(day)
            btn_key = f"day-btn-{year}-{month}-{day}"
            with cols[i]:
                st.markdown('<div class="calendar-day-btn">', unsafe_allow_html=True)
                if st.button(str(day), key=btn_key):
                    st.session_state["selected_day"] = day
                st.markdown('</div>', unsafe_allow_html=True)
            # Render colored dots for events below the button
            if events:
                dots_html = ''.join([
                    f"<span class='dot' style='background:{PLATFORM_COLORS.get(e['platform'], PLATFORM_COLORS['default'])}'></span>"
                    for e in events
                ])
                cols[i].markdown(dots_html, unsafe_allow_html=True)

# --- Event Details for Selected Day ---
if "selected_day" in st.session_state:
    selected_day = st.session_state["selected_day"]
    events = get_events_for_day(selected_day)
    st.markdown("---")
    st.subheader(f"Events for {calendar.month_name[month]} {selected_day}, {year}")
    if not events:
        st.info("No events for this day.")
    else:
        for event in events:
            st.markdown(f"### {event['title']} ({event['platform']})")
            st.markdown(f"**Format:** {event['content_type']}")
            st.markdown(f"**Description:** {event['description']}")
            st.markdown(f"**Source:** {event['source']}")
            st.markdown("---")
    if st.button("Close day details"):
        del st.session_state["selected_day"]

# --- Add/Generate Post Button ---
st.markdown("<br>", unsafe_allow_html=True)
st.page_link("pages/2_Generate.py", label="➕ Generate new post")
