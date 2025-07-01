import streamlit as st 
from clone_repo import clone_repo ## add these function
## from process_code import load_and_embed_repo 
# from qa_bot import ask_question
# from file_tree_utils import build_file_tree, describe_code_file

## setting up the page 
st.set_page_config(page_title = "Decodify",layout="wide")
st.title("🚀 Decodify  -  GitHub Repo Decoded ")

# navigation bar slider
st.sidebar.title("🚀Decodify")
page = st.sidebar.radio("Go to", ["🏠 Home", "🤖 Chatbot", "📂 Decode", "📈 Rate My Repo", "ℹ️ About"])

