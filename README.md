# research-sweep

A stdlib-only research fetcher that pulls recent AI/tech content from public
sources — designed as a fallback when a search API is unavailable.

```
python3 research-sweep.py frontier "AI agents" "scaling laws" --days 7 --out frontier.md
python3 research-sweep.py geopolitics "EU AI act" --days 3 --out geo.md
```

## Sources (stdlib only, no dependencies)

- **HN Algolia** — Hacker News story search
- **arXiv API** — sorted by submitted date (desc)
- **The Register AI atom feed** — recent AI news

## Features

- Multiple queries per run, results merged and deduplicated
- `--days N` recency filter, `--out PATH` output file
- Zero third-party dependencies — works on any Python 3.8+
- Signature matches a nightly research cron pipeline (frontier/geopolitics)

## Output

Markdown with sections per source/query, timestamps, and URLs — ready to be
fed into an LLM summarizer or saved as a research log.
