import streamlit as st
import google.generativeai as genai
import os
import json
import re
from dotenv import load_dotenv
from json_repair import repair_json
from fpdf import FPDF


# -----------------------------
# Gemini Setup
# -----------------------------

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")

genai.configure(api_key=api_key)

model = genai.GenerativeModel("gemini-flash-latest")


# -----------------------------
# Page Setup
# -----------------------------

st.set_page_config(
    page_title="Hook Mate - React Hooks AI Tutor",
    page_icon="🎓"
)


# -----------------------------
# Session State
# -----------------------------

if "quiz_data" not in st.session_state:
    st.session_state.quiz_data = None

if "history" not in st.session_state:
    st.session_state.history = []

if "quiz_saved" not in st.session_state:
    st.session_state.quiz_saved = False

if "ai_response" not in st.session_state:
    st.session_state.ai_response = ""


# -----------------------------
# Title
# -----------------------------

st.title("🎓 Hook Mate - React Hooks AI Tutor")

st.write(
    "Your personal AI tutor for learning React Hooks with explanations, examples, quizzes and feedback."
)


# -----------------------------
# Sidebar
# -----------------------------

st.sidebar.title("⚙️ Learning Settings")


level = st.sidebar.selectbox(
    "Difficulty Level",
    [
        "Beginner",
        "Intermediate",
        "Advanced"
    ]
)


# -----------------------------
# Inputs
# -----------------------------

topic = st.text_input(
    "📌 Enter React Hooks Topic",
    placeholder="Example: useState, useEffect, useContext"
)


activity = st.selectbox(
    "📚 Choose Activity",
    [
        "Explain Concept",
        "Real-Life Example",
        "Interactive Quiz",
        "Ask Anything"
    ]
)


# -----------------------------
# Generate Button
# -----------------------------

if st.button("🚀 Generate"):


    if topic == "":

        st.warning(
            "Please enter a topic"
        )


    else:


        tutor = f"""

        You are Hook Mate,
        a friendly AI tutor who teaches React Hooks.

        Explain concepts in simple beginner-friendly language.

        Give practical examples.
        Encourage learners.

        Difficulty Level:
        {level}

        """


        if activity == "Explain Concept":


            prompt = f"""

            {tutor}

            Explain:

            {topic}


            Include:

            1. Definition
            2. Key points
            3. Simple example
            4. Summary

            """


        elif activity == "Real-Life Example":


            prompt = f"""

            {tutor}

            Give one simple real-life example for:

            {topic}

            Explain how it connects with React Hooks.

            """


        elif activity == "Interactive Quiz":


            prompt = f"""

            Create a quiz about React Hooks topic:

            {topic}


            Return ONLY JSON.

            No markdown.
            No extra text.


            Format:

            {{
              "questions":[
                {{
                  "question":"",
                  "options":[
                    "",
                    "",
                    "",
                    ""
                  ],
                  "answer":"",
                  "explanation":""
                }}
              ]
            }}


            Create exactly 5 questions.

            """


        else:


            prompt = f"""

            {tutor}

            Answer this question:

            {topic}

            """



        try:


            with st.spinner(
                "Generating response..."
            ):


                response = model.generate_content(
                    prompt
                )


            if activity == "Interactive Quiz":


                clean_json = repair_json(
                    response.text
                )


                st.session_state.quiz_data = json.loads(
                    clean_json
                )


                st.session_state.quiz_saved = False



            else:


                st.subheader(
                    "📘 AI Response"
                )

                st.session_state.ai_response = response.text


                st.write(
                    st.session_state.ai_response
                )



        except Exception as e:


            st.error(
                f"Error: {e}"
            )



# -----------------------------
# Interactive Quiz UI
# -----------------------------

if st.session_state.quiz_data:


    st.divider()

    st.subheader(
        "📝 Interactive Quiz"
    )


    user_answers = {}


    for index, question in enumerate(
        st.session_state.quiz_data["questions"]
    ):


        st.write(
            f"### Question {index + 1}"
        )


        st.write(
            question["question"]
        )


        options = [
            "-- Select an answer --"
        ] + question["options"]


        choice = st.radio(
            "Choose answer:",
            options,
            key=f"question_{index}"
        )


        user_answers[index] = choice
        # -----------------------------
# Quiz Evaluation
# -----------------------------

    if st.button(
        "✅ Submit Quiz"
    ):


        score = 0


        st.subheader(
            "📊 Result"
        )


        for index, question in enumerate(
            st.session_state.quiz_data["questions"]
        ):


            st.write(
                f"### Question {index + 1}"
            )


            if user_answers[index] == question["answer"]:


                score += 1


                st.success(
                    "Correct ✅"
                )


            else:


                st.error(
                    "Wrong ❌"
                )


            st.write(
                f"Your Answer: {user_answers[index]}"
            )


            st.write(
                f"Correct Answer: {question['answer']}"
            )


            st.info(
                question["explanation"]
            )



        st.success(
            f"🎯 Final Score: {score}/5"
        )


        # -----------------------------
        # Save Learning History
        # -----------------------------


        if not st.session_state.quiz_saved:


            st.session_state.history.append(
                {
                    "topic": topic,
                    "activity": "Interactive Quiz",
                    "score": score,
                    "total": 5
                }
            )


            st.session_state.quiz_saved = True




# -----------------------------
# Progress Dashboard
# -----------------------------


st.sidebar.divider()


page = st.sidebar.radio(
    "Navigation",
    [
        "📘 Learning",
        "📊 My Progress"
    ]
)

if page == "📊 My Progress":


    st.title(
        "📊 My Learning Progress"
    )


    history = st.session_state.history



    if len(history) == 0:


        st.info(
            "No learning history available yet. Complete a quiz first."
        )



    else:


        total_quizzes = len(history)



        total_score = sum(
            item["score"]
            for item in history
        )



        average_score = (
            total_score /
            (total_quizzes * 5)
        ) * 100



        col1, col2, col3 = st.columns(3)



        col1.metric(
            "Quiz Completed",
            total_quizzes
        )



        col2.metric(
            "Average Score",
            f"{average_score:.0f}%"
        )



        col3.metric(
            "Topics Learned",
            len(
                set(
                    item["topic"]
                    for item in history
                )
            )
        )



        st.divider()



        st.subheader(
            "📚 Learning History"
        )



        for item in history:


            st.info(
                f"""
📌 Topic: {item['topic']}

🎯 Activity: {item['activity']}

⭐ Score: {item['score']}/{item['total']}
"""
            )



# -----------------------------
# Footer
# -----------------------------
# -----------------------------
# Download Notes
# -----------------------------

if st.session_state.ai_response:


    st.divider()

    st.subheader(
        "📥 Download Notes"
    )

    txt_data = st.session_state.ai_response

    # Remove emojis and unsupported Unicode characters
    txt_data = re.sub(r'[^\x00-\xFF]+', '', txt_data)


    st.download_button(
        label="⬇ Download TXT Notes",
        data=txt_data,
        file_name="Hook_Mate_Notes.txt",
        mime="text/plain"
    )



    pdf = FPDF()

    pdf.add_page()

    pdf.set_font("Helvetica", size=12)


    pdf.multi_cell(
        0,
        10,
        txt_data
    )


    pdf_output = bytes(pdf.output(dest="S"))


    st.download_button(
        label="📄 Download PDF Notes",
        data=pdf_output,
        file_name="Hook_Mate_Notes.pdf",
        mime="application/pdf"
    )


st.divider()


st.caption(
    "Built with ❤️ using Streamlit and Google Gemini AI | Hook Mate"
)