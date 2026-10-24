"""
Pengambilan seluruh komentar dari semua video di videos_manifest.csv
menggunakan YouTube Data API v3.

Hanya baris dengan include = "yes" dan video_id terisi yang diambil.
Semua video diambil dalam satu run, sehingga satu tanggal pembekuan data
berlaku untuk seluruh korpus.

authorChannelId tidak pernah disimpan mentah: diganti dengan HMAC-SHA256
(salt dari AUTHOR_HASH_SALT di key.env), nama/foto/URL akun dihapus
dari arsip JSON, dan @handle di teks komentar diganti "@user".

Output (di folder data/<tanggal>/):
  raw/raw_<videoId>.json  arsip respons API (sudah dianonimkan)
  comments.csv            semua komentar + kolom kasus dari manifest
  videos.csv              metadata dan statistik video saat pengambilan
  collection_log.json     waktu run, parameter, jumlah per video, error

Penggunaan:
  python src/fetch_comments.py                 # ambil semua video include=yes
  python src/fetch_comments.py --dry-run       # cek manifest tanpa request API
  python src/fetch_comments.py --only ID1 ID2  # ambil video tertentu saja
"""

from datetime import datetime, timezone
from pathlib import Path
import argparse
import csv
import hashlib
import hmac
import json
import os
import re
import sys
import time

import requests
from dotenv import load_dotenv

# ---------------------------------------------------------------------------
# Konfigurasi
# ---------------------------------------------------------------------------

load_dotenv("key.env")

MANIFEST_CSV = "config/videos_manifest.csv"
YOUTUBE_API_BASE_URL = "https://www.googleapis.com/youtube/v3"
REQUEST_TIMEOUT_SECONDS = 30
MAX_RESULTS = 100
MAX_ATTEMPTS = 4
RETRY_STATUS_CODES = {500, 502, 503, 504}

# @handle di dalam teks komentar (terutama balasan) diganti agar akun tidak teridentifikasi
MENTION_PATTERN = re.compile(r"@[\w.\-]+")
MENTION_REPLACEMENT = "@user"

MANIFEST_COLUMNS = [
    "video_id", "label", "case_id", "case_name", "organization", "org_type",
    "video_type", "uploader", "verification_status", "verification_source",
    "include", "screening_note",
]
ALLOWED_VALUES = {
    "org_type": {"government", "commercial"},
    "video_type": {"official", "reupload_archive", "third_party"},
    "verification_status": {
        "official_statement", "credible_media", "platform_label",
        "visual_indication", "to_verify",
    },
    "include": {"yes", "no", "pending"},
}

# Kolom manifest yang ikut disalin ke setiap baris komentar
CASE_COLUMNS = ["case_id", "organization", "org_type", "video_type", "verification_status"]

COMMENT_COLUMNS = [
    "commentId", "videoId", *CASE_COLUMNS, "parentId", "isReply",
    "textOriginal", "authorHash", "isVideoOwner", "likeCount",
    "publishedAt", "updatedAt", "totalReplyCount", "retrievedAt",
]
VIDEO_COLUMNS = [
    "video_id", "title", "channel_id", "channel_title", "published_at",
    "view_count", "like_count", "comment_count", *CASE_COLUMNS,
    "verification_source", "retrieved_at",
]

# Field identitas akun yang dihapus dari arsip JSON
AUTHOR_FIELDS_TO_DROP = ["authorDisplayName", "authorProfileImageUrl", "authorChannelUrl"]

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def require_environment_variable(*variable_names: str) -> str:
    for name in variable_names:
        value = os.getenv(name)
        if value and value.strip():
            return value.strip()
    print(f"ERROR: Environment variable {' / '.join(variable_names)} tidak ditemukan di key.env.")
    sys.exit(1)


def utc_timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def hash_author(channel_id: str) -> str:
    if not channel_id:
        return ""
    digest = hmac.new(HASH_SALT.encode(), channel_id.encode(), hashlib.sha256)
    return digest.hexdigest()[:16]


def youtube_get(resource: str, parameters: dict) -> dict:
    """GET ke YouTube API; error jaringan dan HTTP 5xx dicoba ulang dengan jeda bertambah."""
    for attempt in range(1, MAX_ATTEMPTS + 1):
        try:
            response = requests.get(
                f"{YOUTUBE_API_BASE_URL}/{resource}",
                params={**parameters, "key": API_KEY},
                timeout=REQUEST_TIMEOUT_SECONDS,
            )
        except (requests.ConnectionError, requests.Timeout):
            if attempt == MAX_ATTEMPTS:
                raise
        else:
            if response.status_code not in RETRY_STATUS_CODES or attempt == MAX_ATTEMPTS:
                response.raise_for_status()
                return response.json()
        wait_seconds = 2 ** attempt
        print(f"    percobaan {attempt} gagal, coba lagi dalam {wait_seconds} detik...")
        time.sleep(wait_seconds)


