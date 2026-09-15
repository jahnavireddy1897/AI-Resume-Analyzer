from flask import Flask, render_template, request

app = Flask(__name__)

# List of skills
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
    "sap"
]


@app.route("/", methods=["GET", "POST"])
def home():

    result = None

    if request.method == "POST":

        resume = request.form["resume"].lower()
        job = request.form["job"].lower()

        resume_skills = []
        job_skills = []

        # Find skills in resume
        for skill in skills:
            if skill in resume:
                resume_skills.append(skill)

        # Find skills required for job
        for skill in skills:
            if skill in job:
                job_skills.append(skill)

        # Find matching skills
        matching_skills = []

        for skill in job_skills:
            if skill in resume_skills:
                matching_skills.append(skill)

        # Find missing skills
        missing_skills = []

        for skill in job_skills:
            if skill not in resume_skills:
                missing_skills.append(skill)

        # Calculate match percentage
        if len(job_skills) > 0:
            match = (
                len(matching_skills)
                / len(job_skills)
            ) * 100
        else:
            match = 0

        # Suggestion
        if match >= 80:
            suggestion = "Excellent match!"

        elif match >= 60:
            suggestion = "Good match. Improve your missing skills."

        else:
            suggestion = "You need to improve your skills."

        result = {
            "resume_skills": resume_skills,
            "job_skills": job_skills,
            "matching": matching_skills,
            "missing": missing_skills,
            "match": round(match, 2),
            "suggestion": suggestion
        }

    return render_template(
        "index.html",
        result=result
    )


if __name__ == "__main__":
    app.run(debug=True)
