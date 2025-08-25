
import streamlit as st
from dataclasses import dataclass
from typing import List
import json, pathlib

@dataclass
class Question:
    id: int
    stem: str
    choices: List[str]
    answer: int
    tags: List[str]

DATA_PATH = pathlib.Path(__file__).parent / "questions_custom.json"
QUESTIONS: List[Question] = [Question(**q) for q in json.loads(DATA_PATH.read_text(encoding="utf-8"))]

NAME_MAP = {
    "milestones": "Milestones",
    "psych": "Psych/Psychosocial",
    "immunization": "Immunization",
    "computation": "Computation",
    "others": "Others",
    "uncategorized": "Uncategorized",
}

def init_state():
    if "module" not in st.session_state:
        st.session_state.module = "All ({} items)".format(len(QUESTIONS))
    if "bank" not in st.session_state:
        st.session_state.bank = QUESTIONS
    if "order" not in st.session_state:
        st.session_state.order = list(range(len(st.session_state.bank)))
    if "current" not in st.session_state:
        st.session_state.current = 0
    if "correct" not in st.session_state:
        st.session_state.correct = 0
    if "attempted" not in st.session_state:
        st.session_state.attempted = 0
    if "shuffle" not in st.session_state:
        st.session_state.shuffle = False

def set_module(label):
    if label.startswith("All"):
        st.session_state.bank = QUESTIONS
    else:
        # reverse lookup
        rev = {v:k for k,v in NAME_MAP.items()}
        tag = rev.get(label, "milestones")
        st.session_state.bank = [q for q in QUESTIONS if (q.tags and q.tags[0]==tag)]
    st.session_state.order = list(range(len(st.session_state.bank)))
    st.session_state.current = 0
    st.session_state.correct = 0
    st.session_state.attempted = 0
    if "shuffled_once" in st.session_state: del st.session_state["shuffled_once"]

def current_question():
    idx = st.session_state.order[st.session_state.current]
    return st.session_state.bank[idx]

def next_q():
    if st.session_state.current < len(st.session_state.bank) - 1:
        st.session_state.current += 1

def prev_q():
    if st.session_state.current > 0:
        st.session_state.current -= 1

def main():
    st.set_page_config(page_title="Pediatrics Quiz — Custom", page_icon="🩺", layout="centered")
    init_state()

    # Build module labels
    labels = ["All ({} items)".format(len(QUESTIONS))]
    tags_present = sorted({q.tags[0] if q.tags else "uncategorized" for q in QUESTIONS})
    for t in ["milestones","psych","immunization","computation","others","uncategorized"]:
        if t in tags_present:
            labels.append(NAME_MAP.get(t, t.title()))

    with st.sidebar:
        module_label = st.selectbox("Module", labels, index=labels.index(st.session_state.module))
        if module_label != st.session_state.module:
            st.session_state.module = module_label
            set_module(module_label)
        if st.checkbox("Shuffle questions", value=st.session_state.shuffle, key="shuffle"):
            import random
            if "shuffled_once" not in st.session_state:
                random.seed(42)
                random.shuffle(st.session_state.order)
                st.session_state.shuffled_once = True
        else:
            if "shuffled_once" in st.session_state:
                del st.session_state["shuffled_once"]
                st.session_state.order = list(range(len(st.session_state.bank)))
                st.session_state.current = 0

        if st.button("Restart"):
            set_module(st.session_state.module)

        st.metric("Score", f"{st.session_state.correct}/{st.session_state.attempted}" if st.session_state.attempted else "0/0")

    if not st.session_state.bank:
        st.info("No questions available in this module.")
        return

    q = current_question()
    st.subheader(f"Question {st.session_state.current+1} of {len(st.session_state.bank)}")
    st.progress((st.session_state.current+1)/len(st.session_state.bank))
    st.write(q.stem)

    choice = st.radio("Select one answer", q.choices, index=None, key=f"pick_{q.id}")
    if st.button("Submit", key=f"submit_{q.id}"):
        if choice is None:
            st.warning("Please choose an option.")
        else:
            chosen = q.choices.index(choice)
            st.session_state.attempted += 1
            if chosen == q.answer:
                st.session_state.correct += 1
                st.success(f"✅ Correct — {st.session_state.correct}/{st.session_state.attempted}")
            else:
                st.error(f"❌ Incorrect — correct answer: {q.choices[q.answer]} • {st.session_state.correct}/{st.session_state.attempted}")

    c1, c2 = st.columns(2)
    c1.button("◀️ Previous", on_click=prev_q, disabled=st.session_state.current==0, use_container_width=True)
    c2.button("Next ▶️", on_click=next_q, disabled=st.session_state.current >= len(st.session_state.bank)-1, use_container_width=True)

if __name__ == "__main__":
    main()
