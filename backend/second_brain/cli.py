import argparse
from .config import Settings
from .index import MemoryIndex
from .ingest import index_notes


def main() -> None:
    parser = argparse.ArgumentParser(description="Index markdown notes for the second brain")
    parser.add_argument("path", nargs="?", help="notes directory (defaults to NOTES_PATH)")
    args = parser.parse_args()
    settings = Settings()
    count = index_notes(__import__("pathlib").Path(args.path) if args.path else settings.notes_path, MemoryIndex())
    print(f"indexed {count} chunks")


if __name__ == "__main__":
    main()
