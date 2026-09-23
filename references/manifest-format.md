# Portable audit manifest

Use this format when a source catalog can be exported without losing business-specific fields.

```json
{
  "products": [
    {
      "id": "sku-001",
      "title": "Verified product title",
      "source_url": "https://merchant.example/products/sku-001",
      "images": ["https://merchant.example/images/sku-001.jpg"],
      "claims": [
        {
          "text": "100% cotton",
          "evidence": {
            "source_url": "https://merchant.example/products/sku-001",
            "quote": "Material: cotton 100%"
          }
        }
      ]
    }
  ]
}
```

The top level may instead be a JSON array or use `items`. Each claim needs a non-empty `text` and evidence containing a product-specific `source_url` plus either `quote`, `field`, or `value`.

Run:

```bash
python3 scripts/audit_manifest.py catalog.json
python3 scripts/audit_manifest.py catalog.json --json
python3 scripts/audit_manifest.py catalog.json --strict
```

Errors always return exit code 1. Warnings return exit code 1 only with `--strict`.
