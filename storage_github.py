# storage_github.py
import base64, os, requests, time
from typing import List, Optional

API = "https://api.github.com"

def _cfg(key: str, default: Optional[str] = None) -> str:
    try:
        import streamlit as st
        return st.secrets["github"][key]
    except Exception:
        return os.environ.get(f"GITHUB_{key.upper()}", default or "")

TOKEN      = _cfg("token")
OWNER      = _cfg("owner")
REPO       = _cfg("repo")
BRANCH     = _cfg("branch", "main")
BASE_PATH  = _cfg("base_path", "KalorikDaten").strip("/")
COMMITTER_NAME  = _cfg("committer_name", "App Bot")
COMMITTER_EMAIL = _cfg("committer_email", "bot@example.org")

def _headers(accept_raw: bool = False):
    h = {
        "Authorization": f"Bearer {TOKEN}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if accept_raw:
        # für Downloads > 1MB: raw liefert Bytes
        h["Accept"] = "application/vnd.github.raw"
    return h

def _full_path(rel_path: str) -> str:
    rel_path = rel_path.strip("/")
    return f"{BASE_PATH}/{rel_path}" if BASE_PATH else rel_path

def gh_get_sha(path: str) -> Optional[str]:
    url = f"{API}/repos/{OWNER}/{REPO}/contents/{path}"
    r = requests.get(url, headers=_headers(), params={"ref": BRANCH}, timeout=30)
    if r.status_code == 404:
        return None
    r.raise_for_status()
    return r.json().get("sha")

def _put_contents(path: str, data_b64: str, message: str, sha: Optional[str]):
    url = f"{API}/repos/{OWNER}/{REPO}/contents/{path}"
    payload = {
        "message": message,
        "content": data_b64,
        "branch": BRANCH,
        "committer": {"name": COMMITTER_NAME, "email": COMMITTER_EMAIL},
    }
    if sha:
        payload["sha"] = sha
    r = requests.put(url, headers=_headers(), json=payload, timeout=60)
    return r

def gh_upload_bytes(rel_path: str, data: bytes, message: str) -> dict:
    """
    Legt Datei neu an oder aktualisiert sie. Base64-kodiert; Retry bei 409 (sha-Race).
    """
    path = _full_path(rel_path)
    data_b64 = base64.b64encode(data).decode("ascii")
    sha = gh_get_sha(path)

    r = _put_contents(path, data_b64, message, sha)
    if r.status_code == 409:
        # Race: sha veraltet – kurz warten, neu holen, retry
        time.sleep(0.3)
        sha = gh_get_sha(path)
        r = _put_contents(path, data_b64, message, sha)

    r.raise_for_status()
    return r.json()

def gh_download_bytes(rel_path: str) -> bytes:
    path = _full_path(rel_path)
    url = f"{API}/repos/{OWNER}/{REPO}/contents/{path}"
    r = requests.get(url, headers=_headers(accept_raw=True), params={"ref": BRANCH}, timeout=60)
    if r.status_code == 404:
        raise FileNotFoundError(path)
    r.raise_for_status()
    return r.content

def gh_list_csv(prefix: str = "") -> List[str]:
    url = f"{API}/repos/{OWNER}/{REPO}/contents/{BASE_PATH}"
    r = requests.get(url, headers=_headers(), params={"ref": BRANCH}, timeout=30)
    if r.status_code == 404:
        return []
    r.raise_for_status()
    items = r.json()
    if isinstance(items, dict):
        return []
    names = [it["name"] for it in items if it.get("type") == "file" and it["name"].lower().endswith(".csv")]
    if prefix:
        names = [n for n in names if n.startswith(prefix)]
    return sorted(names)
