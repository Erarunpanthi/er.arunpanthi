# Search visibility and privacy

The site uses `noindex, nofollow` on its HTML pages to request removal from
search results. `robots.txt` allows crawling so that search engines can see the
noindex directives; do not disallow pages there while requesting removal. No
sitemap is advertised. On Apache, `.htaccess` also sends `X-Robots-Tag` for
all resources, including non-HTML files. GitHub Pages ignores `.htaccess`, so
that header is not available there.

After deploying, Google needs to recrawl existing URLs before removing them;
this is not immediate or guaranteed. Use Google Search Console's Removals tool
for temporary expedited removal, and monitor both the old and new domains.
If the old site remains online, it must also serve noindex (or be taken offline).
For non-HTML files on GitHub Pages, use a host/proxy that can set the
`X-Robots-Tag` header, or remove the files from public hosting.

**Noindex is not access control.** The site and its assets remain accessible to
anyone with a URL, and search engines or other crawlers may not respect it.
To make the site genuinely private, use authentication enforced by the hosting
provider or an authenticated proxy, and restrict access to the repository and
all other published copies. GitHub Pages alone does not provide site-wide
password protection for a public site.

Run `python3 tools/test-noindex.py` to verify the HTML directives, crawler
access and custom domain. Redirect page generation uses noindex, and
`tools/fix-indexing.py` preserves the site-wide noindex policy.
