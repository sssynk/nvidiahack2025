"""
Settings Manager for persisting simple app-wide settings (e.g., ASR mode).
"""
import json
import os
from typing import Any, Dict, Optional


class SettingsManager:
    """Backs settings in a JSON file under the storage root.

    Example schema:
    {
      "asr_mode": "free"  # or "fast"
      ,"llm_provider": "nvidia"  # or "groq"
    }
    """

    def __init__(self, storage_root: str = "transcripts"):
        self.storage_root = storage_root
        os.makedirs(self.storage_root, exist_ok=True)
        self.settings_path = os.path.join(self.storage_root, "settings.json")
        self._cache: Dict[str, Any] = {}
        self._load()

    def _load(self) -> None:
        if os.path.exists(self.settings_path):
            try:
                with open(self.settings_path, "r") as f:
                    self._cache = json.load(f)
            except Exception:
                self._cache = {}
        else:
            self._cache = {}

    def _save(self) -> None:
        with open(self.settings_path, "w") as f:
            json.dump(self._cache, f, indent=2)

    def get_settings(self) -> Dict[str, Any]:
        return dict(self._cache)

    def update_settings(self, updates: Dict[str, Any]) -> Dict[str, Any]:
        self._cache.update(updates)
        self._save()
        return dict(self._cache)

    def get(self, key: str, default: Optional[Any] = None) -> Any:
        return self._cache.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self._cache[key] = value
        self._save()


