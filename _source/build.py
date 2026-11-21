"""Regenerate the buildless GitHub Pages HTML with python3 _source/build.py."""
import json
import posixpath
from html import escape
from pathlib import Path
from urllib.parse import quote

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "_source"
APPS = json.loads((SOURCE / "apps.json").read_text())
INBOX = "RhinoBuildsSupport@gmail.com"


def route(slug, tab="overview"):
    if tab == "overview":
        return f"{slug}/"
    if slug == "breathboss":
        return f"{tab}.html"
    return f"{slug}/{tab}/"


def url(page, dest):
    relative = posixpath.relpath(dest.rstrip("/") or ".", posixpath.dirname(page) or ".")
    return relative + "/" if dest.endswith("/") else relative


def link(page, dest, label, classes="", active=False):
    attrs = ' aria-current="page"' if active else ""
    return f'<a href="{url(page, dest)}" class="{classes}"{attrs}>{escape(label)}</a>'


def email(name, text, kind="Support", classes=""):
    subject = quote(f"{name} {kind}")
    return f'<a class="{classes}" href="mailto:{INBOX}?subject={subject}">{escape(text)}</a>'


def icon(page, slug):
    return f'<img class="icon" src="{url(page, "assets/"+slug+"-icon.jpg")}" width="64" height="64" alt="">'


def sections(rows):
    return "".join(f'<section><h2>{escape(title)}</h2><p>{escape(copy)}</p></section>' for title, copy in rows)


def write(page, title, description, content, selected=None, hub=False):
    path = ROOT / page
    path.parent.mkdir(parents=True, exist_ok=True)
    tabs = "".join(link(page, route(s), a["name"], "tab", selected == s and page == s+"/index.html")
                   if s != selected or page == s+"/index.html" else
                   f'<a class="tab selected" href="{url(page,route(s))}">{a["name"]}</a>'
                   for s,a in APPS.items())
    brand = (f'<a class="brand" aria-label="RhinoBuilds! home" href="{url(page, "./")}">'
             f'<img class="brand-emblem" src="{url(page,"assets/rhino-mark.png")}" width="64" height="56" alt="">'
             '<span class="wordmark"><b>Rhino</b>Builds<i>!</i></span></a>')
    gallery_script = (f'<script src="{url(page, "gallery.js")}" defer></script>'
                      if selected and page == selected+"/index.html" else "")
    app_link = link(page, "./", "Apps", "global-link", page=="index.html")
    help_link = link(page, "support/", "Support", "global-link", hub)
    html = f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{escape(title)} · Rhino Builds</title><meta name="description" content="{escape(description, quote=True)}">
<meta name="color-scheme" content="light"><link rel="stylesheet" href="{url(page, 'styles.css')}">{gallery_script}</head>
<body class="{selected or 'studio'}"><a href="#main" class="skip">Skip to content</a>
<header><div class="wrap mast">{brand}<nav class="global" aria-label="Site navigation">{app_link}{help_link}</nav></div>
<nav class="tabbar" aria-label="App collection"><div class="wrap tabs">{tabs}</div></nav></header>
<main id="main" class="wrap">{content}</main>
<footer><div class="wrap foot">{brand}<div>{link(page, "./","All apps")}{link(page, "support/", "Support directory")}</div></div></footer>
</body></html>"""
    path.write_text(html + "\n", encoding="utf-8")


def directory_card(page, slug, app, support=False):
    dest = route(slug, "support" if support else "overview")
    title = escape(app["name"])
    detail = "Support and contact" if support else escape(app["summary"])
    return f'<a class="card {slug}" href="{url(page,dest)}">{icon(page,slug)}<div><span class="category">{escape(app["category"])}</span><h3>{title}</h3><p>{detail}</p></div></a>'


def directory(page, support=False):
    return '<div class="cards">' + "".join(directory_card(page,s,a,support) for s,a in APPS.items()) + '</div>'


def crumbs(page, slug, current):
    return '<nav class="crumbs" aria-label="Breadcrumb">'+link(page,"./","Apps")+'<span aria-hidden="true">/</span>'+link(page,route(slug),APPS[slug]["name"])+'<span aria-hidden="true">/</span><span>'+current+'</span></nav>'


def home():
    page = "index.html"
    hero = f"""<section class="hero"><img class="hero-art" src="{url(page,'assets/astral-ring.jpg')}" alt="" fetchpriority="high">
