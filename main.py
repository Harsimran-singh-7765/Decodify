import streamlit as st 
from clone_repo import clone_repo 
from process_code import load_and_embed_repo 
from qa_bot import ask_question
# from file_tree_utils import build_file_tree, describe_code_file
import os

st.set_page_config(page_title = "Decodify",layout="wide")
st.title("🚀 Decodify  -  GitHub Repo Decoded ")

st.sidebar.title("🚀Decodify")
page = st.sidebar.radio("Go to", ["🏠 Home", "🤖 Chatbot", "📂 Decode", "📈 Rate My Repo", "ℹ️ About"])

for key in ["vectorstore", "repo_url", "repo_path", "chat_history", "readme_summary", "readme_raw", "selected_file_path"]:

    if key not in st.session_state:
        st.session_state[key] = None if key != "chat_history" else []

 
if page == "🏠 Home":
    st.subheader("🔗 Enter GitHub Repo URL:")
    
    
    if st.session_state.repo_url:
        st.success(f"✅ Repo Loaded: `{st.session_state.repo_url}`")
        st.info("🔄 Refresh the app or click below to enter a new repo.")

    else:
       
        repo_url = st.text_input("Paste your GitHub repo URL")

        if repo_url:
            with st.spinner("🔄 Cloning repo..."):
                repo_path = clone_repo(repo_url)
                if repo_path is None:
                    st.error("❌ Failed to clone the repo. Please check the URL.")
                else:
                    st.session_state.repo_url = repo_url
                    st.session_state.repo_path = repo_path

            with st.spinner("📦 Processing and embedding repo..."):
                vectorstore, summary, readme_content = load_and_embed_repo(repo_path)
                st.session_state.vectorstore = vectorstore
                st.session_state.readme_summary = summary or None
                st.session_state.readme_raw = readme_content or None
                st.session_state.chat_history = []
                st.session_state.selected_file_path = None

            st.success("✅ Repo processed successfully! Switch to Chatbot or Decode tab.")

    if st.session_state.readme_summary:
        with st.expander("📖 README Summary", expanded=True):
            st.markdown(st.session_state.readme_summary)
    elif st.session_state.repo_path:
        st.info("ℹ️ This repo doesn't contain a valid README.md")

    if st.session_state.readme_raw:
        with st.expander("📝 Full README.md"):
            st.code(st.session_state.readme_raw, language="markdown")


elif page == "🤖 Chatbot":
    if st.session_state.vectorstore:
        user_query = st.chat_input("Ask something about this repo...")

        if user_query:
            
            st.session_state.chat_history.append(("user", user_query))
            

          
            with st.spinner("🤖 Thinking with Gemini..."):
                response = ask_question(user_query, st.session_state.vectorstore,readme_text=st.session_state.readme_raw)

            st.session_state.chat_history.append(("ai", response))


       
        for role, msg in st.session_state.chat_history:
            with st.chat_message(role):
                st.markdown(msg)

    else:
        st.warning("⚠️ Please load a repository first from the Home page.")