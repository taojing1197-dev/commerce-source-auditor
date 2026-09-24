#!/usr/bin/env python3
"""Audit a portable commerce manifest using only the Python standard library."""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any
from urllib.parse import urlparse, urlunparse


def valid_url(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    parsed = urlparse(value.strip())
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def canonical_url(value: str) -> str:
    parsed = urlparse(value.strip())
    path = parsed.path.rstrip("/") or "/"
    return urlunparse((parsed.scheme.lower(), parsed.netloc.lower(), path, parsed.params, parsed.query, ""))


def issue(level: str, code: str, index: int, product_id: str, message: str) -> dict[str, Any]:
    return {"level": level, "code": code, "index": index, "product_id": product_id, "message": message}


def load_products(path: Path) -> list[Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        for key in ("products", "items"):
            if isinstance(data.get(key), list):
                return data[key]
    raise ValueError("top level must be an array or an object containing products/items")


def audit(products: list[Any]) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    ids: defaultdict[str, list[int]] = defaultdict(list)
    sources: defaultdict[str, list[int]] = defaultdict(list)

    for index, raw in enumerate(products):
        if not isinstance(raw, dict):
            findings.append(issue("error", "invalid_product", index, "", "product must be an object"))
            continue

        product_id = str(raw.get("id", "")).strip()
        title = str(raw.get("title", "")).strip()
        source_url = raw.get("source_url")
        if not product_id:
            findings.append(issue("error", "missing_id", index, "", "stable product id is required"))
        else:
            ids[product_id].append(index)
        if not title:
            findings.append(issue("error", "missing_title", index, product_id, "title is required"))
        if not valid_url(source_url):
            findings.append(issue("error", "invalid_source_url", index, product_id, "source_url must be an HTTP(S) URL"))
        else:
            sources[canonical_url(str(source_url))].append(index)

        images = raw.get("images", [])
        if not isinstance(images, list):
            findings.append(issue("error", "invalid_images", index, product_id, "images must be an array"))
        elif not images:
            findings.append(issue("warning", "missing_images", index, product_id, "no product image is recorded"))
        else:
            for image_index, image_value in enumerate(images):
                if not isinstance(image_value, str) or not image_value.strip():
                    findings.append(issue("error", "invalid_image", index, product_id, f"image {image_index} is empty"))

        claims = raw.get("claims", [])
        if not isinstance(claims, list):
            findings.append(issue("error", "invalid_claims", index, product_id, "claims must be an array"))
            continue
        for claim_index, claim in enumerate(claims):
            if not isinstance(claim, dict) or not str(claim.get("text", "")).strip():
                findings.append(issue("error", "invalid_claim", index, product_id, f"claim {claim_index} needs text"))
                continue
            evidence = claim.get("evidence")
            if not isinstance(evidence, dict) or not valid_url(evidence.get("source_url")):
                findings.append(issue("error", "missing_evidence_url", index, product_id, f"claim {claim_index} needs an evidence source_url"))
                continue
            if not any(str(evidence.get(key, "")).strip() for key in ("quote", "field", "value")):
                findings.append(issue("error", "missing_evidence_detail", index, product_id, f"claim {claim_index} needs quote, field, or value evidence"))

    for product_id, indexes in ids.items():
        if len(indexes) > 1:
            for index in indexes:
                findings.append(issue("error", "duplicate_id", index, product_id, f"id appears at indexes {indexes}"))
    for source_url, indexes in sources.items():
        if len(indexes) > 1:
            for index in indexes:
                product_id = str(products[index].get("id", "")) if isinstance(products[index], dict) else ""
                findings.append(issue("warning", "duplicate_source", index, product_id, f"source URL appears at indexes {indexes}"))
    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--json", action="store_true", dest="as_json")
    parser.add_argument("--strict", action="store_true", help="fail on warnings")
    args = parser.parse_args()
    try:
        products = load_products(args.manifest)
        findings = audit(products)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    errors = sum(item["level"] == "error" for item in findings)
    warnings = sum(item["level"] == "warning" for item in findings)
    result = {"products": len(products), "errors": errors, "warnings": warnings, "findings": findings}
    if args.as_json:
        print(json.dumps(result, ensure_ascii=False, indent=2))
    else:
        print(f"products={len(products)} errors={errors} warnings={warnings}")
        for item in findings:
            print(f"{item['level'].upper()} {item['code']} index={item['index']} id={item['product_id']}: {item['message']}")
    return 1 if errors or (args.strict and warnings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
