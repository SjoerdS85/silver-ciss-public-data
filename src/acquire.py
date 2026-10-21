from __future__ import annotations

import argparse
import json
import time
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import HTTPRedirectHandler, Request, build_opener

from .common import ContractError, load_json, sha256_bytes

class StrictRedirects(HTTPRedirectHandler):
    def __init__(self, allowed_hosts: set[str]):
        super().__init__()
        self.allowed_hosts = allowed_hosts
        self.chain: list[str] = []

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        parsed = urlparse(newurl)
        if parsed.scheme != "https" or parsed.hostname not in self.allowed_hosts:
            raise ContractError(f"unexpected redirect: {newurl}")
        self.chain.append(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)

@dataclass
class FetchResult:
    request_url: str
    final_url: str
    retrieval_timestamp_utc: str
    http_status: int
    content_type: str
    content_encoding: str
    byte_count: int
    sha256: str
    redirect_chain: list[str]
    body_path: str

def fetch(url: str, contract: dict, target: Path) -> FetchResult:
    parsed = urlparse(url)
    allowed = set(contract["allowed_redirect_hosts"])
    if parsed.scheme != "https" or parsed.hostname not in allowed:
        raise ContractError("source URL outside allowlist")
    retries = int(contract["max_retries"])
    for attempt in range(retries + 1):
        redirects = StrictRedirects(allowed)
        opener = build_opener(redirects)
        req = Request(url, headers={
            "Accept": "text/csv",
            "Accept-Encoding": "identity",
            "Cache-Control": "no-cache",
            "User-Agent": contract["user_agent"],
        })
        try:
            with opener.open(req, timeout=float(contract["timeout_seconds"])) as resp:
                if int(resp.status) != 200:
                    raise ContractError(f"HTTP {resp.status}")
                content_type = resp.headers.get_content_type()
                if content_type not in set(contract["allowed_content_types"]):
                    raise ContractError(f"unexpected content type: {content_type}")
                encoding = resp.headers.get("Content-Encoding", "identity")
                if encoding.lower() != "identity":
                    raise ContractError(f"unexpected content encoding: {encoding}")
                body = resp.read(int(contract["max_response_bytes"]) + 1)
                if not body or len(body) > int(contract["max_response_bytes"]):
                    raise ContractError("empty or oversized response")
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(body)
                ts = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
                return FetchResult(url, resp.geturl(), ts, 200, content_type, encoding, len(body), sha256_bytes(body), redirects.chain, str(target))
        except HTTPError as exc:
            if attempt >= retries or not (exc.code == 429 or 500 <= exc.code <= 599):
                raise ContractError(f"HTTP acquisition failure: {exc.code}") from exc
        except URLError as exc:
            if attempt >= retries:
                raise ContractError(f"network acquisition failure: {exc.reason}") from exc
        time.sleep(2 ** attempt)
    raise ContractError("acquisition exhausted retries")

def acquire_pair(contract_path: str, output_dir: str) -> dict:
    contract = load_json(contract_path)
    out = Path(output_dir)
    full = fetch(contract["source_url"], contract, out / "ciss_full_raw.csv")
    tail = fetch(contract["tail_url"], contract, out / "ciss_tail_raw.csv")
    result = {"full": asdict(full), "tail": asdict(tail)}
    (out / "acquisition.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result

def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--contract", default="config/ciss_contract_v1.json")
    p.add_argument("--output-dir", required=True)
    a = p.parse_args()
    acquire_pair(a.contract, a.output_dir)
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
