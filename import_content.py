import argparse
import json
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parent
CONTENT_PATH = ROOT / "content" / "chapters.json"
WEBAPP_ROOT = ROOT / "webapp"


def read_json(path):
    with path.open("r", encoding="utf-8") as file:
        return json.load(file)


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=2)
        file.write("\n")


def copy_file(source, destination):
    if not source.exists():
        raise FileNotFoundError(f"File not found: {source}")

    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)


def load_content():
    return read_json(CONTENT_PATH)


def save_content(content):
    write_json(CONTENT_PATH, content)


def find_chapter_index(content, chapter_id):
    for index, chapter in enumerate(content["chapters"]):
        if chapter["id"] == chapter_id:
            return index
    return None


def import_chapter(source_dir):
    source_dir = source_dir.resolve()
    config = read_json(source_dir / "chapter.json")
    chapter_id = config["id"]

    copy_file(source_dir / "words.json", ROOT / "words" / f"{chapter_id}.json")

    dialogs = []
    for index, dialog in enumerate(config.get("dialogs", []), start=1):
        file_name = dialog.get("file") or f"dialog{index}.png"
        source_path = source_dir / file_name
        destination_name = f"dialog{index}{source_path.suffix.lower()}"
        destination_path = ROOT / "dialogues" / chapter_id / destination_name

        copy_file(source_path, destination_path)

        dialogs.append({
            "title": dialog["title"],
            "path": f"dialogues/{chapter_id}/{destination_name}",
            "webPath": f"media/dialogues/{chapter_id}/{destination_name}"
        })

    content = load_content()
    chapter = {
        "id": chapter_id,
        "title": config["title"],
        "subtitle": config.get("subtitle", ""),
        "words": f"words/{chapter_id}.json",
        "webWords": f"data/{chapter_id}.json",
        "dialogs": dialogs
    }

    existing_index = find_chapter_index(content, chapter_id)
    if existing_index is None:
        content["chapters"].append(chapter)
    else:
        content["chapters"][existing_index] = chapter

    save_content(content)
    sync_webapp(content)
    print(f"Imported chapter: {chapter['title']}")


def import_rules(source_dir):
    source_dir = source_dir.resolve()
    config = read_json(source_dir / "rules.json")
    content = load_content()
    existing_by_path = {
        rule["path"]: index
        for index, rule in enumerate(content.get("rules", []))
    }

    for rule in config["rules"]:
        file_name = rule["file"]
        source_path = source_dir / file_name
        destination_path = ROOT / "rules" / file_name

        copy_file(source_path, destination_path)

        rule_record = {
            "title": rule["title"],
            "tag": rule.get("tag", "Правило"),
            "path": f"rules/{file_name}",
            "webPath": f"media/rules/{file_name}"
        }

        existing_index = existing_by_path.get(rule_record["path"])
        if existing_index is None:
            content.setdefault("rules", []).append(rule_record)
        else:
            content["rules"][existing_index] = rule_record

    save_content(content)
    sync_webapp(content)
    print(f"Imported rules: {len(config['rules'])}")


def sync_webapp(content=None):
    content = content or load_content()

    for chapter in content["chapters"]:
        copy_file(ROOT / chapter["words"], WEBAPP_ROOT / chapter["webWords"])

        for dialog in chapter.get("dialogs", []):
            copy_file(ROOT / dialog["path"], WEBAPP_ROOT / dialog["webPath"])

    for rule in content.get("rules", []):
        copy_file(ROOT / rule["path"], WEBAPP_ROOT / rule["webPath"])

    write_json(WEBAPP_ROOT / "content" / "chapters.json", content)
    print("Synced webapp content")


def main():
    parser = argparse.ArgumentParser(description="Import course content into the app.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    chapter_parser = subparsers.add_parser("chapter", help="Import one chapter from a folder.")
    chapter_parser.add_argument("source", help="Folder with chapter.json, words.json and dialog images.")

    rules_parser = subparsers.add_parser("rules", help="Import rules from a folder.")
    rules_parser.add_argument("source", help="Folder with rules.json and rule images.")

    subparsers.add_parser("sync", help="Sync current content to webapp.")

    args = parser.parse_args()

    if args.command == "chapter":
        import_chapter(Path(args.source))

    if args.command == "rules":
        import_rules(Path(args.source))

    if args.command == "sync":
        sync_webapp()


if __name__ == "__main__":
    main()
