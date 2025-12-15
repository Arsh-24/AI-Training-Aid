import os
import json
import io
from pathlib import Path
from dataclasses import dataclass
from typing import List, Optional, Dict, Any

import pandas as pd
import streamlit as st


try:
    from reportlab.lib.pagesizes import A4
    from reportlab.pdfgen import canvas
    from reportlab.lib.units import cm

    PDF_AVAILABLE = True
except Exception:
    PDF_AVAILABLE = False

try:
    from openai import OpenAI

    api_key = os.getenv("OPENAI_API_KEY")
    client = OpenAI(api_key=api_key) if api_key else None
    OPENAI_AVAILABLE = client is not None
except Exception:
    client = None
    OPENAI_AVAILABLE = False


@dataclass
class SessionPlan:
    day: str
    focus: str
    intensity: str
    duration_min: int
    load_units: int
    notes: str


DAYS_ORDER = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

MEDIA_DIR = Path("media")

BOXING_VISUAL_MAP: Dict[str, str] = {
    "shadow": "boxing_shadow.gif",
    "bag": "boxing_bag.gif",
    "footwork": "boxing_footwork.gif",
    "defence": "boxing_defence.gif",
    "conditioning": "boxing_conditioning.gif",
}


def find_visual_for_session(focus: str) -> Optional[Path]:
    focus_lower = focus.lower()
    for keyword, filename in BOXING_VISUAL_MAP.items():
        if keyword in focus_lower:
            candidate = MEDIA_DIR / filename
            if candidate.exists():
                return candidate
    return None


