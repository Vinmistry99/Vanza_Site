#!/usr/bin/env python3
"""Post-process exported HTML for Vanza Cleaning Services site."""
import re
from pathlib import Path

BASE = Path(__file__).resolve().parent
BASE_URL = "https://www.vanzacleaning.co.uk"

PAGES = {
    "index.html": {
        "title": "Vanza Cleaning Services | London Home & Commercial Cleaning",
        "desc": "Premium residential and commercial cleaning in London. Deep cleans, end of tenancy, carpet cleaning, and more. Trusted, insured cleaners — book Vanza today.",
        "path": "/",
    },
    "about.html": {
        "title": "About Us | Vanza Cleaning Services London",
        "desc": "Meet Vanza Cleaning Services: our story, vetted cleaners, eco-friendly products, and the standards behind London's trusted home and office cleans.",
        "path": "/about.html",
    },
    "contact.html": {
        "title": "Contact & Get a Quote | Vanza Cleaning Services",
        "desc": "Contact Vanza Cleaning Services for quotes and bookings. Call, email, or send a message — serving Central and Greater London.",
        "path": "/contact.html",
    },
    "services.html": {
        "title": "Cleaning Services | Vanza Cleaning Services London",
        "desc": "Explore Vanza services: deep cleaning, end of tenancy, recurring cleans, one-off, carpet, and commercial cleaning across London.",
        "path": "/services.html",
    },
    "faq.html": {
        "title": "FAQ | Vanza Cleaning Services",
        "desc": "Answers about booking, pricing, what's included, end of tenancy, commercial cleans, and cancellations for Vanza Cleaning Services.",
        "path": "/faq.html",
    },
    "carpet-cleaning.html": {
        "title": "Carpet Cleaning | Vanza Cleaning Services London",
        "desc": "Professional hot water extraction carpet cleaning in London. Stain removal, allergen reduction, and fast drying — book Vanza.",
        "path": "/carpet-cleaning.html",
    },
    "one-off-cleaning.html": {
        "title": "One-Off Cleaning | Vanza Cleaning Services London",
        "desc": "Flexible one-off home cleaning in London for events, seasonal refreshes, or whenever you need a professional deep clean.",
        "path": "/one-off-cleaning.html",
    },
    "commercial-cleaning.html": {
        "title": "Commercial Cleaning | Vanza Cleaning Services London",
        "desc": "Office and commercial cleaning tailored to your business: flexible schedules, insured staff, and consistent standards across London.",
        "path": "/commercial-cleaning.html",
    },
    "end-of-tenancy.html": {
        "title": "End of Tenancy Cleaning | Vanza Cleaning Services London",
        "desc": "Inventory-ready end of tenancy cleaning with deposit-focused detail. Oven, appliances, and full property deep clean — Vanza.",
        "path": "/end-of-tenancy.html",
    },
    "deep-cleaning.html": {
        "title": "Deep Cleaning | Vanza Cleaning Services London",
        "desc": "Top-to-bottom deep cleaning for homes in London: kitchens, bathrooms, fixtures, and hard-to-reach areas — book with Vanza.",
        "path": "/deep-cleaning.html",
    },
}

HEAD_EXTRA = """
    <!-- Google Analytics 4 -->
    <script async src="https://www.googletagmanager.com/gtag/js?id=G-R9V3LE91J4"></script>
    <script>
      window.dataLayer = window.dataLayer || [];
      function gtag(){dataLayer.push(arguments);}
      gtag('js', new Date());
      gtag('config', 'G-R9V3LE91J4');
    </script>

    <!-- Meta Pixel -->
    <!--
    <script>
      !function(f,b,e,v,n,t,s)
      {if(f.fbq)return;n=f.fbq=function(){n.callMethod?
      n.callMethod.apply(n,arguments):n.queue.push(arguments)};
      if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';
      n.queue=[];t=b.createElement(e);t.async=!0;
      t.src=v;s=b.getElementsByTagName(e)[0];
      s.parentNode.insertBefore(t,s)}(window, document,'script',
      'https://connect.facebook.net/en_US/fbevents.js');
      fbq('init', '1447736763753517');
      fbq('track', 'PageView');
    </script>
    <noscript><img height="1" width="1" style="display:none" src="https://www.facebook.com/tr?id=1447736763753517&ev=PageView&noscript=1" alt="" /></noscript>
    -->

    <link rel="stylesheet" href="css/vanza.css">
"""


def strip_grapesjs(html: str) -> str:
    return re.sub(
        r'<style\s+data-grapesjs-styles="true">[\s\S]*?</style>\s*',
        "",
        html,
        count=1,
    )


