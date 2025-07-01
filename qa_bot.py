# qa_bot.py
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.docstore.document import Document
from dotenv import load_dotenv

load_dotenv()

def ask_question(query: str, vectorstore, readme_text=None):
    # Init Gemini
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        temperature=0.4
    )

    # Retrieve top-k from vectorstore
    retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
    relevant_docs = retriever.get_relevant_documents(query)

    # Inject README at top if available
    if readme_text:
        readme_doc = Document(page_content=readme_text, metadata={"source": "README.md"})
        relevant_docs.insert(0, readme_doc)

    # Build context from retrieved + README
    context = "\n\n".join([doc.page_content for doc in relevant_docs])

    # Create final prompt
    prompt = f"""
You are an expert AI assistant helping the user understand a GitHub project.

Use the following context extracted from the project's README and codebase to answer the question:

---CONTEXT---
{context}
-------------

Now answer this question:
{query}
"""

    # Debug (optional)
    print("🧠 Final Prompt Preview:\n", prompt[:700])

    # Run LLM
    response = llm.invoke(prompt)
    return response.content if hasattr(response, "content") else str(response)

