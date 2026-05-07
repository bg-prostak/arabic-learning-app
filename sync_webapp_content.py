import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parent
CONTENT_PATH = ROOT / "content" / "chapters.json"
WEBAPP_ROOT = ROOT / "webapp"


def copy_asset(source, destination):
    source_path = ROOT / source
    destination_path = WEBAPP_ROOT / destination

    if not source_path.exists():
        print(f"skip missing: {source}")
        return

    destination_path.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source_path, destination_path)
    print(f"copied: {source} -> webapp/{destination}")


def main():
    with CONTENT_PATH.open("r", encoding="utf-8") as file:
        content = json.load(file)

    for chapter in content["chapters"]:
        copy_asset(chapter["words"], chapter["webWords"])

        for dialog in chapter.get("dialogs", []):
            copy_asset(dialog["path"], dialog["webPath"])

    for rule in content.get("rules", []):
        copy_asset(rule["path"], rule["webPath"])

    web_content_path = WEBAPP_ROOT / "content" / "chapters.json"
    web_content_path.parent.mkdir(parents=True, exist_ok=True)

    with web_content_path.open("w", encoding="utf-8") as file:
        json.dump(content, file, ensure_ascii=False, indent=2)
        file.write("\n")

    print("updated: webapp/content/chapters.json")


if __name__ == "__main__":
    main()
