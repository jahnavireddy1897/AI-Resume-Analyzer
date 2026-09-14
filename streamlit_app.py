import streamlit as st

st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="📄"
)

st.title("📄 AI Resume Analyzer")
st.write("Resume & Job Matching System")

skills = [
    "python",
    "java",
    "c",
    "c++",
    "sql",
    "html",
    "css",
    "javascript",
    "machine learning",
    "flask",
    "django",
    "aws",
    "mongodb",
    "git"
]

resume = st.text_area(
    "Enter Your Resume",
    placeholder="Example: I know Python, Java, SQL, HTML and Machine Learning."
)

job = st.text_area(
    "Enter Job Description",
    placeholder="Example: Required skills are Python, SQL, Machine Learning and AWS."
)

if st.button("Analyze Resume"):

    resume = resume.lower()
    job = job.lower()

    resume_skills = []
    job_skills = []

    for skill in skills:
        if skill in resume:
            resume_skills.append(skill)

    for skill in skills:
        if skill in job:
            job_skills.append(skill)

    matching_skills = []

    for skill in job_skills:
        if skill in resume_skills:
            matching_skills.append(skill)

    missing_skills = []

    for skill in job_skills:
        if skill not in resume_skills:
            missing_skills.append(skill)

    if len(job_skills) > 0:
        match = (len(matching_skills) / len(job_skills)) * 100
    else:
        match = 0

    st.subheader("📊 Analysis Result")

    st.write("### Resume Skills")
    st.write(resume_skills)

    st.write("### Required Skills")
    st.write(job_skills)

    st.write("### ✅ Matching Skills")
    st.write(matching_skills)

    st.write("### ❌ Missing Skills")
    st.write(missing_skills)

    st.metric("Job Match", f"{match:.2f}%")

    if match >= 80:
        st.success("Excellent match!")
    elif match >= 60:
        st.info("Good match. Improve your missing skills.")
    else:
        st.warning("You need to improve your skills.")