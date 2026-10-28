
from pathlib import Path

from rag.service import RAGService


KNOWLEDGE_BASE = Path("knowledge_base")
SUPPORTED_EXTENSIONS = {".pdf", ".txt", ".md"}


def main() -> None:
    KNOWLEDGE_BASE.mkdir(parents=True, exist_ok=True)
    rag = RAGService()

    files = [
        path
        for path in KNOWLEDGE_BASE.iterdir()
        if path.is_file()
        and path.name != "README.md"
        and path.suffix.lower() in SUPPORTED_EXTENSIONS
    ]

    if not files:
        print(
            "No documents found. Add PDF, TXT, or MD files "
            "to the knowledge_base folder."
        )
        return

    for path in files:
        try:
            count = rag.add_document(
                filename=path.name,
                content=path.read_bytes(),
            )
            print(f"Indexed {path.name}: {count} chunks")
        except Exception as exc:
            print(f"Failed to index {path.name}: {exc}")

    print(f"Total indexed chunks: {rag.chunk_count()}")


if __name__ == "__main__":
    main()
