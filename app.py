
import streamlit as st
import pandas as pd
import json
import sqlite3
import io
import os
from datetime import date
from pypdf import PdfReader
from google import genai

# ==========================================
# PAGE CONFIGURATION
# ==========================================

st.set_page_config(
    page_title="AI Professional Profile Builder",
    page_icon="🤖",
    layout="wide"
)

st.title("🤖 AI Professional Profile Builder")
st.caption("Create your professional profile with the power of Gemini AI.")

# ==========================================
# DATABASE
# ==========================================

DB_NAME = "profiles.db"

def initialize_database():
    conn = sqlite3.connect(DB_NAME)

    conn.execute("""
        CREATE TABLE IF NOT EXISTS profiles (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            age INTEGER,
            category TEXT,
            score INTEGER,
            profile TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


def save_profile(name, email, age, category, score, profile):

    conn = sqlite3.connect(DB_NAME)

    conn.execute("""
        INSERT INTO profiles
        (name, email, age, category, score, profile)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (name, email, age, category, score, profile))

    conn.commit()
    conn.close()


initialize_database()

# ==========================================
# SESSION STATE
# ==========================================

if "generated_profile" not in st.session_state:
    st.session_state.generated_profile = ""

if "submitted" not in st.session_state:
    st.session_state.submitted = False


# ==========================================
# AGE CATEGORY FUNCTION
# ==========================================

def calculate_age_category(age):

    if age < 13:
        return "Child"

    elif age < 18:
        return "Teenager"

    elif age < 30:
        return "Young Adult"

    elif age < 60:
        return "Adult"

    else:
        return "Senior"


# ==========================================
# SCORE RANGE FUNCTION
# ==========================================

def calculate_score_range(score):

    if score <= 20:
        return "Beginner (0-20)"

    elif score <= 40:
        return "Basic (21-40)"

    elif score <= 60:
        return "Intermediate (41-60)"

    elif score <= 80:
        return "Advanced (61-80)"

    else:
        return "Expert (81-100)"


# ==========================================
# GEMINI AI FUNCTION
# ==========================================

def generate_ai_profile(name, email, age, category,
                        education, skills, interests,
                        experience, score, extra_info):

    api_key = "api key"

    if not api_key:
        raise ValueError(
            "Gemini API key not found. Add GEMINI_API_KEY "
            "to Streamlit secrets or environment variables."
        )

    client = genai.Client(api_key=api_key)

    prompt = f"""
    You are a professional AI profile building agent.

    Create a professional, attractive and well-organized
    student or career profile using the following information.

    PERSONAL INFORMATION:
    Name: {name}
    Email: {email}
    Age: {age}
    Age Category: {category}

    EDUCATION:
    {education}

    SKILLS:
    {skills}

    INTERESTS:
    {interests}

    EXPERIENCE:
    {experience}

    SCORE: {score}/100

    SCORE CATEGORY:
    {calculate_score_range(score)}

    ADDITIONAL INFORMATION:
    {extra_info}

    Write the profile with these sections:

    1. Professional Introduction
    2. Personal Information
    3. Education
    4. Technical and Personal Skills
    5. Interests
    6. Experience
    7. Strengths
    8. Career Goals
    9. Professional Summary

    Instructions:
    - Use professional English.
    - Make the profile attractive and clear.
    - Do not invent qualifications or experience.
    - Do not expose unnecessary personal information.
    - Keep the profile realistic.
    """

    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=prompt
    )

    return response.text


# ==========================================
# FILE READER FUNCTION
# ==========================================

def read_uploaded_file(uploaded_file):

    file_name = uploaded_file.name.lower()

    try:

        if file_name.endswith(".txt"):

            return uploaded_file.getvalue().decode(
                "utf-8", errors="replace"
            )

        elif file_name.endswith(".csv"):

            df = pd.read_csv(uploaded_file)

            st.subheader("CSV Data Preview")

            st.dataframe(df, use_container_width=True)

            return df.to_string(index=False)

        elif file_name.endswith(".json"):

            data = json.load(uploaded_file)

            st.subheader("JSON Data")

            st.json(data)

            return json.dumps(data, indent=4)

        elif file_name.endswith(".pdf"):

            pdf = PdfReader(uploaded_file)

            text = ""

            for page in pdf.pages:
                text += page.extract_text() or ""

            return text

        else:

            st.error("Unsupported file format.")

            return None

    except Exception as e:

        st.error(f"File reading error: {e}")

        return None


# ==========================================
# SIDEBAR SETTINGS
# ==========================================

with st.sidebar:

    st.header("⚙️ Agent Settings")

    model = st.selectbox(
        "Select AI Model",
        ["gemini-3.6-flash"]
    )

    theme = st.selectbox(
        "Profile Style",
        ["Professional", "Modern", "Creative", "Academic"]
    )

    language = st.selectbox(
        "Profile Language",
        ["English", "Urdu"]
    )

    show_details = st.checkbox(
        "Show additional information",
        value=True
    )

    st.divider()


    st.caption("AI Profile Builder Agent v1.0")


# ==========================================
# MAIN TABS
# ==========================================

tab1, tab2, tab3, tab4 = st.tabs([
    "👤 Profile Builder",
    "📁 File Reader",
    "📊 Dashboard",
    "⚙️ Settings"
])


# ==========================================
# TAB 1: PROFILE BUILDER
# ==========================================