def generate_boxing_sessions_template(
    level: str,
    sessions_per_week: int,
    contraindications: str,
) -> List[SessionPlan]:
    level = level.lower()

    if level == "novice":
        templates = [
            SessionPlan(
                day="Tue",
                focus="Boxing basics: stance, guard & straight punches",
                intensity="Easy–Moderate",
                duration_min=25,
                load_units=30,
                notes=(
                    "Warm-up: 5 min skipping or brisk walk.\n"
                    "Technique: 4 × 2 min shadow boxing (jab–cross, basic guard) with 1 min rest.\n"
                    "Bag/pillow: 4 × 1 min straight punches, light power.\n"
                    "Cool-down: 5 min shoulder, wrist and calf stretches.\n"
                    f"Contraindications to watch: {contraindications or 'None stated'}."
                )
            ),
            SessionPlan(
                day="Thu",
                focus="Footwork & defence foundations",
                intensity="Moderate",
                duration_min=25,
                load_units=35,
                notes=(
                    "Warm-up: 5 min dynamic mobility (hips, ankles, shoulders).\n"
                    "Main: 4 × 2 min shadow boxing with basic steps (forward/back/side) and guard up.\n"
                    "Defence drill: 3 × 2 min slip/duck movements in front of mirror or wall.\n"
                    "Core: 3 × 20 s plank, 20 s rest.\n"
                    "Cool-down: 5 min relaxed walk + breathing.\n"
                    f"Avoid any movements that aggravate: {contraindications or 'None'}."
                )
            ),
            SessionPlan(
                day="Sat",
                focus="Conditioning: simple intervals + technique",
                intensity="Moderate",
                duration_min=30,
                load_units=40,
                notes=(
                    "Warm-up: 5 min skipping or light jog.\n"
                    "Intervals: 6 × 30 s fast straight punches (shadow or bag) + 60 s easy movement.\n"
                    "Technique: 4 × 2 min shadow boxing, mixing punches with basic defence.\n"
                    "Cool-down: 5–8 min stretch (hips, hamstrings, shoulders).\n"
                    f"Stop if pain or dizziness occurs, especially given: {contraindications or 'no stated issues'}."
                )
            ),
        ]
    elif level == "intermediate":
        templates = [
            SessionPlan(
                day="Mon",
                focus="Technical combinations & footwork",
                intensity="Moderate–Hard",
                duration_min=35,
                load_units=55,
                notes=(
                    "Warm-up: 5 min skipping + joint mobility.\n"
                    "Combos on bag/shadow: 5 × 3 min (jab–cross–hook, jab–cross–cross–hook), "
                    "60–90 s rest.\n"
                    "Footwork rounds: 3 × 2 min circling and cutting the ring.\n"
                    "Cool-down: 5 min light walk + stretching.\n"
                    f"Modify combinations if they aggravate: {contraindications or 'None'}."
                )
            ),
            SessionPlan(
                day="Wed",
                focus="Defence, counters & core",
                intensity="Moderate",
                duration_min=35,
                load_units=50,
                notes=(
                    "Warm-up: 5 min dynamic warm-up.\n"
                    "Defence rounds: 4 × 3 min slips, ducks, parries, then counter 1–2 punches.\n"
                    "Shadow or bag work: 3 × 2 min focusing on clean form at moderate pace.\n"
                    "Core circuit: 3 rounds (20 s plank, 10 sit-ups, 10 Russian twists), 60 s rest.\n"
                    f"Respect pain or previous issues: {contraindications or 'None'}."
                )
            ),
            SessionPlan(
                day="Fri",
                focus="Conditioning: intervals & power focus",
                intensity="Hard",
                duration_min=35,
                load_units=60,
                notes=(
                    "Warm-up: 5–7 min.\n"
                    "Intervals: 8 × 30 s high-output bag punching (all punches) + 60 s light movement.\n"
                    "Power focus: 3 × 2 min heavier single shots and 2–3 punch combinations.\n"
                    "Cool-down: 5–8 min stretching & breathing.\n"
                    "Keep technique tidy; reduce power if form breaks under fatigue."
                )
            ),
        ]
    else:
        templates = [
            SessionPlan(
                day="Tue",
                focus="High-complexity combinations & movement",
                intensity="Hard",
                duration_min=40,
                load_units=70,
                notes=(
                    "Warm-up: 8 min mixed skipping + mobility.\n"
                    "Complex combos: 5 × 3 min on bag/pads, mixing level changes and angles.\n"
                    "Footwork intensity: 3 × 2 min high-tempo ring movement.\n"
                    "Cool-down: 5–8 min mobility & stretch.\n"
                    f"Monitor joints and previous issues: {contraindications or 'None declared'}."
                )
            ),
            SessionPlan(
                day="Thu",
                focus="Defence, counters & conditioning mixed",
                intensity="Hard",
                duration_min=40,
                load_units=70,
                notes=(
                    "Warm-up: 6–8 min.\n"
                    "Defence & counter rounds: 4 × 3 min with slips, blocks and quick counters.\n"
                    "Conditioning: 6 × 30 s punch sprints + 60 s active rest.\n"
                    "Core & stability: 3 × 30 s plank variations.\n"
                    "Cool-down as normal; adjust if any warning signs."
                )
            ),
            SessionPlan(
                day="Sat",
                focus="Mixed technical conditioning (no full sparring)",
                intensity="Moderate–Hard",
                duration_min=40,
                load_units=65,
                notes=(
                    "Warm-up: 6–8 min.\n"
                    "Shadow rounds: 3 × 3 min visualising an opponent.\n"
                    "Bag rounds: 4 × 3 min mixing power and volume.\n"
                    "Cool-down: 5–8 min.\n"
                    "If usually sparring, this tool deliberately avoids contact to reduce risk."
                )
            ),
        ]

    if sessions_per_week <= len(templates):
        sessions = templates[:sessions_per_week]
    else:
        sessions = templates.copy()
        while len(sessions) < sessions_per_week:
            sessions.append(templates[0])

    day_index = {d: i for i, d in enumerate(DAYS_ORDER)}
    sessions.sort(key=lambda s: day_index.get(s.day, 99))
    return sessions


