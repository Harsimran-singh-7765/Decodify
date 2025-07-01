# qa_bot.py
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.docstore.document import Document
from dotenv import load_dotenv

load_dotenv()

def ask_question(query: str, vectorstore, readme_text=None):
   
    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        temperature=0.4
    )

    
    retriever = vectorstore.as_retriever(search_kwargs={"k": 5})
    relevant_docs = retriever.get_relevant_documents(query)

   
    if readme_text:
        readme_doc = Document(page_content=readme_text, metadata={"source": "README.md"})
        relevant_docs.insert(0, readme_doc)

  
    context = "\n\n".join([doc.page_content for doc in relevant_docs])

   
    prompt = f"""
You are an expert AI assistant helping the user understand a GitHub project.

Use the following context extracted from the project's README and codebase to answer the question:

---CONTEXT---
{context}
-------------

Now answer this question:
{query}
"""

    
    print("🧠 Final Prompt Preview:\n", prompt[:700])

   
    response = llm.invoke(prompt)
    return response.content if hasattr(response, "content") else str(response)

