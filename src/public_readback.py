from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse
from urllib.request import Request, build_opener, HTTPRedirectHandler

from .common import ContractError


DEFAULT_BASE_URL = "https://sjoerds85.github.io/silver-ciss-public-data/ciss/v1"
EXPECTED_REPOSITORY = "SjoerdS85/silver-ciss-public-data"
MAX_DATASET_BYTES = 10 * 1024 * 1024
MAX_JSON_BYTES = 256 * 1024


class PublicRedirects(HTTPRedirectHandler):
    allowed_exact = {"github.com", "api.github.com", "sjoerds85.github.io"}
    allowed_suffixes = (".githubusercontent.com",)

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        parsed = urlparse(newurl)
        host = (parsed.hostname or "").lower()
        if parsed.scheme != "https":
            raise ContractError(f"non-HTTPS redirect: {newurl}")
        if host not in self.allowed_exact and not any(host.endswith(s) for s in self.allowed_suffixes):
            raise ContractError(f"unexpected redirect host: {host}")
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _allowed_initial(url: str) -> bool:
    parsed = urlparse(url)
    host = (parsed.hostname or "").lower()
    if parsed.scheme != "https":
        return False
    return (
        host in PublicRedirects.allowed_exact
        or any(host.endswith(s) for s in PublicRedirects.allowed_suffixes)
    )


def get_bytes(url: str, *, max_bytes: int, accept: str = "*/*") -> tuple[bytes, str, str]:
    if not _allowed_initial(url):
        raise ContractError(f"URL outside read-back allowlist: {url}")
    req = Request(
        url,
        headers={
            "Accept": accept,
            "Accept-Encoding": "identity",
            "Cache-Control": "no-cache",
            "User-Agent": "SilverMarketResearch-CISS-Readback/0.1",
        },
    )
    opener = build_opener(PublicRedirects())
    with opener.open(req, timeout=45) as resp:
        if int(resp.status) != 200:
            raise ContractError(f"read-back HTTP {resp.status}: {url}")
        body = resp.read(max_bytes + 1)
        if not body or len(body) > max_bytes:
            raise ContractError(f"empty/oversized read-back: {url}")
        return body, resp.geturl(), resp.headers.get("Content-Type", "")


def get_json(url: str) -> tuple[dict, str]:
    raw, final_url, _ = get_bytes(url, max_bytes=MAX_JSON_BYTES, accept="application/json")
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ContractError(f"invalid JSON from {url}") from exc
    if not isinstance(payload, dict):
        raise ContractError(f"JSON root is not object: {url}")
    return payload, final_url


def extract_tag(snapshot_url: str, repository: str = EXPECTED_REPOSITORY) -> str:
    prefix = f"https://github.com/{repository}/releases/download/"
    if not snapshot_url.startswith(prefix):
        raise ContractError("snapshot URL does not use expected GitHub Release path")
    rest = snapshot_url[len(prefix):]
    parts = rest.split("/", 1)
    if len(parts) != 2 or not parts[0]:
        raise ContractError("invalid snapshot Release URL")
    return parts[0]


def _parse_utc(raw: str) -> datetime:
    try:
        dt = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ContractError(f"invalid UTC timestamp: {raw!r}") from exc
    if dt.tzinfo is None:
        raise ContractError("timestamp is not timezone-aware")
    return dt.astimezone(timezone.utc)


