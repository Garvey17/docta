"""Bootstrap Qdrant vector index with composite dishes."""

import argparse
import json
import sys
from pathlib import Path

# Add project root to sys.path so data_pipeline modules can be imported
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from data_pipeline.src.vector_indexer import (
    get_qdrant_client,
    index_composite_dishes,
    COLLECTION_NAME,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Bootstrap Qdrant vector index with composite dishes.")
    parser.add_argument("--host", default="localhost", help="Qdrant server hostname")
    parser.add_argument("--port", type=int, default=6333, help="Qdrant server port")
    parser.add_argument("--data", default="data/composite_dishes_db.json", help="Path to composite dishes JSON")
    parser.add_argument("--memory", action="store_true", help="Force in-memory Qdrant client")
    args = parser.parse_args()

    data_path = Path(args.data)
    if not data_path.is_absolute():
        data_path = Path(__file__).resolve().parent.parent / args.data

    if not data_path.exists():
        print(f"[FATAL] Data file does not exist: {data_path}", file=sys.stderr)
        return 1

    with open(data_path, "r", encoding="utf-8") as f:
        dishes_db = json.load(f)

    print(f"Loaded {len(dishes_db)} composite dishes from '{data_path}'.")

    client = get_qdrant_client(
        host=args.host if not args.memory else None,
        port=args.port,
        use_memory=args.memory,
    )

    try:
        count = index_composite_dishes(client, dishes_db, collection_name=COLLECTION_NAME)
        print(f"[SUCCESS] Successfully indexed {count} dishes into collection '{COLLECTION_NAME}'.")
        return 0
    except Exception as e:
        print(f"[FATAL] Indexing failed: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
