from pathlib import Path


class Settings:
    APP_NAME = "On-Call Assistant"
    BASE_DIR = Path(__file__).resolve().parents[2]
    DATA_DIR = BASE_DIR / "data"
    TEMPLATES_DIR = BASE_DIR / "app" / "templates"
    STATIC_DIR = BASE_DIR / "app" / "static"


settings = Settings()
