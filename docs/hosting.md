# Hosting notes

The production base URL remains `https://darkechoproject.github.io/darkecho/`.

## robots.txt at the host root

Crawler rules are read from `https://darkechoproject.github.io/robots.txt`, not a repository subpath. The root URL currently returns 404. The corresponding account-root repository was not available through the connected GitHub account during this repair.

The project retains a clearly commented `robots.txt` copy for reuse. This copy is not described as a working host-root policy. Its absence at the host root does not prevent Google from crawling the public project pages.

If a root site or custom host becomes available, publish this at that host's `/robots.txt`, retaining any other projects' existing rules:

```text
User-agent: *
Allow: /

Sitemap: https://darkechoproject.github.io/darkecho/sitemap.xml
```

The project sitemap is linked from the website footer, contains indexable watch pages, and can be submitted directly to the site's verified Search Console property. No Search Console submission is claimed by this repository.

## Security policies

Pages include a Content Security Policy through a supported HTML meta tag, without inline executable JavaScript or inline style attributes. JSON-LD has a matching content hash in the policy. The referrer policy is also set through HTML metadata and on video frames. YouTube uses the privacy-enhanced host, and homepage/archive players load on request.

GitHub Pages controls HTTP response headers. A meta policy cannot supply `frame-ancestors`, `X-Content-Type-Options`, or an HTTP `Permissions-Policy`. Those require host-level configuration or a suitable proxy. They have not been represented as repaired by adding unsupported meta tags. Existing HTTPS and HSTS remain provided by the host.

## Privacy and measurement

The prior `darkecho-analytics-choice-v1` preference is retained. Rejection prevents loading Google Analytics; custom interaction events are sent only after consent. Revocation disables the property, removes the known site Analytics cookies, and reloads to remove the active tag. The change is synchronized to other open site tabs. Video watch pages load a YouTube frame independently of this choice, as explained in the privacy policy.
