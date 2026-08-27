#!/usr/bin/env python3
"""research-sweep.py — curl-based research fetcher (fallback when web_search
is down). Feeds the frontier/geopolitics crons; signature matches the cron
prompts: research-sweep.py <kind> "<query1>" ["<query2>"...] --days N --out PATH

Sources (stdlib only): HN Algolia, arXiv API, The Register AI atom feed.
"""
import argparse, datetime, json, sys, time, urllib.parse, urllib.request, xml.etree.ElementTree as ET

UA = {"User-Agent": "agent1-research-sweep/1.0 (hub)"}


def get(url, timeout=30):
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def hn(query, days):
    since = int(time.time()) - days * 86400
    q = urllib.parse.quote(query)
    url = (f"https://hn.algolia.com/api/v1/search?query={q}&tags=story"
           f"&numericFilters=created_at_i>{since}&hitsPerPage=8")
    try:
        d = json.loads(get(url))
        out = []
        for h in d.get("hits", []):
            out.append((h.get("title", ""), h.get("url") or f"https://news.ycombinator.com/item?id={h.get('objectID')}",
                       h.get("created_at", ""), h.get("points", 0)))
        return out
    except Exception as e:
        return [("HN ERROR: " + str(e), "", "", 0)]


def arxiv(query, days):
    since = (datetime.date.today() - datetime.timedelta(days=days)).isoformat()
    q = urllib.parse.quote(f'all:"{query}"')
    url = (f"http://export.arxiv.org/api/query?search_query={q}"
           f"&sortBy=submittedDate&sortOrder=descending&max_results=5"
           f"&start=0")
    try:
        root = ET.fromstring(get(url))
        ns = {"a": "http://www.w3.org/2005/Atom"}
        out = []
        for e in root.findall("a:entry", ns)[:5]:
            title = " ".join(e.find("a:title", ns).text.split())
            link = e.find("a:id", ns).text
            pub = e.find("a:published", ns).text
            out.append((title, link, pub, 0))
        return out
    except Exception as e:
        return [("ARXIV ERROR: " + str(e), "", "", 0)]


def rss(url, days, max_items=8):
    try:
        root = ET.fromstring(get(url))
        out = []
        for item in root.iter("item"):
            title = item.findtext("title", "")
            link = item.findtext("link", "")
            date = item.findtext("pubDate", "")
            out.append((title, link, date, 0))
            if len(out) >= max_items:
                break
        return out
    except Exception as e:
        return [("RSS ERROR: " + str(e), "", "", 0)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("kind", help="frontier-ai | geopolitics | ...")
    ap.add_argument("queries", nargs="+")
    ap.add_argument("--days", type=int, default=2)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()

    lines = [f"# {args.kind} sweep — {datetime.date.today().isoformat()} (fallback fetcher)"]
    lines.append("")
    for query in args.queries:
        lines.append(f"## {query}")
        for src, fn in (("HN", lambda: hn(query, args.days)),
                        ("arXiv", lambda: arxiv(query, args.days)),
                        ("The Register AI", lambda: rss("https://www.theregister.com/security/ai/headlines.atom", args.days))):
            items = fn()
            lines.append(f"\n### {src}")
            for title, link, date, pts in items:
                lines.append(f"- {title} | {link} | {date}" + (f" | {pts} pts" if pts else ""))
    with open(args.out, "w") as f:
        f.write("\n".join(lines) + "\n")
    print(f"wrote {args.out} ({len(lines)} lines)")


if __name__ == "__main__":
    main()
