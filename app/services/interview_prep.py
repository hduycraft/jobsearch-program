from app.models.job import Job
from app.models.profile import Profile
from app.services.job_analyzer import analyze_job_description
from app.services.matcher import match_profile_to_job

SKILL_QUESTIONS: dict[str, list[str]] = {
    "Python": [
        "How do you structure a Python service so it is easy to test and maintain?",
        "How would you debug a slow Python API endpoint?",
    ],
    "FastAPI": [
        "How do FastAPI dependencies help organize request handling?",
        "How would you validate request and response data in a FastAPI endpoint?",
    ],
    "SQL": [
        "How would you find and fix an inefficient SQL query?",
        "When would you use a join instead of separate queries?",
    ],
    "PostgreSQL": [
        "How would you design a PostgreSQL table for reliable application tracking?",
        "What indexes would you consider for frequently searched job records?",
    ],
    "Docker": [
        "How would you explain the difference between an image and a container?",
        "How would you debug a service that works locally but fails in Docker?",
    ],
    "Azure": [
        "How would you describe the Azure services you have used in a project?",
        "What would you check first when an Azure-hosted app is unavailable?",
    ],
    "Azure DevOps": [
        "How would you structure a basic Azure DevOps pipeline for a Python API?",
        "How would you safely pass environment-specific configuration into a pipeline?",
    ],
    "Git": [
        "How do you keep a feature branch clean before opening a pull request?",
        "How would you recover from a bad commit without losing useful work?",
    ],
    "REST API": [
        "What makes an API endpoint RESTful?",
        "How would you choose status codes for create, validation, and not-found cases?",
    ],
    "Machine Learning": [
        "How would you explain a machine learning model's output to a non-technical user?",
        "How would you evaluate whether a model is good enough for production use?",
    ],
    "NLP": [
        "How would you extract useful signals from unstructured job descriptions?",
        "What are common limitations of keyword-based NLP?",
    ],
    "RAG": [
        "How would you explain retrieval-augmented generation in simple terms?",
        "What can go wrong if retrieved context is irrelevant or stale?",
    ],
    "LLM": [
        "How would you decide when to use an LLM instead of rule-based logic?",
        "How would you reduce hallucination risk in generated application materials?",
    ],
    "React": [
        "How do you manage component state in a React application?",
        "How would you break a complex page into reusable React components?",
    ],
    "Next.js": [
        "When would you use server-side rendering in Next.js?",
        "How would you structure API calls in a Next.js application?",
    ],
}

DEFAULT_TECHNICAL_QUESTIONS = [
    "How have you used this skill in a real project?",
    "What tradeoffs would you consider when applying this skill on a production team?",
]


def build_interview_prep(profile: Profile, job: Job) -> dict[str, object]:
    job_text = _job_text(job)
    job_analysis = analyze_job_description(job_text)
    job_skills = list(job_analysis["extracted_skills"])
    requirements = list(job_analysis["requirements_summary"])
    match_result = match_profile_to_job(profile, job)
    matched_skills = list(match_result["matched_skills"])
    missing_skills = list(match_result["missing_skills"])
    weak_areas = _weak_areas(missing_skills)

    return {
        "technical_questions": _technical_questions(job_skills),
        "hr_questions": _hr_questions(job),
        "study_topics": _study_topics(
            job_skills=job_skills,
            missing_skills=missing_skills,
            requirements=requirements,
        ),
        "weak_areas": weak_areas,
        "three_day_plan": _three_day_plan(
            job=job,
            matched_skills=matched_skills,
            missing_skills=missing_skills,
            requirements=requirements,
        ),
    }


def _job_text(job: Job) -> str:
    parts = [
        job.title,
        job.seniority,
        job.description,
        " ".join(job.requirements or []),
    ]
    return " ".join(part for part in parts if part)


def _technical_questions(job_skills: list[str]) -> list[dict[str, object]]:
    if not job_skills:
        return [
            {
                "skill": "General technical experience",
                "questions": [
                    "Walk through a technical project you are proud of.",
                    "How do you approach debugging an unfamiliar production issue?",
                ],
            }
        ]

    return [
        {
            "skill": skill,
            "questions": SKILL_QUESTIONS.get(skill, DEFAULT_TECHNICAL_QUESTIONS),
        }
        for skill in job_skills
    ]


def _hr_questions(job: Job) -> list[str]:
    return [
        f"Why are you interested in the {job.title} role at {job.company}?",
        "Tell me about a time you learned a new skill quickly for a project.",
        "Tell me about a time you handled unclear requirements or changing priorities.",
        "What kind of team environment helps you do your best work?",
    ]


def _study_topics(
    job_skills: list[str],
    missing_skills: list[str],
    requirements: list[str],
) -> list[str]:
    topics: list[str] = []

    for skill in missing_skills:
        topics.append(f"Review the basics of {skill} and prepare an honest gap explanation.")

    for skill in job_skills:
        if skill not in missing_skills:
            topics.append(f"Prepare a project example that demonstrates {skill}.")

    for requirement in requirements[:2]:
        topics.append(f"Practice explaining this job requirement: {requirement}")

    if not topics:
        topics.append("Review your strongest project and prepare a clear technical walkthrough.")

    return topics[:8]


def _weak_areas(missing_skills: list[str]) -> list[str]:
    if not missing_skills:
        return ["No weak areas were found from the known skill list."]

    return [
        f"{skill} is mentioned in the job but not listed in the profile."
        for skill in missing_skills
    ]


def _three_day_plan(
    job: Job,
    matched_skills: list[str],
    missing_skills: list[str],
    requirements: list[str],
) -> list[dict[str, object]]:
    day_one_tasks = [
        f"Reread the {job.title} description and mark the top responsibilities.",
        "Prepare a 2-minute walkthrough of your most relevant project.",
    ]
    if matched_skills:
        day_one_tasks.append(
            f"Prepare examples for matched skills: {_format_list(matched_skills)}."
        )

    day_two_tasks = [
        "Practice technical questions for the required skills.",
        "Write short STAR-format notes for two project or teamwork stories.",
    ]
    if missing_skills:
        day_two_tasks.append(
            f"Study weak areas honestly: {_format_list(missing_skills)}."
        )

    day_three_tasks = [
        "Run a mock interview and answer questions out loud.",
        f"Prepare thoughtful questions about {job.company}, the team, and success metrics.",
    ]
    if requirements:
        day_three_tasks.append("Review the requirement summary and connect it to your examples.")

    return [
        {"day": 1, "focus": "Map the role to your real experience", "tasks": day_one_tasks},
        {"day": 2, "focus": "Practice technical and behavioral answers", "tasks": day_two_tasks},
        {"day": 3, "focus": "Mock interview and final polish", "tasks": day_three_tasks},
    ]


def _format_list(items: list[str]) -> str:
    if not items:
        return ""
    if len(items) == 1:
        return items[0]
    if len(items) == 2:
        return f"{items[0]} and {items[1]}"
    return f"{', '.join(items[:-1])}, and {items[-1]}"
