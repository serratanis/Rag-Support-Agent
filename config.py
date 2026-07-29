"""
Genel/şirketten bağımsız yapılandırma yükleyici.

Gerçek dağıtımda `config.json` dosyası oluşturup kendi şirket bilgilerinizi
(marka adı, domain, destek linki, telefon vb.) girin. `config.json` git
tarafından yok sayılır (bkz. .gitignore) - böylece herkese açık repoda
gerçek/özel bilgi bulunmaz.

`config.example.json` demo/placeholder değerlerle birlikte gelir; hiçbir
şey yapmasanız bile proje bu değerlerle çalışır.
"""

import json
import os

_HERE = os.path.dirname(os.path.abspath(__file__))
_CONFIG_PATH = os.environ.get("CHATBOT_CONFIG_PATH", os.path.join(_HERE, "config.json"))
_EXAMPLE_PATH = os.path.join(_HERE, "config.example.json")


def _load() -> dict:
    path = _CONFIG_PATH if os.path.exists(_CONFIG_PATH) else _EXAMPLE_PATH
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


_cfg = _load()

COMPANY_NAME: str = _cfg["company_name"]
BASE_URL: str = _cfg["base_url"].rstrip("/")
SUPPORT_PATH: str = _cfg["support_path"]
SUPPORT_PHONE: str = _cfg["support_phone"]
LLM_MODEL: str = _cfg["llm_model"]
OLLAMA_HOST: str = _cfg["ollama_host"].rstrip("/")
CONVERSATION_TIMEOUT_MINUTES: int = _cfg.get("conversation_timeout_minutes", 60)

# "iban" -> "/hesaplar" gibi göreli path'leri tam URL'e çeviriyoruz.
LINKS: dict[str, str] = {
    keyword: f"{BASE_URL}{path}" for keyword, path in _cfg["links"].items()
}

SUPPORT_URL: str = f"{BASE_URL}{SUPPORT_PATH}"

EXTRA_KEYWORDS: list[str] = _cfg.get("extra_keywords", [])
