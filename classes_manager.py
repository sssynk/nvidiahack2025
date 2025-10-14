"""
Class and Session Manager for storing classes containing multiple lecture sessions.
"""
import json
import os
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Tuple


def _now_iso() -> str:
    return datetime.now().isoformat()


class ClassesManager:
    """Manages classes and their lecture sessions on disk.

    Storage layout (root defaults to 'transcripts'):
      - classes.json: index of classes {class_id: {...}}
      - classes/{class_id}/sessions/{session_id}.json: session payloads
    """

    def __init__(self, storage_root: str = "transcripts"):
        self.storage_root = storage_root
        self.classes_index_path = os.path.join(self.storage_root, "classes.json")
        self._ensure_dirs()
        self.classes: Dict[str, Dict] = {}
        self._load_index()

    def _ensure_dirs(self):
        if not os.path.exists(self.storage_root):
            os.makedirs(self.storage_root)
        classes_dir = os.path.join(self.storage_root, "classes")
        if not os.path.exists(classes_dir):
            os.makedirs(classes_dir)

    def _load_index(self):
        if os.path.exists(self.classes_index_path):
            with open(self.classes_index_path, "r") as f:
                data = json.load(f)
                # Normalize to dict keyed by class_id
                if isinstance(data, dict):
                    self.classes = data
                else:
                    # Older formats unsupported; start fresh
                    self.classes = {}
        else:
            self.classes = {}

    def _save_index(self):
        with open(self.classes_index_path, "w") as f:
            json.dump(self.classes, f, indent=2)

    def _class_dir(self, class_id: str) -> str:
        return os.path.join(self.storage_root, "classes", class_id)

    def _sessions_dir(self, class_id: str) -> str:
        return os.path.join(self._class_dir(class_id), "sessions")

    def _ensure_class_dirs(self, class_id: str):
        cdir = self._class_dir(class_id)
        sdir = self._sessions_dir(class_id)
        os.makedirs(cdir, exist_ok=True)
        os.makedirs(sdir, exist_ok=True)

    # -------------------- Class operations --------------------
    def create_class(self, name: str, code: Optional[str] = None, color: Optional[str] = None) -> Dict:
        class_id = self._generate_class_id(name)
        created = _now_iso()
        obj = {
            "class_id": class_id,
            "name": name,
            "code": code or class_id,
            "color": color or "bg-emerald-500",
            "created_at": created,
            "updated_at": created,
            "sessions_count": 0,
            "last_session_at": None,
        }
        self.classes[class_id] = obj
        self._ensure_class_dirs(class_id)
        self._save_index()
        return obj

    def list_classes(self) -> List[Dict]:
        # return shallow copy list
        return list(self.classes.values())

    def get_class(self, class_id: str) -> Optional[Dict]:
        obj = self.classes.get(class_id)
        if not obj:
            return None
        # include sessions listing and details
        sessions = self.list_sessions(class_id)
        out = dict(obj)
        out["sessions"] = sessions
        return out

    def delete_class(self, class_id: str) -> bool:
        if class_id not in self.classes:
            return False
        # delete files
        sdir = self._sessions_dir(class_id)
        if os.path.isdir(sdir):
            for fn in os.listdir(sdir):
                fpath = os.path.join(sdir, fn)
                try:
                    os.remove(fpath)
                except Exception:
                    pass
        # remove directories
        try:
            os.rmdir(sdir)
        except Exception:
            pass
        try:
            os.rmdir(self._class_dir(class_id))
        except Exception:
            pass
        del self.classes[class_id]
        self._save_index()
        return True

    def _generate_class_id(self, base: str) -> str:
        slug = "".join(ch if ch.isalnum() else "-" for ch in base).strip("-").lower() or "class"
        return f"{slug}-{uuid.uuid4().hex[:6]}"

    # -------------------- Session operations --------------------
    def add_session(self, class_id: str, title: str, content: str, metadata: Optional[Dict] = None) -> Dict:
        if class_id not in self.classes:
            raise ValueError("Class not found")
        self._ensure_class_dirs(class_id)
        session_id = f"{uuid.uuid4().hex[:10]}"
        payload = {
            "class_id": class_id,
            "session_id": session_id,
            "title": title or f"Session {session_id}",
            "content": content,
            "summary": None,
            "created_at": _now_iso(),
            "metadata": metadata or {},
        }
        # write file
        fpath = os.path.join(self._sessions_dir(class_id), f"{session_id}.json")
        with open(fpath, "w") as f:
            json.dump(payload, f, indent=2)

        # update class counters
        c = self.classes[class_id]
        c["sessions_count"] = int(c.get("sessions_count", 0)) + 1
        c["updated_at"] = payload["created_at"]
        c["last_session_at"] = payload["created_at"]
        self._save_index()
        return payload

    def list_sessions(self, class_id: str) -> List[Dict]:
        sdir = self._sessions_dir(class_id)
        if not os.path.isdir(sdir):
            return []
        out: List[Dict] = []
        for fn in sorted(os.listdir(sdir)):
            if not fn.endswith('.json'):
                continue
            fpath = os.path.join(sdir, fn)
            try:
                with open(fpath, "r") as f:
                    obj = json.load(f)
                    out.append(obj)
            except Exception:
                continue
        # newest first
        out.sort(key=lambda o: o.get("created_at") or "", reverse=True)
        return out

    def get_session(self, class_id: str, session_id: str) -> Optional[Dict]:
        fpath = os.path.join(self._sessions_dir(class_id), f"{session_id}.json")
        if not os.path.exists(fpath):
            return None
        with open(fpath, "r") as f:
            return json.load(f)

    def update_session_summary(self, class_id: str, session_id: str, summary: str):
        sess = self.get_session(class_id, session_id)
        if not sess:
            return
        sess["summary"] = summary
        fpath = os.path.join(self._sessions_dir(class_id), f"{session_id}.json")
        with open(fpath, "w") as f:
            json.dump(sess, f, indent=2)

    # -------------------- Aggregation helpers --------------------
    def get_class_corpus(self, class_id: str) -> Tuple[str, List[Dict]]:
        """Concatenate all session contents for a class and return corpus and sessions list."""
        sessions = self.list_sessions(class_id)
        texts = []
        for s in sessions:
            title = s.get("title") or s.get("session_id")
            texts.append(f"=== {title} ({s.get('created_at', '')}) ===\n{s.get('summary') or ''}\n{s.get('content') or ''}")
        return ("\n\n".join(texts), sessions)