def generate_generic_sessions_template(
    sport: str,
    level: str,
    sessions_per_week: int,
    contraindications: str,
) -> List[SessionPlan]:
    sessions: List[SessionPlan] = []
    for i in range(sessions_per_week):
        day = DAYS_ORDER[(i * 2) % len(DAYS_ORDER)]
        sessions.append(
            SessionPlan(
                day=day,
                focus=f"{sport} conditioning session {i + 1}",
                intensity="Moderate",
                duration_min=30,
                load_units=40,
                notes=(
                    "Warm-up: 5–10 min easy movement.\n"
                    "Main: intervals or tempo work relevant to the sport.\n"
                    "Cool-down: 5–10 min mobility & stretching.\n"
                    f"Contraindications to respect: {contraindications or 'None stated'}."
                ),
            )
        )
    return sessions


def generate_sessions_ai(
    sport: str,
    level: str,
    sessions_per_week: int,
    last_week_load: int,
    contraindications: str,
) -> Optional[List[SessionPlan]]:
    if not OPENAI_AVAILABLE:
        return None

    try:
        level_lower = level.lower()

        if last_week_load <= 0:
            if level_lower == "novice":
                total_minutes_target = sessions_per_week * 25
            elif level_lower == "intermediate":
                total_minutes_target = sessions_per_week * 35
            else:
                total_minutes_target = sessions_per_week * 40
        else:
            total_minutes_target = max(60, min(300, int(last_week_load * 0.8)))

        safety_context = (
            "General rules:\n"
            "- Focus on non-contact, non-maximal work.\n"
            "- Use body-weight, light conditioning, or bag/shadow work (for boxing).\n"
            "- No heavy barbell max testing, no dangerous plyometrics.\n"
            "- Encourage listening to the body, stopping if anything feels sharp or worrying.\n"
        )

        prompt = (
            "Design a safe one-week training plan for a recreational athlete.\n"
            "Return ONLY valid JSON with a list under key 'sessions', no extra commentary.\n\n"
            f"Sport: {sport}\n"
            f"Level: {level}\n"
            f"Approximate sessions per week: {sessions_per_week}\n"
            f"Approximate total minutes target: {total_minutes_target}\n"
            f"Things to be careful with: {contraindications or 'None stated'}\n\n"
            f"{safety_context}\n"
            "For each session, include fields:\n"
            "- day: one of Mon, Tue, Wed, Thu, Fri, Sat, Sun\n"
            "- focus: short description of the main aim (e.g., 'Intervals and tempo work')\n"
            "- intensity: 'Easy', 'Moderate', or 'Hard'\n"
            "- duration_min: integer between 20 and 60 minutes\n"
            "- notes: outline warm-up, main part and cool-down in plain language\n\n"
            "Example JSON structure:\n"
            "{\n"
            "  \"sessions\": [\n"
            "    {\n"
            "      \"day\": \"Tue\",\n"
            "      \"focus\": \"Easy aerobic base run\",\n"
            "      \"intensity\": \"Easy\",\n"
            "      \"duration_min\": 30,\n"
            "      \"notes\": \"Warm-up: ... Main: ... Cool-down: ...\"\n"
            "    }\n"
            "  ]\n"
            "}\n"
        )

        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are a cautious strength and conditioning coach who avoids unnecessary risk.",
                },
                {"role": "user", "content": prompt},
            ],
            max_tokens=900,
            temperature=0.8,
        )

        raw = response.choices[0].message.content.strip()

        if raw.startswith("```"):
            raw = raw.strip("`")
            raw = raw.replace("json", "", 1).strip()

        data = json.loads(raw)
        sessions_data = data.get("sessions", [])

        sessions: List[SessionPlan] = []
        used_days = set()

        for item in sessions_data:
            if len(sessions) >= sessions_per_week:
                break

            day = item.get("day", "Mon")
            if day not in DAYS_ORDER:
                day = "Mon"

            base_index = DAYS_ORDER.index(day)
            for offset in range(len(DAYS_ORDER)):
                candidate_day = DAYS_ORDER[(base_index + offset) % len(DAYS_ORDER)]
                if candidate_day not in used_days:
                    day = candidate_day
                    used_days.add(day)
                    break

            focus = item.get("focus", f"{sport} session")
            intensity = item.get("intensity", "Moderate").title()
            if intensity not in ["Easy", "Moderate", "Hard"]:
                intensity = "Moderate"

            duration = int(item.get("duration_min", 30))
            duration = max(20, min(60, duration))

            factor = {"Easy": 1, "Moderate": 2, "Hard": 3}.get(intensity, 2)
            load_units = factor * duration

            notes = item.get("notes", "")
            notes += (
                f"\n\nIf anything feels sharp, unusual or worrying, stop or reduce intensity. "
                f"Context to remember: {contraindications or 'no specific issues noted'}."
            )

            sessions.append(
                SessionPlan(
                    day=day,
                    focus=focus,
                    intensity=intensity,
                    duration_min=duration,
                    load_units=load_units,
                    notes=notes,
                )
            )

        if not sessions:
            return None

        day_index = {d: i for i, d in enumerate(DAYS_ORDER)}
        sessions.sort(key=lambda s: day_index.get(s.day, 99))
        return sessions

    except Exception:
        return None


