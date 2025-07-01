import os
import shutil
from git import Repo

def force_remove_readonly(func, path, _):
    os.chmod(path, 0o777)
    func(path)

def clone_repo(repo_url, base_dir="cloned_repos", faiss_dir="faiss_index"):
    
    repo_name = repo_url.rstrip("/").split("/")[-1]
    save_dir = os.path.join(base_dir, repo_name)

    
    if os.path.exists(save_dir):
        print(f"🧹 Removing previous cloned repo at: {save_dir}")
        shutil.rmtree(save_dir, onerror=force_remove_readonly)

    
    if os.path.exists(faiss_dir):
        print(f"🧹 Removing old FAISS index at: {faiss_dir}")
        shutil.rmtree(faiss_dir, onerror=force_remove_readonly)

    
    try:
        Repo.clone_from(repo_url, save_dir)
        print(f"✅ Cloned to {save_dir}")
        return save_dir  
    except Exception as e:
        print(f"❌ Failed to clone: {e}")
        return None
