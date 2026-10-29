#!/usr/bin/env python3
"""
Write DataCite JSON (one record per line) for datasets in the Zenodo
'nsfncar' community.

1. OAI-PMH ListIdentifiers on set 'user-nsfncar' -> Zenodo record ids
2. For each id, ask Zenodo's REST API for its DataCite JSON serialization

    pip install sickle requests
    python zenodo_nsfncar_datacite_json.py
"""
import json
import os
import sys
import time

import requests
from sickle import Sickle

SET = "user-nsfncar"
OUT = "nsfncar_datacite.jsonl"
DATACITE_JSON = "application/vnd.datacite.datacite+json"
PAUSE = 1.0          # seconds between record requests; be gentle
ONLY_DATASETS = False


def record_ids():
    sickle = Sickle("https://zenodo.org/oai2d", max_retries=5,
                    retry_status_codes=(429, 503), default_retry_after=30)
    for header in sickle.ListIdentifiers(metadataPrefix="oai_dc", set=SET,
                                         ignore_deleted=True):
        # identifiers look like 'oai:zenodo.org:1234567'
        yield header.identifier.rsplit(":", 1)[-1]


def fetch_datacite(session, rec_id):
    urls = [
        f"https://zenodo.org/api/records/{rec_id}",              # content negotiation
        f"https://zenodo.org/records/{rec_id}/export/datacite-json",  # fallback
    ]
    for url in urls:
        for _ in range(5):
            r = session.get(url, headers={"Accept": DATACITE_JSON}, timeout=60)
            if r.status_code == 429:
                time.sleep(int(r.headers.get("Retry-After", 60)))
                continue
            break
        if r.ok:
            try:
                data = r.json()
            except ValueError:
                continue
            # Sanity check: DataCite JSON has 'types'/'titles', not 'metadata'
            if "titles" in data:
                return data
    raise RuntimeError(f"No DataCite JSON for record {rec_id} (last HTTP {r.status_code})")


def main():
    session = requests.Session()
    token = os.environ.get("ZENODO_TOKEN")
    if token:
        session.headers["Authorization"] = f"Bearer {token}"

    ids = list(record_ids())
    print(f"{len(ids)} records in {SET}", file=sys.stderr)

    kept = 0
    with open(OUT, "w", encoding="utf-8") as f:
        for i, rec_id in enumerate(ids, 1):
            try:
                dc = fetch_datacite(session, rec_id)
            except Exception as e:
                print(f"  skip {rec_id}: {e}", file=sys.stderr)
                continue
            finally:
                time.sleep(PAUSE)

            rtg = dc.get("types", {}).get("resourceTypeGeneral")
            if ONLY_DATASETS and rtg != "Dataset":
                continue
            f.write(json.dumps(dc, ensure_ascii=False) + "\n")
            kept += 1
            if i % 25 == 0:
                print(f"  {i}/{len(ids)} checked, {kept} datasets", file=sys.stderr)

    print(f"Wrote {kept} DataCite JSON records to {OUT}", file=sys.stderr)


if __name__ == "__main__":
    main()
