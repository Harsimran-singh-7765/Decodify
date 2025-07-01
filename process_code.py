import os
import time
import json
from pathlib import Path
from dotenv import load_dotenv
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_community.vectorstores import FAISS
from langchain_community.document_loaders import TextLoader
from langchain.docstore.document import Document
from langchain.vectorstores import FAISS as FAISS_alt 


load_dotenv()

llm = ChatGoogleGenerativeAI(
    model="gemini-2.0-flash",
    temperature=0.2
)


def load_and_embed_repo(repo_path: str, db_path: str = "faiss_index"):
    if os.path.exists(db_path):
        print("🧠 Loading existing FAISS index...")
        vectorstore = FAISS.load_local(
            db_path,
            GoogleGenerativeAIEmbeddings(model="models/embedding-001"),
            allow_dangerous_deserialization=True
        )    
        
        summary = None
        readme_content = None
        meta_path = os.path.join(db_path, "meta.json")

        if os.path.exists(meta_path):
            try:
                with open(meta_path, "r", encoding="utf-8") as f:
                    meta = json.load(f)
                    summary = meta.get("summary")
                    readme_content = meta.get("readme")
                    print("📦 Loaded metadata from previous run.")
            except Exception as e:
                print(f"⚠️ Failed to load meta.json: {e}")


        if not summary or not readme_content:
            readme_path = Path(repo_path) / "README.md"
            if readme_path.exists():
                try:
                    with open(readme_path, "r", encoding="utf-8") as f:
                        readme_content = f.read().strip()
                        print("📜 README Preview:", readme_content[:300])
                    prompt = f"Summarize the GitHub project using this README:\n\n{readme_content}"
                    response = llm.invoke(prompt)
                    summary = response.content if hasattr(response, "content") else str(response)
                    print("🧾 Regenerated README Summary:\n", summary)

                    # 💾 Save meta again
                    with open(meta_path, "w", encoding="utf-8") as f:
                        json.dump({
                            "summary": summary,
                            "readme": readme_content
                        }, f, indent=2)
                    print("💾 meta.json updated.")
                except Exception as e:
                    print(f"❌ Could not regenerate summary: {e}")
            else:
                print("❌ README.md not found. Can't regenerate summary.")

        return vectorstore, summary, readme_content

    print("📚 Loading and embedding repository files...")
    allowed_ext = [".py", ".md", ".txt", ".json", ".js", ".ts", ".java", ".c", ".cpp",".tsx",".html",".css"]
    docs = []

    for filepath in Path(repo_path).rglob("*"):
        if filepath.suffix.lower() in allowed_ext and "__pycache__" not in str(filepath).lower():
            try:
                loader = TextLoader(str(filepath), autodetect_encoding=True)
                docs.extend(loader.load())
            except Exception as e:
                print(f"❌ Error loading {filepath}: {e}")

    if not docs:
        raise ValueError("🚨 No valid documents found in the repo!")

    
    readme_docs = [doc for doc in docs if "readme" in doc.metadata['source'].lower()]
    print("📄 README files found:", [doc.metadata['source'] for doc in readme_docs])
    readme_content = None
    readme_path = Path(repo_path) / "README.md"

    if readme_path.exists():
        try:
            with open(readme_path, "r", encoding="utf-8") as f:
                readme_content = f.read().strip()
                print("📜 README Preview:", readme_content[:300])
        except Exception as e:
            print(f"❌ Could not read README.md: {e}")
    else:
        print("❌ README.md not found in repo.")

    summary = None
    if readme_content:
        prompt = f"Summarize the GitHub project using this README:\n\n{readme_content}"
        response = llm.invoke(prompt)
        summary = response.content if hasattr(response, "content") else str(response)
        print("🧾 README Summary:\n", summary)
    else:
        print("⚠️ README content empty or unreadable.")

   
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=2000,
        chunk_overlap=300,
        separators=["\n\n", "\n", " ", ""]
    )
    chunks = splitter.split_documents(docs)

    embeddings = GoogleGenerativeAIEmbeddings(model="models/embedding-001")
    all_embeddings = []
    batch_size = 40
    batch_delay = 10

    print(f"📦 Total chunks to embed: {len(chunks)}")

    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i + batch_size]
        try:
            print(f"⚙️ Embedding batch {i} - {i + len(batch)}...")
            vectors = embeddings.embed_documents([doc.page_content for doc in batch])
            for doc, vector in zip(batch, vectors):
                doc.metadata["embedding"] = vector
                all_embeddings.append(doc)
        except Exception as e:
            print(f"❌ Error embedding batch {i}-{i + len(batch)}: {e}")
        time.sleep(batch_delay)

    vectorstore = FAISS_alt.from_documents(all_embeddings, embeddings)
    vectorstore.save_local(db_path)
    print(f"✅ Vectorstore saved at: {db_path}")


    try:
        meta = {
            "summary": summary,
            "readme": readme_content
        }
        with open(os.path.join(db_path, "meta.json"), "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2)
        print("💾 Saved summary + readme in meta.json")
    except Exception as e:
        print(f"⚠️ Failed to save meta.json: {e}")

    return vectorstore, summary, readme_content