def apply_weekly_load_guardrail(
    sessions: List[SessionPlan],
    last_week_load: int,
) -> List[SessionPlan]:
    if last_week_load <= 0:
        return sessions

    current_total = sum(s.load_units for s in sessions)
    allowed_max = max(int(last_week_load * 1.10), last_week_load + 20)

    if current_total <= allowed_max:
        sessions[0].notes += (
            f"\n\nLoad check: planned weekly load {current_total} vs "
            f"last week {last_week_load} (within approximately +10% rule)."
        )
        return sessions

    factor = allowed_max / current_total
    for s in sessions:
        s.load_units = max(20, int(s.load_units * factor))
        s.notes += (
            f"\n\nLoad guardrail applied: weekly load reduced to stay within "
            f"+10% of last week ({last_week_load} → target ≤ {allowed_max})."
        )

    return sessions


def generate_week_plan(
    sport: str,
    level: str,
    sessions_per_week: int,
    last_week_load: int,
    contraindications: str,
) -> List[SessionPlan]:
    sport_lower = sport.lower()

    ai_sessions = generate_sessions_ai(
        sport=sport,
        level=level,
        sessions_per_week=sessions_per_week,
        last_week_load=last_week_load,
        contraindications=contraindications,
    )

    if ai_sessions:
        sessions = ai_sessions
    else:
        if sport_lower == "boxing":
            sessions = generate_boxing_sessions_template(
                level=level,
                sessions_per_week=sessions_per_week,
                contraindications=contraindications,
            )
        else:
            sessions = generate_generic_sessions_template(
                sport=sport,
                level=level,
                sessions_per_week=sessions_per_week,
                contraindications=contraindications,
            )

    sessions = apply_weekly_load_guardrail(sessions, last_week_load)
    return sessions


def generate_coaching_message(
    sessions: List[SessionPlan],
    sport: str,
    level: str,
    use_ai: bool = True,
) -> str:
    fallback = (
        "This week is about consistent, safe work. Focus on clean technique, "
        "controlled breathing, and honest pacing. If anything feels sharp, "
        "unusual or worrying, ease back or rest instead of forcing it. "
        "Small, steady sessions will build confidence and fitness over time."
    )

    if not use_ai or not OPENAI_AVAILABLE:
        return fallback

    try:
        total_load = sum(s.load_units for s in sessions)
        total_minutes = sum(s.duration_min for s in sessions)
        session_summary = "; ".join(
            f"{s.day}: {s.focus} ({s.intensity}, {s.duration_min} min)"
            for s in sessions
        )

        prompt = (
            "You are a calm, supportive sports coach. "
            "Write a short motivational message (120–160 words) for this week. "
            "Keep it safe, realistic and encouraging. Highlight pacing, rest, "
            "technique quality, and listening to the body. Avoid medical advice "
            "and do not promise specific results.\n\n"
            f"Sport: {sport}\n"
            f"Level: {level}\n"
            f"Weekly minutes: {total_minutes}\n"
            f"Weekly load units: {total_load}\n"
            f"Sessions: {session_summary}\n"
        )

        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": "You are a safe, encouraging sports coach."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=220,
            temperature=0.8,
        )
        text = response.choices[0].message.content.strip()
        return text or fallback
    except Exception:
        return fallback


