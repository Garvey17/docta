"""Bootstrap Qdrant Cloud vector index with composite dishes using LangChain & OpenAI."""

import argparse
import json
import sys
from pathlib import Path

# Add project root to sys.path so data_pipeline modules can be imported
sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))

from data_pipeline.src.config import Settings, get_settings
from data_pipeline.src.vector_indexer import index_composite_dishes


def main() -> int:
    parser = argparse.ArgumentParser(description="Bootstrap Qdrant Cloud vector index with composite dishes.")
    parser.add_argument("--data", default="data/composite_dishes_db.json", help="Path to composite dishes JSON")
    parser.add_argument("--url", default=None, help="Qdrant Cloud URL (overrides .env)")
    parser.add_argument("--api-key", default=None, help="Qdrant Cloud API Key (overrides .env)")
    parser.add_argument("--collection", default=None, help="Qdrant Collection Name (overrides .env)")
    parser.add_argument("--memory", action="store_true", help="Force in-memory Qdrant client")
    parser.add_argument("--host", default=None, help="Qdrant server host")
    parser.add_argument("--port", type=int, default=6333, help="Qdrant server port")
    args = parser.parse_args()

    settings = get_settings()
    if args.memory:
        settings.qdrant_url = None
    elif args.url:
        settings.qdrant_url = args.url
    if args.api_key:
        settings.qdrant_api_key = args.api_key
    if args.collection:
        settings.qdrant_collection_name = args.collection

    data_path = Path(args.data)
    if not data_path.is_absolute():
        data_path = Path(__file__).resolve().parent.parent / args.data

    if not data_path.exists():
        print(f"[FATAL] Data file does not exist: {data_path}", file=sys.stderr)
        return 1

    with open(data_path, "r", encoding="utf-8") as f:
        dishes_db = json.load(f)

    print(f"Loaded {len(dishes_db)} composite dishes from '{data_path}'.")
    print(f"Target Qdrant: {settings.qdrant_url or 'in-memory'} (Collection: {settings.qdrant_collection_name})")

    try:
        count = index_composite_dishes(dishes_db, settings=settings)
        print(f"[SUCCESS] Successfully indexed {count} dishes into Qdrant Cloud via LangChain.")
        return 0
    except Exception as e:
        print(f"[FATAL] Indexing failed: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