<div class="hero-copy"><h1>The app<br>collection<span>.</span></h1>
<p>Four iPhone apps from Rhino Builds for changing habits and tracking nutrition.</p><a class="button light" href="#apps">Explore the apps</a></div>
<a class="art-credit" href="{url(page,route('resistboss'))}">ResistBoss <span>/</span> The Astral Ring</a></section>"""
    write(page,"The app collection","Explore the four iPhone apps from Rhino Builds and find app-specific support and privacy information.",
          hero + '<section class="collection" id="apps"><h2>Browse the apps</h2>'+directory(page)+'</section>')
    page = "support/index.html"
    body = '<div class="directory-title"><p class="category">Rhino Builds</p><h1>App support</h1><p class="lead">Choose your app to find answers and email the support team.</p></div>'
    write(page, "App support", "Contact Rhino Builds for help with any of our four apps.", body+directory(page,True),hub=True)


def gallery(page, slug, app):
    # Each entry describes a reviewed, public image.
    previews = app["previews"]
    first = previews[0]
    first_url = url(page, first["asset"])
    controls = []
    for index, item in enumerate(previews):
        image_url = url(page, item["asset"])
        label = escape(item["label"], quote=True)
        alt = escape(item["alt"], quote=True)
        thumb = url(page, item["thumb"])
        note = escape(item["note"], quote=True)
        selected = ' aria-current="true"' if index == 0 else ""
        controls.append(f'<li><a {selected} href="{image_url}" data-preview data-alt="{alt}" '
                        f'data-label="{label}" data-note="{note}"><img width="58" height="72" loading="lazy" '
                        f'src="{thumb}" alt=""><span>{label}</span></a></li>')
    nav = ('<nav aria-label="App previews"><ul class="preview-choices">' + "".join(controls) + '</ul></nav>'
           if len(previews) > 1 else "")
    note = f'<small data-note-line>{escape(first["note"])}</small>'
    return (f'<div class="gallery" data-gallery><figure><a data-full href="{first_url}" '
            'aria-label="Open full-size preview"><img data-main fetchpriority="high" '
            f'src="{first_url}" alt="{escape(first["alt"], quote=True)}"></a>'
            f'<figcaption><strong data-caption aria-live="polite">{escape(first["label"])}</strong>'
            f'{note}</figcaption></figure>{nav}</div>')


def app_pages(slug, app):
    name = app["name"]
    overview = slug+"/index.html"
    go_support = link(overview,route(slug,"support"),"Get support","button dark")
    go_privacy = link(overview,route(slug,"privacy"),"Privacy policy","button plain")
    details = "".join(f'<section><h3>{escape(t)}</h3><p>{escape(c)}</p></section>' for t,c in app["features"])
    body = f"""<section class="product"><div class="product-copy">{icon(overview,slug)}<p class="category">{escape(app["category"])}</p>
<h1>{name}</h1><p class="lead">{escape(app["intro"])}</p><div class="actions">{go_support}{go_privacy}</div></div>
{gallery(overview,slug,app)}</section>
<section class="features"><h2>Inside {name}</h2><div>{details}</div></section>"""
    write(overview, name, app["summary"], body, slug)
    for tab in ["support","privacy"]:
        dest = route(slug,tab)
        page = dest + "index.html" if dest.endswith("/") else dest
        is_help = tab == "support"
        label = "Support" if is_help else "Privacy policy"
        intro = app["support"] if is_help else app.get("privacyIntro", "How BreathBoss handles account access, progress tracking, community features, and related app services.")
        lead = f'<div class="dochead">{icon(page,slug)}<div><p class="category">{label}</p><h1>{name} {"support" if is_help else "privacy policy"}</h1></div></div><p class="lead">{escape(intro)}</p>'
        contact = email(name,"Email support" if is_help else "Email a privacy question","Support" if is_help else "Privacy","button dark")
        address = email(name,INBOX,"Support" if is_help else "Privacy","address")
        other = link(page,route(slug,"privacy" if is_help else "support"),"Privacy policy" if is_help else "App support","related")
        aside = f'<aside><h2>Contact Rhino Builds</h2>{contact}{address}<div>{other}</div></aside>'
        if slug == "breathboss":
            body = (SOURCE / f"breathboss-{tab}.html").read_text()
            body = body.replace("mailto:"+INBOX, "mailto:"+INBOX+"?subject="+quote("BreathBoss Privacy" if not is_help else "BreathBoss Support"))
        else:
            body = sections(app["faq"] if is_help else app["privacy"])
            if not is_help:
                body += sections([("Contacting support", "If you email Rhino Builds, we receive the email address and information you choose to send so we can respond. You can ask about access, correction, or removal at the address on this page.")])
        if not is_help:
            date = "July 9, 2026" if slug=="breathboss" else "November 20, 2026"
            lead += f'<p class="date">Effective {date}</p>'
        write(page, name+" "+label, intro, crumbs(page,slug,label) + '<article class="doc">'+lead+f'<div class="docgrid">{aside}<div class="docbody">{body}</div></div></article>',slug)


if __name__ == "__main__":
    home()
    for key, item in APPS.items():
        app_pages(key,item)