def generate_voice_for_message(text: str) -> Optional[bytes]:
    if not OPENAI_AVAILABLE:
        return None

    try:
        response = client.audio.speech.create(
            model="gpt-4o-mini-tts",
            voice="alloy",
            input=text,
        )
        if hasattr(response, "read"):
            return response.read()
        if hasattr(response, "to_bytes"):
            return response.to_bytes()
        return None
    except Exception:
        return None


def build_plan_pdf(
    sessions: List[SessionPlan],
    meta: Dict[str, Any],
    coach_text: str,
) -> Optional[bytes]:
    if not PDF_AVAILABLE:
        return None

    buffer = io.BytesIO()
    c = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4

    x_margin = 2 * cm
    y = height - 2 * cm

    c.setFont("Helvetica-Bold", 16)
    c.drawString(x_margin, y, "Weekly Training Plan")
    y -= 1 * cm

    c.setFont("Helvetica", 11)
    sport = meta.get("sport", "N/A")
    level = meta.get("level", "N/A")
    last_load = meta.get("last_week_load", 0)
    c.drawString(x_margin, y, f"Sport: {sport} | Level: {level}")
    y -= 0.5 * cm
    c.drawString(x_margin, y, f"Last week's load (units): {last_load}")
    y -= 1 * cm

    c.setFont("Helvetica-Bold", 11)
    c.drawString(x_margin, y, "Day")
    c.drawString(x_margin + 2.5 * cm, y, "Focus")
    c.drawString(x_margin + 10 * cm, y, "Dur (min)")
    c.drawString(x_margin + 13 * cm, y, "Load")
    y -= 0.4 * cm
    c.line(x_margin, y, width - x_margin, y)
    y -= 0.3 * cm

    c.setFont("Helvetica", 10)
    for s in sessions:
        if y < 3 * cm:
            c.showPage()
            y = height - 2 * cm
            c.setFont("Helvetica-Bold", 11)
            c.drawString(x_margin, y, "Day")
            c.drawString(x_margin + 2.5 * cm, y, "Focus")
            c.drawString(x_margin + 10 * cm, y, "Dur (min)")
            c.drawString(x_margin + 13 * cm, y, "Load")
            y -= 0.4 * cm
            c.line(x_margin, y, width - x_margin, y)
            y -= 0.3 * cm
            c.setFont("Helvetica", 10)

        c.drawString(x_margin, y, s.day)
        c.drawString(x_margin + 2.5 * cm, y, s.focus[:40])
        c.drawString(x_margin + 10 * cm, y, str(s.duration_min))
        c.drawString(x_margin + 13 * cm, y, str(s.load_units))
        y -= 0.5 * cm

    if y < 4 * cm:
        c.showPage()
        y = height - 2 * cm

    c.setFont("Helvetica-Bold", 12)
    c.drawString(x_margin, y, "Motivational Coach Message")
    y -= 0.8 * cm
    c.setFont("Helvetica", 10)

    from textwrap import wrap
    for line in wrap(coach_text, 90):
        if y < 2 * cm:
            c.showPage()
            y = height - 2 * cm
            c.setFont("Helvetica", 10)
        c.drawString(x_margin, y, line)
        y -= 0.4 * cm

    c.showPage()
    c.save()
    pdf = buffer.getvalue()
    buffer.close()
    return pdf