def audit_public_route(
    *,
    base_url: str = DEFAULT_BASE_URL,
    repository: str = EXPECTED_REPOSITORY,
    require_unexpired: bool = True,
) -> dict:
    base = base_url.rstrip("/")
    current_url = f"{base}/current.json"
    pages_dataset_url = f"{base}/ciss_current.csv"
    pages_manifest_url = f"{base}/ciss_current_manifest.json"

    current, current_final = get_json(current_url)
    required_states = {
        "validation_status": "PASS",
        "freshness_status": "HEALTHY",
        "release_audit_status": "PASS",
        "revision_governance_status": "ACCEPTED_CURRENT_VINTAGE",
        "source": "ECB_OFFICIAL",
        "series_key": "CISS.D.U2.Z0Z.4F.EC.SS_CIN.IDX",
    }
    for field, expected in required_states.items():
        if current.get(field) != expected:
            raise ContractError(f"current pointer {field} mismatch: {current.get(field)!r}")

    if require_unexpired:
        valid_until = _parse_utc(current["valid_until_utc"])
        if valid_until <= datetime.now(timezone.utc):
            raise ContractError("current pointer TTL expired")

    snapshot_url = current["snapshot_url"]
    snapshot_manifest_url = current["snapshot_manifest_url"]
    tag = extract_tag(snapshot_url, repository)
    if extract_tag(snapshot_manifest_url, repository) != tag:
        raise ContractError("snapshot and manifest Release tags differ")

    release_dataset, release_dataset_final, _ = get_bytes(
        snapshot_url,
        max_bytes=MAX_DATASET_BYTES,
        accept="text/csv",
    )
    release_manifest_raw, release_manifest_final, _ = get_bytes(
        snapshot_manifest_url,
        max_bytes=MAX_JSON_BYTES,
        accept="application/json",
    )
    release_dataset_sha = sha256_bytes(release_dataset)
    release_manifest_sha = sha256_bytes(release_manifest_raw)

    if release_dataset_sha != current["sha256_dataset"]:
        raise ContractError("Release dataset SHA-256 mismatch")
    if release_manifest_sha != current["snapshot_manifest_sha256"]:
        raise ContractError("Release manifest SHA-256 mismatch")

    manifest = json.loads(release_manifest_raw)
    if manifest.get("tag") != tag:
        raise ContractError("manifest tag mismatch")
    if manifest.get("canonical_dataset", {}).get("sha256") != release_dataset_sha:
        raise ContractError("manifest dataset SHA-256 mismatch")

    pages_dataset, pages_dataset_final, _ = get_bytes(
        pages_dataset_url,
        max_bytes=MAX_DATASET_BYTES,
        accept="text/csv",
    )
    pages_manifest_raw, pages_manifest_final, _ = get_bytes(
        pages_manifest_url,
        max_bytes=MAX_JSON_BYTES,
        accept="application/json",
    )
    if pages_dataset != release_dataset:
        raise ContractError("Pages dataset differs from immutable Release dataset")
    if pages_manifest_raw != release_manifest_raw:
        raise ContractError("Pages manifest differs from immutable Release manifest")

    release_api_url = f"https://api.github.com/repos/{repository}/releases/tags/{tag}"
    release_api, release_api_final = get_json(release_api_url)
    if release_api.get("immutable") is not True:
        raise ContractError("GitHub Release is not immutable")
    if release_api.get("tag_name") != tag:
        raise ContractError("GitHub Release tag mismatch")

    asset_digests = {
        asset.get("name"): asset.get("digest")
        for asset in release_api.get("assets", [])
        if isinstance(asset, dict)
    }
    expected_assets = {
        "ciss_snapshot.csv": f"sha256:{release_dataset_sha}",
        "ciss_snapshot_manifest.json": f"sha256:{release_manifest_sha}",
        "revision_report.csv": f"sha256:{manifest['revision_governance']['revision_report_sha256']}",
    }
    for name, expected_digest in expected_assets.items():
        if asset_digests.get(name) != expected_digest:
            raise ContractError(f"Release asset digest mismatch for {name}")

    return {
        "status": "PASS",
        "repository": repository,
        "pages_base_url": base,
        "release_tag": tag,
        "immutable": True,
        "dataset_sha256": release_dataset_sha,
        "manifest_sha256": release_manifest_sha,
        "revision_report_sha256": manifest["revision_governance"]["revision_report_sha256"],
        "row_count": current["canonical_row_count"],
        "first_observation": current["canonical_first_observation"],
        "last_observation": current["canonical_last_observation"],
        "current_valid_until_utc": current["valid_until_utc"],
        "final_urls": {
            "current": current_final,
            "pages_dataset": pages_dataset_final,
            "pages_manifest": pages_manifest_final,
            "release_dataset": release_dataset_final,
            "release_manifest": release_manifest_final,
            "release_api": release_api_final,
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default=DEFAULT_BASE_URL)
    parser.add_argument("--repository", default=EXPECTED_REPOSITORY)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    report = audit_public_route(base_url=args.base_url, repository=args.repository)
    path = Path(args.output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