with tab1:

    st.header("Create Your Professional Profile")

    with st.form("profile_form"):

        col1, col2 = st.columns(2)

        with col1:

            name = st.text_input(
                "Full Name *",
                placeholder="Enter your name"
            )

            email = st.text_input(
                "Email Address *",
                placeholder="example@gmail.com"
            )

            dob = st.date_input(
                "Date of Birth",
                value=date(2008, 1, 1),
                min_value=date(1900, 1, 1),
                max_value=date.today()
            )

            education = st.text_input(
                "Education",
                placeholder="e.g. Computer Science Student"
            )

        with col2:

            skills = st.text_area(
                "Your Skills",
                placeholder="Python, HTML, Communication..."
            )

            interests = st.text_area(
                "Your Interests",
                placeholder="AI, Coding, Gaming..."
            )

            experience = st.text_area(
                "Experience",
                placeholder="Projects, internships, achievements..."
            )

        st.divider()

        st.subheader("Performance Information")

        score = st.slider(
            "Select Your Skill Score",
            min_value=0,
            max_value=100,
            value=50
        )

        extra_info = st.text_area(
            "Additional Information",
            placeholder="Tell us more about yourself..."
        )

        st.caption("* Required fields")

        submitted = st.form_submit_button(
            "🚀 Generate Professional Profile",
            use_container_width=True
        )

    # FORM VALIDATION

    if submitted:

        if not name.strip():

            st.error("Please enter your full name.")

        elif not email.strip() or "@" not in email:

            st.error("Please enter a valid email address.")

        elif not skills.strip():

            st.error("Please enter at least one skill.")

        else:

            today = date.today()

            age = today.year - dob.year - (
                (today.month, today.day) <
                (dob.month, dob.day)
            )

            category = calculate_age_category(age)

            score_range = calculate_score_range(score)

            st.success("Form submitted successfully!")

            st.subheader("Your Calculated Information")

            c1, c2, c3 = st.columns(3)

            c1.metric("Age", age)
            c2.metric("Age Category", category)
            c3.metric("Score", f"{score}/100")

            st.info(f"Score Range: {score_range}")

            # GENERATE AI PROFILE

            with st.spinner("Gemini AI is creating your profile..."):

                try:

                    profile = generate_ai_profile(
                        name,
                        email,
                        age,
                        category,
                        education,
                        skills,
                        interests,
                        experience,
                        score,
                        extra_info
                    )

                    st.session_state.generated_profile = profile

                    save_profile(
                        name,
                        email,
                        age,
                        category,
                        score,
                        profile
                    )

                    st.session_state.submitted = True

                    st.success(
                        "Your AI professional profile was generated and saved!"
                    )

                except Exception as e:

                    st.error(f"AI Generation Error: {e}")

    # DISPLAY GENERATED PROFILE

    if st.session_state.generated_profile:

        st.divider()

        st.subheader("✨ Your AI Generated Profile")

        st.markdown(
            st.session_state.generated_profile
        )

        st.download_button(
            label="⬇️ Download Profile as TXT",
            data=st.session_state.generated_profile,
            file_name="professional_profile.txt",
            mime="text/plain",
            use_container_width=True
        )

    # RESET BUTTON

    if st.button("🔄 Reset Inputs"):

        st.session_state.generated_profile = ""
        st.session_state.submitted = False

        st.rerun()


# ==========================================
# TAB 2: FILE READER
# ==========================================

with tab2:

    st.header("📁 Upload and Read Files")

    st.write(
        "Upload TXT, CSV, JSON or PDF files "
        "to read their contents."
    )

    uploaded_file = st.file_uploader(
        "Choose a file",
        type=["txt", "csv", "json", "pdf"]
    )

    if uploaded_file:

        st.success(
            f"File uploaded: {uploaded_file.name}"
        )

        if st.button("Read Uploaded File"):

            content = read_uploaded_file(uploaded_file)

            if content is not None:

                st.subheader("Extracted File Content")

                st.text_area(
                    "File Content",
                    value=content,
                    height=350
                )

                st.download_button(
                    "Download Extracted Text",
                    data=content,
                    file_name="extracted_content.txt",
                    mime="text/plain"
                )


# ==========================================
# TAB 3: DASHBOARD
# ==========================================

with tab3:

    st.header("📊 Saved Profiles Dashboard")

    conn = sqlite3.connect(DB_NAME)

    df = pd.read_sql_query(
        "SELECT * FROM profiles ORDER BY id DESC",
        conn
    )

    conn.close()

    if not df.empty:

        st.metric(
            "Total Saved Profiles",
            len(df)
        )

        st.subheader("Saved User Information")

        st.dataframe(
            df.drop(columns=["profile"]),
            use_container_width=True
        )

        selected_id = st.selectbox(
            "Select Profile ID",
            df["id"].tolist()
        )

        selected_profile = df[
            df["id"] == selected_id
        ].iloc[0]

        st.subheader("Profile Details")

        st.write("Name:", selected_profile["name"])
        st.write("Email:", selected_profile["email"])
        st.write("Age:", selected_profile["age"])
        st.write("Category:", selected_profile["category"])
        st.write("Score:", selected_profile["score"])

        st.download_button(
            "Download Selected Profile",
            data=selected_profile["profile"],
            file_name=f"profile_{selected_id}.txt",
            mime="text/plain"
        )

    else:

        st.info("No profiles have been saved yet.")


# ==========================================
# TAB 4: SETTINGS AND WIDGET VALUES
# ==========================================

with tab4:

    st.header("⚙️ Application Settings")

    st.subheader("Selected Settings")

    st.write("AI Model:", model)
    st.write("Profile Style:", theme)
    st.write("Language:", language)
    st.write("Show Additional Details:", show_details)

    st.divider()

    st.subheader("Widget Information")

    st.write("Application:", "AI Professional Profile Builder")
    st.write("Interface:", "Streamlit")
    st.write("AI Provider:", "Google Gemini")
    st.write("Database:", "SQLite")
    st.write("Supported Files:", "TXT, CSV, JSON, PDF")

    st.success("Application is running successfully!")

    st.caption("Developed using Python and Streamlit.")
