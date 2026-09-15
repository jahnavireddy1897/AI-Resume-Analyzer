import streamlit as st
import re
from pypdf import PdfReader
import yake
from rapidfuzz import fuzz


# ---------------------------------------
# Page Configuration
# ---------------------------------------

st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="📄",
    layout="wide"
)


# ---------------------------------------
# Title
# ---------------------------------------

st.title("📄 AI Resume Analyzer")
st.write(
    "Upload your resume and paste a job description "
    "to automatically analyze your job match."
)


# ---------------------------------------
# PDF TEXT EXTRACTION
# ---------------------------------------

def extract_pdf_text(uploaded_file):

    reader = PdfReader(uploaded_file)

    text = ""

    for page in reader.pages:
        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n"

    return text


# ---------------------------------------
# CLEAN TEXT
# ---------------------------------------

def clean_text(text):

    text = text.lower()

    # Replace common symbols
    text = text.replace("&", " and ")

    # Remove unwanted characters
    text = re.sub(r"[^a-zA-Z0-9+#.\-/ ]", " ", text)

    # Remove multiple spaces
    text = re.sub(r"\s+", " ", text)

    return text.strip()


# ---------------------------------------
# KEYWORD EXTRACTION USING YAKE
# ---------------------------------------

def extract_keywords(text, max_keywords=25):

    if not text:
        return []

    # YAKE keyword extractor
    kw_extractor = yake.KeywordExtractor(
        lan="en",
        n=3,
        dedupLim=0.7,
        top=max_keywords
    )

    keywords = kw_extractor.extract_keywords(text)

    result = []

    for keyword, score in keywords:

        keyword = keyword.lower().strip()

        # Ignore very short keywords
        if len(keyword) < 2:
            continue

        # Remove common non-skill words
        ignored = {
            "candidate",
            "experience",
            "work",
            "working",
            "team",
            "role",
            "job",
            "company",
            "project",
            "projects",
            "responsibilities",
            "requirements",
            "required",
            "knowledge",
            "skills",
            "ability",
            "strong",
            "good",
            "excellent"
        }

        if keyword in ignored:
            continue

        if keyword not in result:
            result.append(keyword)

    return result


# ---------------------------------------
# TECHNICAL SKILL EXTRACTION
# ---------------------------------------

def extract_technical_terms(text):

    text = clean_text(text)

    terms = []

    # Technical words / phrases detected
    patterns = [
        r"\bpython\b",
        r"\bjava\b",
        r"\bc\+\+\b",
        r"\bc#\b",
        r"\bsql\b",
        r"\bmysql\b",
        r"\bpostgresql\b",
        r"\bmongodb\b",
        r"\bjavascript\b",
        r"\btypescript\b",
        r"\bhtml\b",
        r"\bcss\b",
        r"\breact\b",
        r"\bangular\b",
        r"\bnode\.?js\b",
        r"\bflask\b",
        r"\bdjango\b",
        r"\bfastapi\b",
        r"\bmachine learning\b",
        r"\bdeep learning\b",
        r"\bartificial intelligence\b",
        r"\bnatural language processing\b",
        r"\bnlp\b",
        r"\bcomputer vision\b",
        r"\bopencv\b",
        r"\byolo\b",
        r"\btensorflow\b",
        r"\bpytorch\b",
        r"\bscikit[- ]learn\b",
        r"\bpandas\b",
        r"\bnumpy\b",
        r"\bgit\b",
        r"\bgithub\b",
        r"\bdocker\b",
        r"\baws\b",
        r"\bazure\b",
        r"\brest api\b",
        r"\brestful api\b",
        r"\bapi\b",
        r"\bdata analysis\b",
        r"\bdata science\b",
        r"\bcloud computing\b",
        r"\bdevops\b",
        r"\blinux\b",
        r"\bpower bi\b",
        r"\btableau\b",
        r"\bexcel\b"
    ]

    for pattern in patterns:

        matches = re.findall(pattern, text)

        for match in matches:

            match = match.lower()

            if match not in terms:
                terms.append(match)

    return terms


# ---------------------------------------
# COMBINE KEYWORDS + TECHNICAL TERMS
# ---------------------------------------

def get_skills(text):

    keywords = extract_keywords(text)

    technical_terms = extract_technical_terms(text)

    combined = technical_terms.copy()

    for keyword in keywords:

        # Don't add very generic keywords
        if len(keyword.split()) <= 4:

            if keyword not in combined:
                combined.append(keyword)

    return combined[:30]


# ---------------------------------------
# NORMALIZE SKILL
# ---------------------------------------

def normalize_skill(skill):

    skill = skill.lower().strip()

    replacements = {
        "node js": "node.js",
        "nodejs": "node.js",
        "scikit learn": "scikit-learn",
        "restful api": "rest api",
        "natural language processing": "nlp",
        "artificial intelligence": "ai",
        "machine-learning": "machine learning",
        "deep-learning": "deep learning"
    }

    if skill in replacements:
        skill = replacements[skill]

    return skill