def analyse_adherence_and_rpe(
    adherence_data: List[Dict[str, Any]],
) -> Optional[str]:
    if not adherence_data:
        return None

    completed = [d for d in adherence_data if d.get("completed")]
    total = len(adherence_data)
    comp_rate = len(completed) / total if total else 0.0

    rpes = [d["rpe"] for d in completed if isinstance(d.get("rpe"), int)]
    avg_rpe = sum(rpes) / len(rpes) if rpes else None

    msg_parts = []
    msg_parts.append(
        f"You completed {len(completed)} of {total} sessions "
        f"({comp_rate * 100:.0f}% adherence)."
    )

    if avg_rpe is not None:
        msg_parts.append(f" Average effort on completed sessions was about {avg_rpe:.1f}/10.")

        if avg_rpe >= 8:
            msg_parts.append(
                " That is quite high. Next week, it may be safer to hold or slightly "
                "reduce intensity rather than pushing further."
            )
        elif avg_rpe <= 3 and comp_rate >= 0.7:
            msg_parts.append(
                " Effort scores are low and consistency is good. A small progression "
                "next week may be reasonable if everything feels comfortable."
            )
        else:
            msg_parts.append(
                " Effort looks broadly appropriate. Keep aiming for this balance of challenge and control."
            )

    return " ".join(msg_parts)


