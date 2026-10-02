import json
from pathlib import Path


def main():
    data = json.loads(Path("data/metrics.json").read_text(encoding="utf-8"))
    print(f"total: {data['total']}")


if __name__ == "__main__":
    main()
