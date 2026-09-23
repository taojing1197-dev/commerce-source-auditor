---
name: commerce-source-auditor
description: Audit product catalogs, marketplace imports, and AI-generated commerce copy for source traceability, duplicate records, unsupported claims, and missing product evidence. Use before publishing or synchronizing product data; do not use as a general website QA skill.
---

# Commerce Source Auditor

Protect the factual chain from a merchant or marketplace source to the final catalog. Treat the source as evidence, not as permission to copy its page design or marketing claims.

## Route the task

1. Identify the catalog format, publishing target, and source fields already retained.
2. If the data can be represented as the portable audit manifest, read [references/manifest-format.md](references/manifest-format.md) and run `scripts/audit_manifest.py`.
3. Otherwise, inspect the smallest relevant schema and adapt the checks without rewriting the user's catalog.
4. Separate errors that block publishing from warnings that need human review.

## Invariants

- Every product needs a stable ID, a source URL, and a non-empty title.
- Every factual claim needs product-specific evidence. A category page or brand homepage is not enough.
- Never invent sales, review counts, effects, ingredients, materials, colors, sizes, stock, certifications, or model attributes.
- Detect duplicates before choosing a canonical record. Prefer the record with stronger provenance and richer verified data; preserve identifiers needed by downstream systems.
- Original source facts and source image URLs may be retained, but do not reproduce a source site's layout or copyrighted marketing copy.
- An audit does not authorize publishing, account actions, or production data changes.

## Deliverable

Report blocking errors, review warnings, duplicate groups, and the exact records affected. When asked to fix data, preserve the original file format and unrelated fields, then rerun the audit.