# ---------------------------------------
# MATCH SKILLS
# ---------------------------------------

def find_matches(required_skills, resume_skills):

    matching = []
    missing = []

    normalized_resume = [
        normalize_skill(skill)
        for skill in resume_skills
    ]

    for required in required_skills:

        required_normalized = normalize_skill(required)

        found = False

        for resume_skill in normalized_resume:

            # Exact match
            if required_normalized == resume_skill:
                found = True
                break

            # Partial/fuzzy match
            similarity = fuzz.ratio(
                required_normalized,
                resume_skill
            )

            if similarity >= 85:
                found = True
                break

        if found:
            matching.append(required)

        else:
            missing.append(required)

    return matching, missing


# ---------------------------------------
# MATCH PERCENTAGE
# ---------------------------------------

def calculate_percentage(required, matching):

    if not required:
        return 0

    percentage = (
        len(matching) / len(required)
    ) * 100

    return round(percentage, 2)


# ---------------------------------------
# USER INPUT
# ---------------------------------------

st.subheader("📄 Upload Resume")

uploaded_file = st.file_uploader(
    "Upload your resume in PDF format",
    type=["pdf"]
)


st.subheader("💼 Job Description")

job_description = st.text_area(
    "Paste the Job Description here",
    height=250,
    placeholder=(
        "Example:\n"
        "We are looking for a Python developer with "
        "experience in Flask, SQL, Machine Learning, "
        "REST APIs and Git."
    )
)


# ---------------------------------------
# ANALYZE BUTTON
# ---------------------------------------

if st.button(
    "🔍 Analyze Resume",
    use_container_width=True
):

    if uploaded_file is None:

        st.error("❌ Please upload a PDF resume.")

    elif not job_description.strip():

        st.error("❌ Please enter the Job Description.")

    else:

        with st.spinner(
            "Analyzing resume and job description..."
        ):

            # ---------------------------------------
            # Extract resume text
            # ---------------------------------------

            resume_text = extract_pdf_text(
                uploaded_file
            )

            if not resume_text.strip():

                st.error(
                    "Could not extract text from this PDF. "
                    "Please upload a text-based PDF."
                )

                st.stop()


            # ---------------------------------------
            # Extract skills
            # ---------------------------------------

            resume_skills = get_skills(
                resume_text
            )

            required_skills = get_skills(
                job_description
            )


            # ---------------------------------------
            # Find matching and missing skills
            # ---------------------------------------

            matching_skills, missing_skills = find_matches(
                required_skills,
                resume_skills
            )


            # ---------------------------------------
            # Calculate percentage
            # ---------------------------------------

            match_percentage = calculate_percentage(
                required_skills,
                matching_skills
            )


        # ---------------------------------------
        # RESULTS
        # ---------------------------------------

        st.divider()

        st.header("📊 Analysis Result")


        # ---------------------------------------
        # Score
        # ---------------------------------------

        col1, col2, col3 = st.columns(3)

        with col1:

            st.metric(
                "Match Percentage",
                f"{match_percentage}%"
            )

        with col2:

            st.metric(
                "Matching Skills",
                len(matching_skills)
            )

        with col3:

            st.metric(
                "Missing Skills",
                len(missing_skills)
            )


        # ---------------------------------------
        # Progress bar
        # ---------------------------------------

        st.progress(
            int(match_percentage)
        )


        # ---------------------------------------
        # Resume Skills
        # ---------------------------------------

        st.subheader("📄 Resume Skills")

        if resume_skills:

            for skill in resume_skills:
                st.write(f"• {skill}")

        else:

            st.warning(
                "No skills could be automatically detected "
                "from the resume."
            )


        # ---------------------------------------
        # Required Skills
        # ---------------------------------------

        st.subheader("🎯 Required Skills")

        if required_skills:

            for skill in required_skills:
                st.write(f"• {skill}")

        else:

            st.warning(
                "No skills could be automatically detected "
                "from the Job Description."
            )


        # ---------------------------------------
        # Matching Skills
        # ---------------------------------------

        st.subheader("✅ Matching Skills")

        if matching_skills:

            for skill in matching_skills:
                st.success(skill)

        else:

            st.info(
                "No matching skills were found."
            )


        # ---------------------------------------
        # Missing Skills
        # ---------------------------------------

        st.subheader("❌ Missing Skills")

        if missing_skills:

            for skill in missing_skills:
                st.error(skill)

        else:

            st.success(
                "🎉 No major missing skills detected!"
            )


        # ---------------------------------------
        # Recommendation
        # ---------------------------------------

        st.subheader("💡 Recommendation")

        if match_percentage >= 80:

            st.success(
                "Excellent match! Your resume strongly "
                "matches the Job Description."
            )

        elif match_percentage >= 60:

            st.info(
                "Good match. Consider improving the "
                "missing skills listed above."
            )

        elif match_percentage >= 40:

            st.warning(
                "Moderate match. Your resume needs "
                "improvement in several required areas."
            )

        else:

            st.error(
                "Low match. Consider developing the "
                "missing skills before applying."
            )
