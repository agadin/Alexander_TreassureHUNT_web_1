import streamlit as st
import json
import os

#hide top color bar
hide_decoration_bar_style = '''
    <style>
        header {visibility: hidden;}
    </style>
'''
st.markdown(hide_decoration_bar_style, unsafe_allow_html=True)

if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

def check_password():
    if st.session_state["password"] == "softtissue":  # Replace 'your_password' with your desired password
        st.session_state.authenticated = True
        st.session_state.password = ''  # Clear password input after successful authentication
    else:
        st.error("Incorrect password")

# If the user is not authenticated, show the password input
if not st.session_state.authenticated:
    st.write("User: Lakelab")
    st.session_state["password"] = st.text_input("Password", type="password")
    st.button("Submit", on_click=check_password)

# If the user is authenticated, display the main content
if st.session_state.authenticated:
    
    if 'current_file' not in st.session_state:
        st.session_state.current_file = 1
    if 'current_question' not in st.session_state:
        st.session_state.current_question = 0
    if 'score' not in st.session_state:
        st.session_state.score = 0
    if 'attempted' not in st.session_state:
        st.session_state.attempted = 0
    if 'wrong' not in st.session_state:
        st.session_state.wrong = 0
    if 'submitted' not in st.session_state:
        st.session_state.submitted = False
    if 'selected_answer' not in st.session_state:
        st.session_state.selected_answer = None
    
    def load_json(file_number):
        file_name = f'passage{file_number}.json'
        if os.path.exists(file_name):
            with open(file_name, 'r') as f:
                return json.load(f)
        return None
    
    
    def calculate_final_score():
        if st.session_state.attempted > 0:
            score = 132 - st.session_state.wrong
            return score
        return 122
    
    def display_passage():
        data = load_json(st.session_state.current_file)
        if data:
            st.write(f"**Passage {st.session_state.current_file}**")
            st.write(data['passage'])
            return data
        else:
            st.write("No more passages available.")
            return None
    
    
    def display_question(data):
        question_set = data['questions'][st.session_state.current_question]
        st.write(f"**Question {st.session_state.current_question + 1}:** {question_set['question']}")
        options = question_set['options']
    
        st.session_state.selected_answer = st.radio('Select your answer:', options)
        
        return question_set['correct']
    
    
    def next_question():
        st.session_state.submitted = False  # Reset submit state
        st.session_state.current_question += 1
    
        if st.session_state.current_question >= len(st.session_state.data['questions']):
            st.session_state.current_file += 1
            st.session_state.current_question = 0
            st.session_state.data = load_json(st.session_state.current_file)
    
    
    st.session_state.data = load_json(st.session_state.current_file) if 'data' not in st.session_state else st.session_state.data
    
    
    if st.session_state.data:
        display_passage()
    
    
        correct_answer = display_question(st.session_state.data)
    
        if st.button('Submit') and not st.session_state.submitted:
            st.session_state.attempted += 1
            st.session_state.submitted = True
    
            if st.session_state.selected_answer == correct_answer:
                st.session_state.score += 1
            else:
                st.session_state.wrong += 1
                print("Wrong")
                print(st.session_state.wrong)
            
            next_question()
            st.experimental_rerun()
    
    
    if not load_json(st.session_state.current_file):
        final_score = calculate_final_score()
        st.write(f"**Your final score is: {final_score}**")
        if final_score > 128:
            st.write("**Good job!**")
        else:
            st.write("**Refresh and try again!**")
