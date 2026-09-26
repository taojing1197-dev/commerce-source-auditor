# Commerce Source Auditor

An open-source Codex skill and zero-dependency CLI for auditing product-catalog provenance before publication.

It checks stable IDs, source URLs, evidence-backed claims, image records, and duplicate IDs or equivalent source pages. URL matching normalizes host case, fragments, and trailing slashes without discarding meaningful query parameters. The skill is useful for marketplace imports, AI-assisted commerce copy, catalog migrations, and product-data synchronization.

Required text fields reject JSON `null` values instead of accidentally treating them as the literal text `None`.
Source and evidence URLs containing embedded usernames or passwords are rejected to prevent credentials from leaking into catalogs and reports.

## Install and use

Copy this repository into your Codex skills directory, or run the CLI directly:

```bash
python3 scripts/audit_manifest.py path/to/catalog.json
python3 -m unittest discover -s tests -v
```

See `references/manifest-format.md` for the portable manifest format.

## Contributing

Issues and pull requests with anonymized fixtures are welcome. Do not submit customer data, credentials, or copyrighted merchant copy.

## License

MIT
