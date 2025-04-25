import streamlit as st
import os
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
from langchain_groq import ChatGroq

# Load environment variables
load_dotenv()

# Set your Groq API Key here
groq_api_key = "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"

# Function to dynamically generate follow-up questions
def generate_question(stage, disease=None, severity=None, medical_history=None):
    llm = ChatGroq(api_key=groq_api_key, model="gemma2-9b-it")  # Groq model
    prompt = f"""
    You are an experienced neurologist AI assistant. Based on the patient's details so far:
    - Neurological Complaint: {disease or "Not specified"}
    - Severity: {severity or "Not specified"}
    - Medical History: {medical_history or "Not specified"}

    Generate the next most relevant question to gather additional details about the patient's neurological issue.
    Only ask one question.
    """
    return llm.predict(prompt).strip()

# Function to get AI Doctor's response based on the user's input
def get_doctor_response(disease, severity, medical_history, follow_up):
    llm = ChatGroq(api_key=groq_api_key, model="gemma2-9b-it")
    
    template = f"""
    You are only an experienced neurologist. You are only allowed to provide neurology-related advice. You are unable to suggest any advice other than neurologist problems.

    The following details are provided by the patient:
    - Neurological Complaint: {disease}
    - Severity: {severity}
    - Medical History: {medical_history}
    - Follow-up Details: {follow_up}

    Only provide answers related to neurological care, treatment, and advice. If the problem is not neurology-related, inform the patient that you can only provide neurology-related advice.

    Provide a concise output including:
    1. Likely Neurological Conditions or Concerns
    2. Recommended Tests or Referrals (e.g., MRI, EEG, neurologist visit)
    3. Medication or Treatment Suggestions (if applicable)
    4. Lifestyle or Mental Wellness Tips
    """

    prompt = PromptTemplate(
        input_variables=["disease", "severity", "medical_history", "follow_up"],
        template=template,
    )
    response = llm.predict(
        prompt.format(
            disease=disease,
            severity=severity,
            medical_history=medical_history,
            follow_up=follow_up,
        )
    )
    return response.strip()

# Streamlit setup
st.set_page_config(page_title="Neurologist AI Chatbot", page_icon="🧠", layout="centered")

# Custom CSS
st.markdown("""
    <style>
    body {
        background-color: #f0f8ff;
        color: #333333;
        font-family: Arial, sans-serif;
    }
    .chat-box {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 16px;
        box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
        border-left: 5px solid #6495ED;
    }
    .user-text {
        text-align: left;
        font-weight: bold;
        color: #4169E1;
    }
    .bot-text {
        text-align: left;
        color: #444444;
        font-size: 16px;
        line-height: 1.5;
    }
    .stTextInput {
        margin-top: 20px;
        padding: 12px;
        border: 1px solid #cccccc;
        border-radius: 12px;
        font-size: 14px;
        background-color: #fdfdfd;
    }
    .stButton > button {
        margin: 0 10px;
        padding: 10px 18px;
        font-size: 14px;
        border-radius: 8px;
        background-color: #6495ED;
        color: white;
        border: none;
        cursor: pointer;
        transition: background-color 0.3s ease;
    }
    .stButton > button:hover {
        background-color: #4169E1;
    }
    h1 {
        color: #4169E1;
        font-size: 32px;
        margin-bottom: 20px;
    }
    .history-box {
        background-color: #f2f9ff;
        padding: 10px;
        border: 1px solid #e6e6e6;
        border-radius: 10px;
        margin-bottom: 10px;
        font-size: 14px;
    }
    </style>
    """, unsafe_allow_html=True)

st.title("Neurologist AI Chatbot 🧠")

# Initialize session states
if 'conversation' not in st.session_state:
    st.session_state['conversation'] = [{"role": "bot", "text": "Hello, I am your Neurologist AI. What neurological problem are you experiencing?"}]
if 'history' not in st.session_state:
    st.session_state['history'] = []
if 'stage' not in st.session_state:
    st.session_state['stage'] = 0
if 'user_input' not in st.session_state:
    st.session_state['user_input'] = ""

# Chat-like interaction
chat_placeholder = st.container()
st.session_state.user_input = st.text_input("Enter your response:", st.session_state.user_input, key="input_box")

# Stage-based conversation flow
if st.session_state.stage == 0 and st.session_state.user_input:
    st.session_state.disease = st.session_state.user_input
    st.session_state.conversation.append({"role": "user", "text": st.session_state.user_input})
    next_question = generate_question(stage=1, disease=st.session_state.disease)
    st.session_state.conversation.append({"role": "bot", "text": next_question})
    st.session_state.stage = 1
    st.session_state.user_input = ""

elif st.session_state.stage == 1 and st.session_state.user_input:
    st.session_state.severity = st.session_state.user_input
    st.session_state.conversation.append({"role": "user", "text": st.session_state.user_input})
    next_question = generate_question(stage=2, disease=st.session_state.disease, severity=st.session_state.severity)
    st.session_state.conversation.append({"role": "bot", "text": next_question})
    st.session_state.stage = 2
    st.session_state.user_input = ""

elif st.session_state.stage == 2 and st.session_state.user_input:
    st.session_state.medical_history = st.session_state.user_input
    st.session_state.conversation.append({"role": "user", "text": st.session_state.user_input})
    next_question = generate_question(stage=3, disease=st.session_state.disease, severity=st.session_state.severity, medical_history=st.session_state.medical_history)
    st.session_state.conversation.append({"role": "bot", "text": next_question})
    st.session_state.stage = 3
    st.session_state.user_input = ""

elif st.session_state.stage == 3 and st.session_state.user_input:
    st.session_state.follow_up = st.session_state.user_input
    st.session_state.conversation.append({"role": "user", "text": st.session_state.user_input})
    response = get_doctor_response(
        st.session_state.disease,
        st.session_state.severity,
        st.session_state.medical_history,
        st.session_state.follow_up,
    )
    st.session_state.conversation.append({"role": "bot", "text": response})
    st.session_state.history.append({
        "disease": st.session_state.disease,
        "severity": st.session_state.severity,
        "medical_history": st.session_state.medical_history,
        "follow_up": st.session_state.follow_up,
        "response": response,
    })
    st.session_state.stage = 0
    st.session_state.user_input = ""

# Display chat
with chat_placeholder:
    for message in st.session_state.conversation:
        if message["role"] == "user":
            st.markdown(f'<div class="chat-box user-text">You: {message["text"]}</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="chat-box bot-text">Doctor: {message["text"]}</div>', unsafe_allow_html=True)

# Button to view history
if st.button("View Past History"):
    if st.session_state.history:
        for idx, memory in enumerate(st.session_state.history):
            st.markdown(f"**Case {idx + 1}:**")
            st.markdown(f"- **Neurological Complaint:** {memory['disease']}")
            st.markdown(f"- **Severity:** {memory['severity']}")
            st.markdown(f"- **Medical History:** {memory['medical_history']}")
            st.markdown(f"- **Follow-Up Details:** {memory['follow_up']}")
            st.markdown(f"- **Response:** {memory['response']}")
            st.markdown("---")
    else:
        st.write("No history available.")