def answer_user_question(question: str) -> str:
    if not question or question.strip() == "":
        return "Please type a question about your plan, training load, RPE, or safety."

    plan_sessions = st.session_state.get("plan_sessions") or []
    sport = st.session_state.get("plan_meta", {}).get("sport", "Not set")
    level = st.session_state.get("plan_meta", {}).get("level", "Not set")

    if not OPENAI_AVAILABLE:
        q_lower = question.lower()
        if "rpe" in q_lower or "effort" in q_lower:
            return (
                "RPE stands for Rate of Perceived Exertion, from 1 (very easy) to 10 (maximum effort). "
                "Choose the number that best matches how hard the session felt overall."
            )
        if "load" in q_lower:
            return (
                "Unit load combines how long and how hard you worked. Roughly: "
                "longer sessions and harder efforts mean higher load. It helps keep weekly increases safe."
            )
        if "safe" in q_lower or "injury" in q_lower:
            return (
                "The tool keeps sessions between about 20–60 minutes and limits weekly increases in load. "
                "It is still important to listen to your body and stop if anything feels sharp or worrying."
            )
        return (
            "This coach focuses on safe training structure: sessions, effort, and weekly progression. "
            "It cannot give medical advice. You can ask about RPE, load, why rest days appear, "
            "or how to think about progression."
        )

    try:
        session_summaries = []
        for s in plan_sessions:
            session_summaries.append(
                f"{s.get('day')}: {s.get('focus')} "
                f"({s.get('intensity')}, {s.get('duration_min')} min)"
            )
        session_text = "; ".join(session_summaries) if session_summaries else "No plan generated yet."

        context = (
            "You are an in-app coaching assistant. Answer questions about the training plan, "
            "RPE, load, and safety in simple, friendly language. Do NOT give medical advice or "
            "talk about internal implementation details. Do not mention any models or APIs.\n\n"
            f"Current sport: {sport}\n"
            f"Level: {level}\n"
            f"Sessions: {session_text}\n\n"
            "RPE explanation: 1–10 scale of how hard it felt. 1 = very easy, 10 = maximum effort.\n"
            "Load units: an internal number that combines how long and how hard sessions are. "
            "Higher numbers mean more training stress.\n"
        )

        response = client.chat.completions.create(
            model="gpt-4.1-mini",
            messages=[
                {"role": "system", "content": context},
                {"role": "user", "content": question},
            ],
            max_tokens=250,
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()
    except Exception:
        return (
            "There was a problem generating a detailed answer. "
            "As a reminder: RPE is how hard it felt (1–10), and load is a rough measure of "
            "training stress combining time and effort."
        )


st.set_page_config(
    page_title="Rules-Constrained AI Training Aid",
    layout="wide",
)

if "plan_sessions" not in st.session_state:
    st.session_state["plan_sessions"] = None
if "plan_meta" not in st.session_state:
    st.session_state["plan_meta"] = {}

st.title("Rules-Constrained AI Training Aid with Motivational Coach")

st.warning(
    "⚠️ This tool is for training support only. Do **not** enter personal or sensitive "
    "information such as passwords, card details, addresses, or medical IDs."
)

st.markdown(
    "This prototype generates a **safety-guarded weekly plan** and a short "
    "**motivational message** for sport-specific training. It is not medical "
    "advice and does not replace a qualified coach or clinician."
)

with st.sidebar:
    st.header("Plan inputs")

    sport = st.selectbox(
        "Sport",
        ["Boxing", "Running", "Football", "Generic conditioning"],
    )
    level = st.selectbox(
        "Level",
        ["Novice", "Intermediate", "Advanced"],
    )
    sessions_per_week = st.slider("Sessions per week", 2, 6, 3)

    last_week_load = st.number_input(
        "Last week's approximate training load (units)",
        min_value=0,
        max_value=1000,
        value=0,
        help="Used for a simple +10% weekly progression safety guardrail.",
    )

    contraindications = st.text_area(
        "Known issues / things to be careful with",
        placeholder="e.g., knee pain, shoulder surgery, asthma… "
                    "Do not include personal IDs or contact details.",
    )

    st.markdown("---")
    st.markdown("### Ask the coach")

    user_question = st.text_area(
        "Ask a question about your plan, RPE, load, or safety:",
        placeholder="e.g., What does RPE 7 mean? Why is there a rest day?",
        key="coach_question",
    )

    if st.button("Send question", key="ask_coach_button"):
        answer = answer_user_question(user_question)
        st.session_state["coach_answer"] = answer

    if "coach_answer" in st.session_state and st.session_state["coach_answer"]:
        st.markdown("**Coach reply:**")
        st.write(st.session_state["coach_answer"])


generate_clicked = st.button("Generate / Regenerate weekly plan", type="primary")

if generate_clicked:
    with st.spinner("Generating your personalised plan…"):
        sessions = generate_week_plan(
            sport=sport,
            level=level,
            sessions_per_week=sessions_per_week,
            last_week_load=last_week_load,
            contraindications=contraindications,
        )

    st.session_state["plan_sessions"] = [s.__dict__ for s in sessions]
    st.session_state["plan_meta"] = {
        "sport": sport,
        "level": level,
        "last_week_load": last_week_load,
        "contraindications": contraindications,
    }

if st.session_state["plan_sessions"] is not None:
    sessions = [SessionPlan(**d) for d in st.session_state["plan_sessions"]]

    df = pd.DataFrame(
        [
            {
                "Day": s.day,
                "Focus": s.focus,
                "Intensity": s.intensity,
                "Duration (min)": s.duration_min,
                "Load (units)": s.load_units,
            }
            for s in sessions
        ]
    )

    total_minutes = sum(s.duration_min for s in sessions)
    total_load = sum(s.load_units for s in sessions)

    st.subheader("Weekly Plan Overview")
    st.dataframe(df, width="stretch")

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Sessions", len(sessions))
    c2.metric("Total planned minutes", total_minutes)
    c3.metric("Total load (units)", total_load)

    with c4:
        if PDF_AVAILABLE:
            temp_coach_text = generate_coaching_message(
                sessions=sessions,
                sport=st.session_state["plan_meta"].get("sport", "Not set"),
                level=st.session_state["plan_meta"].get("level", "Not set"),
                use_ai=True,
            )
            pdf_bytes = build_plan_pdf(
                sessions,
                st.session_state["plan_meta"],
                temp_coach_text,
            )
            if pdf_bytes:
                st.download_button(
                    label="Download plan as PDF",
                    data=pdf_bytes,
                    file_name="training_plan.pdf",
                    mime="application/pdf",
                )
        else:
            st.caption("Install `reportlab` to enable PDF export.")

    with st.expander("How effort and load are measured"):
        st.markdown(
            "**Rate of Perceived Exertion (RPE)**\n\n"
            "- RPE is how hard the session felt on a scale from 1 to 10.\n"
            "- 1 = very easy, like a gentle walk.\n"
            "- 5–6 = steady but comfortable work.\n"
            "- 9–10 = maximum effort; not sustainable for long.\n\n"
            "**Unit Load**\n\n"
            "- Unit load is a rough measure of training stress.\n"
            "- It combines how long you trained and how hard it felt.\n"
            "- Roughly: longer sessions and harder efforts = higher load.\n"
            "- This helps keep weekly increases safe and controlled."
        )

    with st.expander("Safety summary"):
        st.markdown(
            "- Sessions are kept between **20 and 60 minutes**.\n"
            "- Weekly load is constrained to approximately **+10% of last week** when previous load is provided.\n"
            "- Notes remind the user to stop if anything feels sharp, unusual or worrying.\n"
            "- Content avoids max lifting and high-risk activities by design.\n"
            "- Always listen to your body and seek professional advice for pain or health concerns."
        )

    st.subheader("Motivational Coach Message")
    coach_text = generate_coaching_message(
        sessions=sessions,
        sport=st.session_state["plan_meta"].get("sport", "Not set"),
        level=st.session_state["plan_meta"].get("level", "Not set"),
        use_ai=True,
    )
    st.write(coach_text)

    audio_bytes = generate_voice_for_message(coach_text)
    if audio_bytes:
        st.audio(audio_bytes, format="audio/mp3")

    with st.expander("Session details"):
        for s in sessions:
            st.markdown(f"### {s.day} – {s.focus}")
            st.markdown(
                f"**Intensity:** {s.intensity}  |  "
                f"**Duration:** {s.duration_min} min  |  "
                f"**Load:** {s.load_units} units"
            )
            st.markdown("**What to do:**")
            st.markdown(s.notes.replace("\n", "  \n"))

            if st.session_state["plan_meta"].get("sport", "").lower() == "boxing":
                visual = find_visual_for_session(s.focus)
                if visual is not None:
                    st.image(
                        str(visual),
                        caption=f"Example drill for {s.focus}",
                        width="content",
                    )

            st.markdown("---")

    st.subheader("Adherence & Effort (optional reflection)")
    st.markdown(
        "Use this after you complete the week to reflect on what you actually did. "
        "This does not automatically change the plan yet, but it helps with thinking "
        "about progression and load.\n\n"
        "**RPE:** 1 = very easy, 10 = maximum effort."
    )

    for i in range(len(sessions)):
        if f"completed_{i}" not in st.session_state:
            st.session_state[f"completed_{i}"] = False
        if f"rpe_{i}" not in st.session_state:
            st.session_state[f"rpe_{i}"] = 0

    with st.form("adherence_form", clear_on_submit=False):
        adherence_data: List[Dict[str, Any]] = []

        for i, s in enumerate(sessions):
            cols = st.columns([2, 1, 1])
            with cols[0]:
                st.markdown(f"**{s.day} – {s.focus}**")
            with cols[1]:
                done = st.checkbox(
                    "Completed",
                    key=f"completed_{i}",
                )
            with cols[2]:
                rpe = st.number_input(
                    "RPE (0–10)",
                    min_value=0,
                    max_value=10,
                    key=f"rpe_{i}",
                    help="Rate of Perceived Exertion: how hard it felt overall.",
                )
            adherence_data.append({"completed": done, "rpe": rpe})

        submitted = st.form_submit_button("Summarise adherence & effort")

    if submitted:
        summary = analyse_adherence_and_rpe(adherence_data)
        if summary:
            st.success(summary)
        else:
            st.info("No adherence data entered yet.")
else:
    st.info("Set your details on the left, then click **Generate / Regenerate weekly plan**.")
