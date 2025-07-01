from pathlib import Path
from langchain_google_genai import ChatGoogleGenerativeAI
import os
llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash", temperature=0.3)

def build_file_tree(root_dir):
    IGNORE_DIRS = {".git", "__pycache__", ".ipynb_checkpoints", "venv", "env", ".idea", ".vscode", ".DS_Store"}
    IGNORE_FILES = {".DS_Store"}

    tree = {}

    for root, dirs, files in os.walk(root_dir):
        # Remove ignored dirs in-place to prevent recursion
        dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]

        relative_root = os.path.relpath(root, root_dir)
        current = tree
        if relative_root != ".":
            for part in relative_root.split(os.sep):
                current = current.setdefault(part, {})

        for f in files:
            if f not in IGNORE_FILES:
                current[f] = os.path.join(root, f)

    return tree



def describe_code_file(content: str):
    prompt = f"""You are a code explainer.

    Analyze the following code and give:
    1. Description (what does this file do?)
    2. Usage (how and where could it be used?)
    3. Importance (how important is it in a full-stack repo?)

    CODE:
    ---
    {content[:3000]}
    ---

    Answer in this format:
    Description: ...
    Usage: ...
    Importance: ...
    """

    try:
        response = llm.invoke(prompt)
        raw = response.content if hasattr(response, "content") else str(response)

        description = usage = importance = "Not available"

        if "Description:" in raw:
            description = raw.split("Description:")[1].split("Usage:")[0].strip()
        if "Usage:" in raw:
            usage = raw.split("Usage:")[1].split("Importance:")[0].strip()
        if "Importance:" in raw:
            importance = raw.split("Importance:")[1].strip()

        return description, usage, importance

    except Exception as e:
        return f"❌ Failed to generate: {e}", "", ""
