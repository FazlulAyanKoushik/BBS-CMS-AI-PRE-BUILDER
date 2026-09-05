"""CLI: build a site spec from a local CSV, either by calling the API or directly."""

from __future__ import annotations

import argparse
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests

from app.agent import AGENT_NAME, AIAgent1
from app.csv_loader import build_profiles_from_file
from app.schemas import SiteSpec


def run_direct(path: str, criteria: dict, row_index: int) -> dict:
    profiles = build_profiles_from_file(path)
    profile = profiles[row_index]
    agent = AIAgent1()
    spec: SiteSpec = agent.generate(profile, criteria)
    return {
        "agent_name": AGENT_NAME,
        "provider": agent.provider_name,
        "site_spec": spec.model_dump(exclude_none=True),
    }


def run_http(base_url: str, path: str, criteria: dict, row_index: int) -> dict:
    with open(path, "rb") as fh:
        resp = requests.post(
            f"{base_url.rstrip('/')}/api/generate",
            files={"file": fh},
            data={"criteria_json": json.dumps(criteria, ensure_ascii=False), "row_index": row_index},
            timeout=120,
        )
    resp.raise_for_status()
    return resp.json()


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate a website structure spec from a business CSV.")
    parser.add_argument("csv", help="Path to the business CSV file.")
    parser.add_argument("--criteria", default="{}", help='JSON criteria, e.g. \'{"language":"ja"}\'. Use "-" to read JSON from stdin.')
    parser.add_argument("--row", type=int, default=0, help="CSV data row to use (0-based).")
    parser.add_argument("--api", default=None, help="If set, call this FastAPI base URL instead of running locally.")
    parser.add_argument("--output", default=None, help="Write JSON output to this file.")
    args = parser.parse_args()

    criteria_text = args.criteria
    if criteria_text.strip() == "-":
        criteria_text = sys.stdin.read()

    try:
        criteria = json.loads(criteria_text)
    except json.JSONDecodeError:
        parser.error("--criteria must be valid JSON.")

    result = (
        run_http(args.api, args.csv, criteria, args.row)
        if args.api
        else run_direct(args.csv, criteria, args.row)
    )

    text = json.dumps(result, ensure_ascii=False, indent=2)
    if args.output:
        with open(args.output, "w", encoding="utf-8") as fh:
            fh.write(text + "\n")
        print(f"Wrote spec to {args.output}")
    else:
        print(text)


if __name__ == "__main__":
    main()