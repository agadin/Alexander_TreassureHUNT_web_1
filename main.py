import streamlit as st
import json
import os
import random
import re

# ────────────────────────────────────────────────────────────────────────────────
#  Hide Streamlit header bar
# ────────────────────────────────────────────────────────────────────────────────
hide_decoration_bar_style = """
    <style>
        header {visibility: hidden;}
    </style>
"""
st.markdown(hide_decoration_bar_style, unsafe_allow_html=True)

# ────────────────────────────────────────────────────────────────────────────────
#  One‑time session initialisation
# ────────────────────────────────────────────────────────────────────────────────
if "init_done" not in st.session_state:
    st.session_state.update({
        "authenticated": False,
        "passage_order": [],   # shuffled list of (max 3) JSON file names
        "passage_idx": 0,      # index of current passage in passage_order
        "question_order": [],  # shuffled list of question indices for current passage
        "question_idx": 0,     # index of current question in question_order
        "score": 0,
        "attempted": 0,
        "wrong": 0,
        "submitted": False,
        "selected_answer": None,
        "finished": False,
        "init_done": True
    })

# ────────────────────────────────────────────────────────────────────────────────
#  Authentication helpers
# ────────────────────────────────────────────────────────────────────────────────
PASSWORD = "softtissue"  # change as required


def check_password() -> None:
    """Simple password check."""
    if st.session_state.get("password_input", "") == PASSWORD:
        st.session_state.authenticated = True
        st.session_state.password_input = ""
        build_passage_list()  # prepare data right after login
    else:
        st.error("Incorrect password")


# ────────────────────────────────────────────────────────────────────────────────
#  Passage & question ordering
# ────────────────────────────────────────────────────────────────────────────────

def build_passage_list() -> None:
    """Build a shuffled list of up to three passage files for this session."""
    files = sorted(
        [f for f in os.listdir() if f.startswith("passage") and f.endswith(".json")],
        key=lambda x: int(re.findall(r"\d+", x)[0])  # keep numeric order before shuffling
    )
    # Pick at most 3 unique passages
    if len(files) > 3:
        files = random.sample(files, k=3)
    random.shuffle(files)

    st.session_state.passage_order = files
    st.session_state.passage_idx = 0
    load_current_passage()


def load_current_passage() -> None:
    """Load JSON for current passage and shuffle its questions."""
    fname = st.session_state.passage_order[st.session_state.passage_idx]
    with open(fname, "r", encoding="utf-8") as f:
        st.session_state.current_data = json.load(f)

    num_qs = len(st.session_state.current_data["questions"])
    st.session_state.question_order = random.sample(range(num_qs), k=num_qs)
    st.session_state.question_idx = 0

# ────────────────────────────────────────────────────────────────────────────────
#  Display helpers
# ────────────────────────────────────────────────────────────────────────────────

def show_passage() -> None:
    st.markdown(f"**Passage {st.session_state.passage_idx + 1}**")
    st.write(st.session_state.current_data["passage"])


def show_question() -> str:
    q_pos = st.session_state.question_order[st.session_state.question_idx]
    q_data = st.session_state.current_data["questions"][q_pos]

    st.markdown(f"{q_data['question']}")
    st.session_state.selected_answer = st.radio("Select your answer:", q_data["options"])
    return q_data["correct"]

# ────────────────────────────────────────────────────────────────────────────────
#  Navigation logic
# ────────────────────────────────────────────────────────────────────────────────

def advance():
    """Move to next question or passage; set finished flag when done."""
    st.session_state.question_idx += 1

    # More questions within this passage?
    if st.session_state.question_idx < len(st.session_state.question_order):
        return  # stay on same passage

    # Otherwise move to next passage
    st.session_state.passage_idx += 1
    if st.session_state.passage_idx < len(st.session_state.passage_order):
        load_current_passage()
    else:
        st.session_state.finished = True

# ────────────────────────────────────────────────────────────────────────────────
#  Final score calculation
# ────────────────────────────────────────────────────────────────────────────────

def final_score() -> int:
    # Original spec: 132 – wrong answers
    return 132 - st.session_state.wrong

# ────────────────────────────────────────────────────────────────────────────────
#  UI flow
# ────────────────────────────────────────────────────────────────────────────────

# 1. Login
if not st.session_state.authenticated:
    st.write("User: Lakelab")
    st.session_state.password_input = st.text_input("Password", type="password")
    st.button("Submit", on_click=check_password)
    st.stop()


if st.session_state.finished:
    score = final_score()
    st.markdown(f"## Your final score is: {score}")
    st.markdown("**Behind the poster where the walls grow bare,The old Instron room holds secrets rare.**" if score > 127 else "**Refresh and try again!**")
    st.stop()

# 3. Main quiz interface
show_passage()
correct_ans = show_question()

if st.button("Submit") and not st.session_state.submitted:
    st.session_state.submitted = True
    st.session_state.attempted += 1

    if st.session_state.selected_answer == correct_ans:
        st.session_state.score += 1
    else:
        st.session_state.wrong += 1

    # reset submit flag & continue
    st.session_state.submitted = False
    advance()
    st.experimental_rerun()
