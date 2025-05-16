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
        "passage_order": [],
        "passage_idx": 0,
        "question_order": [],
        "question_idx": 0,
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
PASSWORD = st.secrets["auth"]["password"]


def check_password() -> None:
    if st.session_state.get("password_input", "") == PASSWORD:
        st.session_state.authenticated = True
        st.session_state.password_input = ""
        build_passage_list()
    else:
        st.error("Incorrect password")

# ────────────────────────────────────────────────────────────────────────────────
#  Passage & question ordering
# ────────────────────────────────────────────────────────────────────────────────

def build_passage_list() -> None:
    files = sorted(
        [f for f in os.listdir() if f.startswith("passage") and f.endswith(".json")],
        key=lambda x: int(re.findall(r"\d+", x)[0])
    )
    if len(files) > 3:
        files = random.sample(files, k=3)
    random.shuffle(files)

    st.session_state.passage_order = files
    st.session_state.passage_idx = 0
    load_current_passage()


def load_current_passage() -> None:
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
    st.session_state.question_idx += 1
    if st.session_state.question_idx < len(st.session_state.question_order):
        return
    st.session_state.passage_idx += 1
    if st.session_state.passage_idx < len(st.session_state.passage_order):
        load_current_passage()
    else:
        st.session_state.finished = True

# ────────────────────────────────────────────────────────────────────────────────
#  Final score calculation
# ────────────────────────────────────────────────────────────────────────────────

def final_score() -> int:
    return 132 - st.session_state.wrong

# ────────────────────────────────────────────────────────────────────────────────
#  UI flow
# ────────────────────────────────────────────────────────────────────────────────

if not st.session_state.authenticated:
    st.write("User: Lakelab")
    st.session_state.password_input = st.text_input("Password", type="password")
    st.button("Submit", on_click=check_password)
    st.stop()

if st.session_state.finished:
    score = final_score()
    st.markdown(f"## Your final score is: {score}")
    if score > 127:
        st.markdown(f"**{st.secrets['auth']['pass_message']}**")
    else:
        st.markdown("**Refresh and try again!**")
    st.stop()

show_passage()
correct_ans = show_question()

if st.button("Submit") and not st.session_state.submitted:
    st.session_state.submitted = True
    st.session_state.attempted += 1

    if st.session_state.selected_answer == correct_ans:
        st.session_state.score += 1
    else:
        st.session_state.wrong += 1

    st.session_state.submitted = False
    advance()
    st.rerun()