def extract_youtube_error(error: requests.HTTPError) -> str:
    try:
        error_payload = error.response.json()
        errors = error_payload.get("error", {}).get("errors", [])
        if errors:
            first = errors[0]
            return f"{first.get('reason', 'unknown')}: {first.get('message', '')}"
        return error_payload.get("error", {}).get("message", str(error))
    except Exception:
        return str(error)


# ---------------------------------------------------------------------------
# Manifest
# ---------------------------------------------------------------------------


def load_manifest(path: str) -> list[dict]:
    """Membaca dan memvalidasi manifest; berhenti jika ada nilai yang tidak valid."""
    with open(path, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        missing = set(MANIFEST_COLUMNS) - set(reader.fieldnames or [])
        if missing:
            print(f"ERROR: Kolom manifest hilang: {sorted(missing)}")
            sys.exit(1)
        rows = [{k: (v or "").strip() for k, v in row.items()} for row in reader]

    problems = []
    seen_ids = set()
    for line_number, row in enumerate(rows, start=2):
        for column, allowed in ALLOWED_VALUES.items():
            if row[column] and row[column] not in allowed:
                problems.append(f"baris {line_number}: {column}='{row[column]}' tidak valid")
        if row["include"] == "yes":
            if not row["video_id"]:
                problems.append(f"baris {line_number}: include=yes tetapi video_id kosong")
            for column in CASE_COLUMNS:
                if not row[column]:
                    problems.append(f"baris {line_number}: include=yes tetapi {column} kosong")
        if row["video_id"]:
            if row["video_id"] in seen_ids:
                problems.append(f"baris {line_number}: video_id {row['video_id']} duplikat")
            seen_ids.add(row["video_id"])

    if problems:
        print("ERROR: Manifest tidak valid:")
        for p in problems:
            print(f"  - {p}")
        sys.exit(1)

    return rows


# ---------------------------------------------------------------------------
# Pengambilan data
# ---------------------------------------------------------------------------


def fetch_video_metadata(video_ids: list[str]) -> dict[str, dict]:
    """Mengambil snippet + statistics untuk semua video (maks. 50 ID per request)."""
    items = {}
    for start in range(0, len(video_ids), 50):
        batch = video_ids[start:start + 50]
        response = youtube_get("videos", {"part": "snippet,statistics", "id": ",".join(batch)})
        for item in response.get("items", []):
            items[item["id"]] = item
    return items


def fetch_all_pages(resource: str, params: dict) -> list[dict]:
    """Mengambil seluruh halaman sebuah list endpoint dengan mengikuti nextPageToken."""
    pages = []
    next_page_token = None
    while True:
        page_params = {**params, "maxResults": MAX_RESULTS, "textFormat": "plainText"}
        if next_page_token:
            page_params["pageToken"] = next_page_token
        page = youtube_get(resource, page_params)
        pages.append(page)
        next_page_token = page.get("nextPageToken")
        if not next_page_token:
            return pages


def fetch_video_comments(video_id: str) -> tuple[list[dict], dict[str, list[dict]]]:
    """Mengambil semua comment thread, lalu balasan lengkap untuk thread yang terpotong."""
    thread_pages = fetch_all_pages("commentThreads", {"part": "snippet,replies", "videoId": video_id})
    n_threads = sum(len(p.get("items", [])) for p in thread_pages)
    print(f"    {n_threads} thread dalam {len(thread_pages)} halaman")

    # commentThreads hanya menyertakan sebagian balasan; sisanya lewat comments.list
    reply_pages_map = {}
    for page in thread_pages:
        for item in page.get("items", []):
            total_reply_count = item["snippet"].get("totalReplyCount", 0)
            returned = len(item.get("replies", {}).get("comments", []))
            if total_reply_count > returned:
                parent_id = item["snippet"]["topLevelComment"]["id"]
                reply_pages_map[parent_id] = fetch_all_pages(
                    "comments", {"part": "snippet", "parentId": parent_id}
                )
    if reply_pages_map:
        print(f"    {len(reply_pages_map)} thread membutuhkan pengambilan balasan tambahan")

    return thread_pages, reply_pages_map


# ---------------------------------------------------------------------------
# Anonimisasi dan transformasi
# ---------------------------------------------------------------------------


def anonymize_snippet(snippet: dict) -> None:
    """Mengganti authorChannelId dengan hash, menghapus identitas akun, dan menyamarkan @handle (in place)."""
    for field in AUTHOR_FIELDS_TO_DROP:
        snippet.pop(field, None)
    for field in ("textOriginal", "textDisplay"):
        if field in snippet:
            snippet[field] = MENTION_PATTERN.sub(MENTION_REPLACEMENT, snippet[field])
    channel = snippet.pop("authorChannelId", None)
    if channel is not None:
        snippet["authorHash"] = hash_author(channel.get("value", ""))


def anonymize_pages(thread_pages: list[dict], reply_pages_map: dict) -> None:
    for page in thread_pages:
        for item in page.get("items", []):
            anonymize_snippet(item["snippet"]["topLevelComment"]["snippet"])
            for reply in item.get("replies", {}).get("comments", []):
                anonymize_snippet(reply["snippet"])
    for pages in reply_pages_map.values():
        for page in pages:
            for reply in page.get("items", []):
                anonymize_snippet(reply["snippet"])


def extract_rows(thread_pages: list[dict], reply_pages_map: dict, case_info: dict,
                 video_id: str, owner_hash: str, retrieved_at: str) -> list[dict]:
    """Mengubah respons API (yang sudah dianonimkan) menjadi baris CSV."""
    rows = []

    def make_row(comment: dict, parent_id: str, is_reply: bool, total_reply_count: int) -> dict:
        snippet = comment.get("snippet", {})
        author_hash = snippet.get("authorHash", "")
        return {
            "commentId": comment.get("id", ""),
            "videoId": video_id,
            **case_info,
            "parentId": parent_id,
            "isReply": is_reply,
            "textOriginal": snippet.get("textOriginal", ""),
            "authorHash": author_hash,
            "isVideoOwner": bool(author_hash) and author_hash == owner_hash,
            "likeCount": snippet.get("likeCount", 0),
            "publishedAt": snippet.get("publishedAt", ""),
            "updatedAt": snippet.get("updatedAt", ""),
            "totalReplyCount": total_reply_count,
            "retrievedAt": retrieved_at,
        }

    # Thread yang di-pin bisa muncul dua kali (halaman pertama dan posisi aslinya)
    seen_thread_ids = set()

    for page in thread_pages:
        for item in page.get("items", []):
            top_level = item["snippet"]["topLevelComment"]
            parent_id = top_level.get("id", "")
            if parent_id in seen_thread_ids:
                continue
            seen_thread_ids.add(parent_id)
            rows.append(make_row(top_level, "", False, item["snippet"].get("totalReplyCount", 0)))

            if parent_id in reply_pages_map:
                replies = [r for p in reply_pages_map[parent_id] for r in p.get("items", [])]
            else:
                replies = item.get("replies", {}).get("comments", [])
            for reply in replies:
                rows.append(make_row(reply, parent_id, True, 0))

    return rows


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Ambil komentar YouTube untuk semua video di manifest.")
    parser.add_argument("--manifest", default=MANIFEST_CSV)
    parser.add_argument("--out-dir", default=None, help="Default: data/<YYYYMMDD>")
    parser.add_argument("--only", nargs="+", metavar="VIDEO_ID", help="Ambil video tertentu saja")
    parser.add_argument("--dry-run", action="store_true", help="Validasi manifest tanpa request API")
    parser.add_argument("--overwrite", action="store_true", help="Timpa hasil run di out-dir yang sama")
    return parser.parse_args()


def main():
    args = parse_args()
    manifest = load_manifest(args.manifest)

    selected = [r for r in manifest if r["include"] == "yes"]
    if args.only:
        unknown = set(args.only) - {r["video_id"] for r in selected}
        if unknown:
            print(f"ERROR: Tidak ada di manifest dengan include=yes: {sorted(unknown)}")
            sys.exit(1)
        selected = [r for r in selected if r["video_id"] in args.only]
    pending = [r for r in manifest if r["include"] == "pending"]

    print("=== Pengambilan komentar YouTube ===")
    print(f"Manifest : {args.manifest}")
    print(f"Video    : {len(selected)} dipilih, {len(pending)} masih pending")
    for r in selected:
        print(f"  {r['video_id']}  {r['case_id']}  {r['org_type']:<10}  {r['video_type']:<16}  {r['label'][:50]}")
    for r in pending:
        print(f"  (pending) {r['case_id']}  {r['label'][:50]}")
    if args.dry_run:
        print("\nDry run: manifest valid, tidak ada request API yang dikirim.")
        return
    if not selected:
        print("Tidak ada video untuk diambil.")
        return

    started_at = utc_timestamp()
    out_dir = Path(args.out_dir or Path("data") / started_at[:10].replace("-", ""))
    if (out_dir / "comments.csv").exists() and not args.overwrite:
        print(f"ERROR: {out_dir} sudah berisi hasil run sebelumnya. "
              f"Gunakan --out-dir lain atau --overwrite.")
        sys.exit(1)
    raw_dir = out_dir / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)

    print(f"\n[1/2] Mengambil metadata video...")
    video_ids = [r["video_id"] for r in selected]
    try:
        metadata = fetch_video_metadata(video_ids)
    except requests.RequestException as e:
        print(f"ERROR: Gagal mengambil metadata video: {extract_youtube_error(e)}")
        sys.exit(1)

    print(f"\n[2/2] Mengambil komentar...")
    all_rows = []
    video_rows = []
    log_videos = []

    for r in selected:
        video_id = r["video_id"]
        case_info = {c: r[c] for c in CASE_COLUMNS}
        entry = {"video_id": video_id, "case_id": r["case_id"], "status": "ok"}
        print(f"  {video_id} ({r['case_id']})")

        item = metadata.get(video_id)
        if item is None:
            entry.update(status="error", error="video tidak ditemukan / private / dihapus")
            print(f"    ERROR: {entry['error']}")
            log_videos.append(entry)
            continue

        snippet, stats = item["snippet"], item.get("statistics", {})
        retrieved_at = utc_timestamp()
        video_rows.append({
            "video_id": video_id,
            "title": snippet.get("title", ""),
            "channel_id": snippet.get("channelId", ""),
            "channel_title": snippet.get("channelTitle", ""),
            "published_at": snippet.get("publishedAt", ""),
            "view_count": stats.get("viewCount", ""),
            "like_count": stats.get("likeCount", ""),
            "comment_count": stats.get("commentCount", ""),
            **case_info,
            "verification_source": r["verification_source"],
            "retrieved_at": retrieved_at,
        })

        try:
            thread_pages, reply_pages_map = fetch_video_comments(video_id)
        except requests.RequestException as e:
            reason = extract_youtube_error(e)
            entry.update(status="error", error=reason)
            print(f"    ERROR: {reason}")
            log_videos.append(entry)
            if "quotaExceeded" in reason:
                print("Quota habis; run dihentikan.")
                break
            continue

        anonymize_pages(thread_pages, reply_pages_map)
        with open(raw_dir / f"raw_{video_id}.json", "w", encoding="utf-8") as f:
            json.dump({
                "videoId": video_id,
                "retrievedAt": retrieved_at,
                "commentThreadPages": thread_pages,
                "additionalReplyPages": reply_pages_map,
            }, f, ensure_ascii=False, indent=2)

        rows = extract_rows(thread_pages, reply_pages_map, case_info, video_id,
                            hash_author(snippet.get("channelId", "")), retrieved_at)
        all_rows.extend(rows)

        n_top = sum(1 for x in rows if not x["isReply"])
        entry.update(
            reported_comment_count=int(stats["commentCount"]) if "commentCount" in stats else None,
            fetched_top_level=n_top,
            fetched_replies=len(rows) - n_top,
            fetched_total=len(rows),
        )
        print(f"    {n_top} komentar + {len(rows) - n_top} balasan = {len(rows)} "
              f"(statistik video: {stats.get('commentCount', '?')})")
        log_videos.append(entry)

    with open(out_dir / "comments.csv", "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=COMMENT_COLUMNS)
        writer.writeheader()
        writer.writerows(all_rows)

    with open(out_dir / "videos.csv", "w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=VIDEO_COLUMNS)
        writer.writeheader()
        writer.writerows(video_rows)

    finished_at = utc_timestamp()
    with open(out_dir / "collection_log.json", "w", encoding="utf-8") as f:
        json.dump({
            "started_at_utc": started_at,
            "finished_at_utc": finished_at,
            "manifest": args.manifest,
            "only": args.only,
            "api_parameters": {"maxResults": MAX_RESULTS, "textFormat": "plainText",
                               "commentThreads.part": "snippet,replies"},
            "anonymization": "authorChannelId -> HMAC-SHA256 (AUTHOR_HASH_SALT), first 16 hex; "
                             + ", ".join(AUTHOR_FIELDS_TO_DROP) + " removed; "
                             + f"@handles in text replaced with {MENTION_REPLACEMENT}",
            "pending_videos": [{"case_id": r["case_id"], "label": r["label"]} for r in pending],
            "videos": log_videos,
            "total_rows": len(all_rows),
        }, f, ensure_ascii=False, indent=2)

    n_errors = sum(1 for v in log_videos if v["status"] != "ok")
    print(f"\n=== Ringkasan ===")
    print(f"Video berhasil : {len(log_videos) - n_errors} / {len(selected)}")
    print(f"Total baris    : {len(all_rows)}")
    print(f"Output         : {out_dir}")
    if n_errors:
        print(f"PERINGATAN: {n_errors} video gagal, lihat collection_log.json")


API_KEY = require_environment_variable("YOUTUBE_API_KEY", "YT_API_KEY")
HASH_SALT = require_environment_variable("AUTHOR_HASH_SALT")

if __name__ == "__main__":
    main()