def inject_seo(html: str, name: str) -> str:
    meta = PAGES[name]
    url = BASE_URL.rstrip("/") + meta["path"]
    title = meta["title"]
    desc = meta["desc"]

    # Replace or insert title
    html = re.sub(r"<title>[^<]*</title>", f"<title>{title}</title>", html, count=1)

    # Remove existing meta description if any, we'll add fresh
    html = re.sub(
        r'\s*<meta\s+name="description"\s*[^>]*>\s*',
        "\n",
        html,
    )

    block = f"""
    <meta name="description" content="{desc}">
    <meta name="robots" content="index, follow">
    <link rel="canonical" href="{url}">
    <meta property="og:title" content="{title}">
    <meta property="og:description" content="{desc}">
    <meta property="og:type" content="website">
    <meta property="og:url" content="{url}">
"""
    # Insert after viewport
    html = re.sub(
        r'(<meta\s+name="viewport"\s+content="width=device-width,\s*initial-scale=1\.0">)',
        r"\1" + block,
        html,
        count=1,
    )
    return html


def add_assets(html: str) -> str:
    if 'href="css/vanza.css"' not in html:
        html = html.replace("</head>", HEAD_EXTRA + "\n  </head>", 1)
    if 'src="js/vanza.js"' not in html:
        html = html.replace("</body>", '  <script src="js/vanza.js" defer></script>\n</body>', 1)
    return html


def fix_img(html: str) -> str:
    def repl(m):
        tag = m.group(0)
        if 'loading=' in tag:
            return tag
        if tag.endswith("/>"):
            return tag.replace("<img", "<img loading=\"lazy\"", 1)
        return tag.replace("<img", "<img loading=\"lazy\"", 1)

    return re.sub(r"<img\s[^>]+>", repl, html)


def noopener_external_anchors(html: str) -> str:
    """Add rel noopener noreferrer to <a href="http..."> external URLs."""

    out = []
    i = 0
    while True:
        start = html.find("<a ", i)
        if start == -1:
            out.append(html[i:])
            break
        out.append(html[i:start])
        end = html.find(">", start)
        if end == -1:
            out.append(html[start:])
            break
        tag = html[start : end + 1]
        hm = re.search(r'href="([^"]*)"', tag)
        if hm:
            href = hm.group(1)
            if (
                href.startswith("http://") or href.startswith("https://")
            ) and "rel=" not in tag.lower():
                tag = tag.replace("<a ", '<a rel="noopener noreferrer" ', 1)
        out.append(tag)
        i = end + 1
    return "".join(out)


def remove_scroll_progress_js(html: str) -> str:
    """Remove scroll progress lines only; vanza.js updates #scroll-progress."""
    html = re.sub(r"\s*// Scroll Progress\s*", "", html)
    return re.sub(
        r"\s*const winScroll = document\.body\.scrollTop \|\| document\s*\.documentElement\.scrollTop;\s*"
        r"const height = document\.documentElement\.scrollHeight - document\s*\.documentElement\.clientHeight;\s*"
        r"const scrolled = \(winScroll / height\) \* 100;\s*"
        r"document\.getElementById\(\"scroll-progress\"\)\.style\.width = scrolled\s*\+\s*\"%\";\s*",
        "\n",
        html,
    )


def nav_updates(html: str) -> str:
    html = re.sub(
        r'<nav class="hidden lg:flex',
        '<nav id="primary-nav" class="hidden lg:flex',
        html,
        count=1,
    )
    html = re.sub(
        r'(<button\s+)(class="lg:hidden[^"]*")',
        r'\1data-nav-toggle aria-controls="primary-nav" aria-expanded="false" aria-label="Open menu" \2',
        html,
        count=1,
    )
    return html


def fix_faq_logo(html: str) -> str:
    return html.replace(
        '<span class="font-playfair text-2xl font-bold tracking-tight text-vanza-textDark"><br></span>',
        '<span class="font-playfair text-2xl font-bold tracking-tight text-vanza-textDark">Vanza Cleaning</span>',
    )


def scrub_inline_progress_height(html: str) -> str:
    """Avoid conflicting heights; vanza.css sets 3px."""
    html = re.sub(
        r"(#scroll-progress\s*\{[^}]*?)height:\s*4px;",
        r"\1height: 3px;",
        html,
    )
    return html


def patch_body_scroll(html: str) -> str:
    """Prefer html { scroll-behavior } only."""
    html = re.sub(
        r"body\s*\{[^}]*scroll-behavior:\s*smooth;[^}]*\}",
        lambda m: m.group(0).replace("scroll-behavior: smooth;", ""),
        html,
        count=1,
    )
    return html


def main():
    for fname, _meta in PAGES.items():
        path = BASE / fname
        if not path.exists():
            print("Missing", path)
            continue
        html = path.read_text(encoding="utf-8")
        html = strip_grapesjs(html)
        html = inject_seo(html, fname)
        html = add_assets(html)
        html = fix_img(html)
        html = noopener_external_anchors(html)
        html = remove_scroll_progress_js(html)
        html = nav_updates(html)
        html = scrub_inline_progress_height(html)
        html = patch_body_scroll(html)
        if fname == "faq.html":
            html = fix_faq_logo(html)
        path.write_text(html, encoding="utf-8")
        print("OK", fname)


if __name__ == "__main__":
    main()
