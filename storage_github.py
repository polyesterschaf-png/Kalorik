# storage_github.py
import base64, os, requests, time
from urllib.parse import quote  # <— NEU
from typing import List, Optional

API = "https://api.github.com"
USER_AGENT = "Kalorik-App/1.0 (+https://github.com/polyesterschaf-png/Kalorik)"

def _headers(accept_raw: bool = False):
    h = {
        "Authorization": f"token {TOKEN}",  # <— PAT: 'token' ist korrekt
        "Accept": "application/vnd.github+json",
        "User-Agent": USER_AGENT,
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if accept_raw:
        h["Accept"] = "application/vnd.github.raw"
    return h

def _encode_path(p: str) -> str:


def _cfg(key: str, default: Optional[str] = None) -> str:
    """
    Konfiguration zuerst aus st.secrets['github'][key], sonst aus Umgebungsvariablen GITHUB_KEY,
    sonst default.
    """
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
        "Authorization": f"token {TOKEN}",
        "Accept": "application/vnd.github+json",
        "User-Agent": USER_AGENT,
        "X-GitHub-Api-Version": "2022-11-28",
    }
    if accept_raw:
        # Für Downloads >1MB sollte raw verwendet werden
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
    if not r.ok:
        # Hilfreiche Fehlermeldung mit Status + GitHub-Message
        try:
            msg = r.json().get("message", "")
        except Exception:
            msg = r.text[:300]
        raise RuntimeError(f"GitHub GET {r.status_code} for {path}: {msg}")
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
    Legt Datei neu an oder aktualisiert sie. Base64-kodiert; einmaliger Retry bei 409 (sha-Race).
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
    """
    Lädt Dateiinhalt (Bytes). Nutzt raw media type.
    """
    path = _full_path(rel_path)
    url = f"{API}/repos/{OWNER}/{REPO}/contents/{path}"
    r = requests.get(url, headers=_headers(accept_raw=True), params={"ref": BRANCH}, timeout=60)
    if r.status_code == 404:
        raise FileNotFoundError(path)
    r.raise_for_status()
    return r.content

def gh_list_csv(prefix: str = "") -> List[str]:
    """
    Listet .csv-Dateien im BASE_PATH. Mit kleinem Retry und verständlicher Fehlermeldung.
    """
    url = f"{API}/repos/{OWNER}/{REPO}/contents/{BASE_PATH}"
    last_error = None
    for attempt in range(3):  # Retry für 5xx/Netz-Haker
        r = requests.get(url, headers=_headers(), params={"ref": BRANCH}, timeout=30)
        if r.status_code == 404:
            return []
        if r.ok:
            break
        last_error = r
        time.sleep(0.4 * (attempt + 1))
    else:
        # Nach Retries immer noch Fehler: aussagekräftig machen
        try:
            detail = last_error.json().get("message", "")
        except Exception:
            detail = last_error.text[:300]
        raise RuntimeError(f"GitHub list error {last_error.status_code}: {detail}")

    items = r.json()
    if isinstance(items, dict):  # BASE_PATH ist (unerwartet) eine Datei
        return []
    names = [it["name"] for it in items if it.get("type") == "file" and it["name"].lower().endswith(".csv")]
    if prefix:
        names = [n for n in names if n.startswith(prefix)]
    return sorted(names)

# Optional: einfacher Selbsttest, kann temporär im Lehrkraftmodus angezeigt werden
def gh_self_test() -> dict:
    r = requests.get(f"{API}/repos/{OWNER}/{REPO}/branches/{BRANCH}", headers=_headers(), timeout=15)
    r.raise_for_status()
    return {"ok": True, "branch": BRANCH, "head": r.json().get("commit", {}).get("sha")}
