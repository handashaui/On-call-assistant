from pathlib import Path

import requests


BASE_URL = "http://127.0.0.1:8000"
DATA_DIR = Path(__file__).resolve().parents[1] / "data"


def main() -> None:
    for path in sorted(DATA_DIR.glob("*.html")):
        response = requests.post(
            f"{BASE_URL}/v1/documents",
            json={"id": path.stem, "html": path.read_text(encoding="utf-8")},
            timeout=10,
        )
        response.raise_for_status()
        print(response.json())


if __name__ == "__main__":
    main()
