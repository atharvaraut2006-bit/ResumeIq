from app.models.skill import Skill, SkillAlias
from app import db
import logging

logger = logging.getLogger(__name__)

INITIAL_KNOWLEDGE_BASE = [
    {
        "canonical_name": "JavaScript",
        "category": "Programming Languages",
        "aliases": ["js", "javascript", "java script"]
    },
    {
        "canonical_name": "Python",
        "category": "Programming Languages",
        "aliases": ["python", "py"]
    },
    {
        "canonical_name": "Java",
        "category": "Programming Languages",
        "aliases": ["java"]
    },
    {
        "canonical_name": "C++",
        "category": "Programming Languages",
        "aliases": ["c++", "cpp"]
    },
    {
        "canonical_name": "C",
        "category": "Programming Languages",
        "aliases": ["c"]
    },
    {
        "canonical_name": "TypeScript",
        "category": "Programming Languages",
        "aliases": ["typescript", "ts"]
    },
    {
        "canonical_name": "Go",
        "category": "Programming Languages",
        "aliases": ["go", "golang"]
    },
    {
        "canonical_name": "Rust",
        "category": "Programming Languages",
        "aliases": ["rust"]
    },
    {
        "canonical_name": "C#",
        "category": "Programming Languages",
        "aliases": ["c#", "csharp", ".net"]
    },
    {
        "canonical_name": "PHP",
        "category": "Programming Languages",
        "aliases": ["php"]
    },
    {
        "canonical_name": "Kotlin",
        "category": "Programming Languages",
        "aliases": ["kotlin"]
    },
    {
        "canonical_name": "Swift",
        "category": "Programming Languages",
        "aliases": ["swift"]
    },
    {
        "canonical_name": "HTML",
        "category": "Web Development",
        "aliases": ["html", "html5"]
    },
    {
        "canonical_name": "CSS",
        "category": "Web Development",
        "aliases": ["css", "css3"]
    },
    {
        "canonical_name": "React",
        "category": "Web Development",
        "aliases": ["react", "react.js", "reactjs"]
    },
    {
        "canonical_name": "Angular",
        "category": "Web Development",
        "aliases": ["angular", "angularjs"]
    },
    {
        "canonical_name": "Vue",
        "category": "Web Development",
        "aliases": ["vue", "vue.js", "vuejs"]
    },
    {
        "canonical_name": "Node.js",
        "category": "Web Development",
        "aliases": ["node", "nodejs", "node.js"]
    },
    {
        "canonical_name": "Express",
        "category": "Web Development",
        "aliases": ["express", "express.js", "expressjs"]
    },
    {
        "canonical_name": "Next.js",
        "category": "Web Development",
        "aliases": ["next.js", "nextjs", "next"]
    },
    {
        "canonical_name": "Flask",
        "category": "Web Development",
        "aliases": ["flask"]
    },
    {
        "canonical_name": "Django",
        "category": "Web Development",
        "aliases": ["django"]
    },
    {
        "canonical_name": "Spring Boot",
        "category": "Web Development",
        "aliases": ["spring boot", "springboot", "spring"]
    },
    {
        "canonical_name": "REST API",
        "category": "Web Development",
        "aliases": ["rest", "rest api", "restful", "restful api", "rest apis"]
    },
    {
        "canonical_name": "MySQL",
        "category": "Databases",
        "aliases": ["mysql"]
    },
    {
        "canonical_name": "PostgreSQL",
        "category": "Databases",
        "aliases": ["postgresql", "postgres"]
    },
    {
        "canonical_name": "SQLite",
        "category": "Databases",
        "aliases": ["sqlite"]
    },
    {
        "canonical_name": "MongoDB",
        "category": "Databases",
        "aliases": ["mongodb", "mongo"]
    },
    {
        "canonical_name": "Oracle",
        "category": "Databases",
        "aliases": ["oracle", "oracle db"]
    },
    {
        "canonical_name": "Redis",
        "category": "Databases",
        "aliases": ["redis"]
    },
    {
        "canonical_name": "SQL",
        "category": "Databases",
        "aliases": ["sql"]
    },
    {
        "canonical_name": "NoSQL",
        "category": "Databases",
        "aliases": ["nosql"]
    },
    {
        "canonical_name": "Machine Learning",
        "category": "Artificial Intelligence",
        "aliases": ["machine learning", "machine-learning", "ml"]
    },
    {
        "canonical_name": "Deep Learning",
        "category": "Artificial Intelligence",
        "aliases": ["deep learning", "dl"]
    },
    {
        "canonical_name": "Natural Language Processing",
        "category": "Artificial Intelligence",
        "aliases": ["natural language processing", "nlp"]
    },
    {
        "canonical_name": "Computer Vision",
        "category": "Artificial Intelligence",
        "aliases": ["computer vision", "cv"]
    },
    {
        "canonical_name": "TensorFlow",
        "category": "Artificial Intelligence",
        "aliases": ["tensorflow", "tf"]
    },
    {
        "canonical_name": "PyTorch",
        "category": "Artificial Intelligence",
        "aliases": ["pytorch"]
    },
    {
        "canonical_name": "Keras",
        "category": "Artificial Intelligence",
        "aliases": ["keras"]
    },
    {
        "canonical_name": "NumPy",
        "category": "Data Science",
        "aliases": ["numpy"]
    },
    {
        "canonical_name": "Pandas",
        "category": "Data Science",
        "aliases": ["pandas"]
    },
    {
        "canonical_name": "Matplotlib",
        "category": "Data Science",
        "aliases": ["matplotlib"]
    },
    {
        "canonical_name": "Seaborn",
        "category": "Data Science",
        "aliases": ["seaborn"]
    },
    {
        "canonical_name": "Scikit-learn",
        "category": "Artificial Intelligence",
        "aliases": ["scikit-learn", "scikit learn", "sklearn"]
    },
    {
        "canonical_name": "AWS",
        "category": "Cloud",
        "aliases": ["aws", "amazon web services"]
    },
    {
        "canonical_name": "Azure",
        "category": "Cloud",
        "aliases": ["azure", "microsoft azure"]
    },
    {
        "canonical_name": "Google Cloud",
        "category": "Cloud",
        "aliases": ["google cloud", "gcp", "google cloud platform"]
    },
    {
        "canonical_name": "EC2",
        "category": "Cloud",
        "aliases": ["ec2", "amazon ec2"]
    },
    {
        "canonical_name": "S3",
        "category": "Cloud",
        "aliases": ["s3", "amazon s3"]
    },
    {
        "canonical_name": "Lambda",
        "category": "Cloud",
        "aliases": ["lambda", "aws lambda"]
    },
    {
        "canonical_name": "Cloud Computing",
        "category": "Cloud",
        "aliases": ["cloud computing"]
    },
    {
        "canonical_name": "Docker",
        "category": "DevOps",
        "aliases": ["docker"]
    },
    {
        "canonical_name": "Kubernetes",
        "category": "DevOps",
        "aliases": ["kubernetes", "k8s"]
    },
    {
        "canonical_name": "Jenkins",
        "category": "DevOps",
        "aliases": ["jenkins"]
    },
    {
        "canonical_name": "GitHub Actions",
        "category": "DevOps",
        "aliases": ["github actions"]
    },
    {
        "canonical_name": "CI/CD",
        "category": "DevOps",
        "aliases": ["ci/cd", "ci-cd", "continuous integration", "continuous deployment"]
    },
    {
        "canonical_name": "Terraform",
        "category": "DevOps",
        "aliases": ["terraform"]
    },
    {
        "canonical_name": "Git",
        "category": "Version Control",
        "aliases": ["git"]
    },
    {
        "canonical_name": "GitHub",
        "category": "Version Control",
        "aliases": ["github"]
    },
    {
        "canonical_name": "GitLab",
        "category": "Version Control",
        "aliases": ["gitlab"]
    },
    {
        "canonical_name": "Bitbucket",
        "category": "Version Control",
        "aliases": ["bitbucket"]
    },
    {
        "canonical_name": "Operating Systems",
        "category": "Core Subjects",
        "aliases": ["os", "operating systems", "operating system", "operating system (os)", "os (operating systems)"]
    },
    {
        "canonical_name": "DBMS",
        "category": "Core Subjects",
        "aliases": ["dbms", "database management", "database management system", "database management systems", "dbms (database management system)", "database management system (dbms)"]
    },
    {
        "canonical_name": "Data Structures & Algorithms",
        "category": "Core Subjects",
        "aliases": ["dsa", "data structures", "algorithms", "data structures & algorithms", "data structures and algorithms", "data structures & algorithm", "data structure and algorithm", "dsa (data structures and algorithms)", "data structures and algorithms (dsa)"]
    },
    {
        "canonical_name": "Computer Networks",
        "category": "Core Subjects",
        "aliases": ["cn", "computer networks", "networking", "computer network", "computer networks (cn)"]
    },
    {
        "canonical_name": "Object-Oriented Programming",
        "category": "Core Subjects",
        "aliases": ["oops", "oop", "object oriented programming", "object-oriented programming", "oops (object oriented programming)", "object oriented programming (oops)", "oops/oop"]
    },
    {
        "canonical_name": "Software Engineering",
        "category": "Core Subjects",
        "aliases": ["software engineering", "sdlc", "software development life cycle"]
    },
    {
        "canonical_name": "Web Technologies",
        "category": "Web Development",
        "aliases": ["web technologies", "web development", "web dev", "web technology"]
    }
]

def initialize_knowledge_base():
    """
    Populates/syncs the database with the skill knowledge base.
    """
    logger.info("Syncing skill knowledge base...")
    
    for skill_data in INITIAL_KNOWLEDGE_BASE:
        skill = Skill.query.filter_by(canonical_name=skill_data["canonical_name"]).first()
        if not skill:
            skill = Skill(
                canonical_name=skill_data["canonical_name"],
                category=skill_data["category"]
            )
            db.session.add(skill)
            db.session.flush()
        
        for alias_name in skill_data["aliases"]:
            clean_alias = alias_name.lower()
            existing_alias = SkillAlias.query.filter_by(alias=clean_alias).first()
            if not existing_alias:
                alias = SkillAlias(
                    skill_id=skill.id,
                    alias=clean_alias
                )
                db.session.add(alias)
            
    try:
        db.session.commit()
        logger.info("Successfully populated/synced skill knowledge base.")
    except Exception as e:
        db.session.rollback()
        logger.error(f"Failed to populate skill knowledge base: {e}")
