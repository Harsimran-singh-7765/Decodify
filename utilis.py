import os
from pathlib import Path
from collections import Counter

# Basic extension to language mapping
EXT_TO_LANG = {
    # Web & Frontend
    ".html": "HTML",
    ".htm": "HTML",
    ".css": "CSS",
    ".scss": "SASS",
    ".sass": "SASS",
    ".less": "LESS",
    ".js": "JavaScript",
    ".mjs": "JavaScript",
    ".ts": "TypeScript",
    ".tsx": "TypeScript JSX",
    ".jsx": "JavaScript JSX",

    # Backend & Scripting
    ".py": "Python",
    ".rb": "Ruby",
    ".php": "PHP",
    ".java": "Java",
    ".kt": "Kotlin",
    ".go": "Go",
    ".rs": "Rust",
    ".c": "C",
    ".cpp": "C++",
    ".cs": "C#",
    ".sh": "Shell",
    ".bat": "Batch",
    ".pl": "Perl",
    ".lua": "Lua",

    # Data & Config
    ".json": "JSON",
    ".yaml": "YAML",
    ".yml": "YAML",
    ".xml": "XML",
    ".toml": "TOML",
    ".ini": "INI",
    ".env": "ENV",

    # Markup & Docs


    # Notebook & Data Science
    ".ipynb": "Jupyter Notebook",
    ".r": "R",
    ".jl": "Julia",

    # SQL & DB
    ".sql": "SQL",

    # Other
    ".dockerfile": "Dockerfile",
    "Dockerfile": "Dockerfile",  
    ".makefile": "Makefile",
    "Makefile": "Makefile",      

   
    ".log": "Log File",
    ".gitignore": "Git Ignore",
}


def analyze_languages(repo_path: str) -> dict:
    """Analyzes file extensions and names to estimate language usage."""
    counter = Counter()

    for file_path in Path(repo_path).rglob("*"):
        if file_path.is_file():
            ext = file_path.suffix.lower()
            name = file_path.name.lower()

            
            lang = EXT_TO_LANG.get(ext)

            
            if not lang:
                lang = EXT_TO_LANG.get(name)

            if lang:
                counter[lang] += 1

    total = sum(counter.values())
    if total == 0:
        return {}

    percentages = {lang: round((count / total) * 100, 2) for lang, count in counter.items()}
    return dict(sorted(percentages.items(), key=lambda x: x[1], reverse=True))
