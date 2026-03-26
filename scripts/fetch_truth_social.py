"""Download and normalize Truth Social archive from CNN."""

import html
import re
import sys
from pathlib import Path
from typing import List

import pandas as pd
import requests

BASE_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = BASE_DIR / "data" / "raw" / "truth_social"
PROCESSED_DIR = BASE_DIR / "data" / "processed"

CNN_JSON_URL = "https://ix.cnn.io/data/truth-social/truth_archive.json"


def download(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    resp = requests.get(url, timeout=120)
    resp.raise_for_status()
    dest.write_bytes(resp.content)
    print(f"downloaded {dest.name} -> {dest.stat().st_size/1024:.1f} KB")


def strip_html(text: str) -> str:
    if not isinstance(text, str):
        return ""
    # Decode HTML entities then remove tags.
    decoded = html.unescape(text)
    cleaned = re.sub(r"<[^>]+>", " ", decoded)
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned


def parse_media(media_field) -> List[str]:
    # media_field is a list of dicts; collect url fields if present.
    urls: List[str] = []
    if isinstance(media_field, list):
        for item in media_field:
            if isinstance(item, dict):
                url = item.get("url") or item.get("src")
                if url:
                    urls.append(str(url))
    return urls


def main() -> int:
    raw_json_path = RAW_DIR / "truth_archive.json"
    download(CNN_JSON_URL, raw_json_path)

    data = pd.read_json(raw_json_path)
    if data.empty:
        print("No records downloaded.")
        return 1

    data.rename(
        columns={
            "id": "post_id",
            "content": "text_raw",
        },
        inplace=True,
    )

    data["created_at"] = pd.to_datetime(data["created_at"], utc=True, errors="coerce")
    data["text"] = data["text_raw"].apply(strip_html)
    data["media_urls"] = data["media"].apply(parse_media)
    data["media_count"] = data["media_urls"].str.len()
    data["has_media"] = data["media_count"] > 0
    data["text_length"] = data["text"].str.len()
    data["source_platform"] = "truthsocial"

    cols = [
        "post_id",
        "created_at",
        "text",
        "replies_count",
        "reblogs_count",
        "favourites_count",
        "media_count",
        "media_urls",
        "has_media",
        "text_length",
        "url",
        "source_platform",
    ]
    data = data[cols]

    RAW_DIR.mkdir(parents=True, exist_ok=True)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    raw_csv_path = RAW_DIR / "truth_archive.csv"
    processed_path = PROCESSED_DIR / "truth_social_posts.parquet"

    data.to_csv(raw_csv_path, index=False)
    data.to_parquet(processed_path, index=False)

    print(f"records: {len(data):,}")
    print("date range:", data["created_at"].min(), "to", data["created_at"].max())
    print("saved raw csv ->", raw_csv_path)
    print("saved parquet ->", processed_path)
    print("media stats: has_media", data["has_media"].sum(), "/", len(data))
    return 0


if __name__ == "__main__":
    sys.exit(main())
