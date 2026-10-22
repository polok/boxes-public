#!/usr/bin/env python3
"""Builds the static site: <lang>/{index,privacy,terms,support}.html for eight languages, the language
pickers at the root, the stylesheet and the images. Texts live in tools/content_*.py.

Usage (from the repo root):  python3 tools/build.py [--shots ../boxes-ios/fastlane/screenshots]
Needs Pillow only for the screenshots (`python3 -m pip install Pillow`); without --shots they are kept as they are.
"""
import html
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from content_de_fr import DE, FR  # noqa: E402
from content_en_pl import EN, PL  # noqa: E402
from content_es_it import ES, IT  # noqa: E402
from content_ja_zh import JA, ZH  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
LANGS = [PL, EN, DE, IT, ES, FR, ZH, JA]
PAGES = ["privacy", "terms", "support"]
MAIL = "marcin.polak@ideaapps.io"
APP_STORE = "https://apps.apple.com/app/id6825208997"
# framed store screenshot folder (boxes-ios/fastlane/screenshots) per site folder
SHOT_FOLDERS = {"pl": "pl", "en": "en-US", "de": "de-DE", "it": "it", "es": "es-ES", "fr": "fr-FR", "zh": "zh-Hans", "ja": "ja"}
# the store posters the page shows, cropped to 4:5 (headline and the top of the phone): hero pair, then a row of three
HERO_SHOTS = ("iphone-01-home", "iphone-04-voice")
ROW_SHOTS = ("iphone-02-new", "iphone-03-box", "iphone-05-label")
SHOT_W, SHOT_H = 640, 800
GROUP_COLORS = ["#4F6BD6", "#1F9D6E"]
ICONS = [  # one per feature, in the order of the `items` of each language
    '<path d="M12 3l9 5-9 5-9-5 9-5z"/><path d="M3 8v8l9 5 9-5V8M12 13v8"/>',
    '<rect x="9" y="3" width="6" height="11" rx="3"/><path d="M5 11a7 7 0 0014 0M12 18v3"/>',
    '<path d="M4 8h3l2-3h6l2 3h3v11H4z"/><circle cx="12" cy="13" r="3.5"/>',
    '<path d="M2 7h12v9H2zM14 10h4l3 3v3h-7"/><circle cx="6" cy="17.5" r="1.8"/><circle cx="17" cy="17.5" r="1.8"/>',
    '<rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><path d="M14 14h3v3M21 14v1M14 21h1M18 21h3v-4"/>',
    '<path d="M4 8V5a1 1 0 011-1h3M16 4h3a1 1 0 011 1v3M20 16v3a1 1 0 01-1 1h-3M8 20H5a1 1 0 01-1-1v-3M3 12h18"/>',
    '<circle cx="11" cy="11" r="7"/><path d="M16.5 16.5L21 21"/>',
    '<path d="M7 18a4.5 4.5 0 01-.6-8.96A6 6 0 0118 8.5 4 4 0 0117 18H7z"/>',
]

STYLE = """\
@font-face{font-family:"Plus Jakarta Sans";font-weight:400;font-display:swap;src:url(fonts/PlusJakartaSans-Regular.ttf) format("truetype")}
@font-face{font-family:"Plus Jakarta Sans";font-weight:700;font-display:swap;src:url(fonts/PlusJakartaSans-Bold.ttf) format("truetype")}
@font-face{font-family:"Plus Jakarta Sans";font-weight:800;font-display:swap;src:url(fonts/PlusJakartaSans-ExtraBold.ttf) format("truetype")}
:root{color-scheme:light dark;--bg:#F4F5F8;--card:#FFFFFF;--ink:#151823;--soft:#646A7E;--accent:#2B3347;--border:#E1E4EC;--on:#FFFFFF;--tint:#E8EBF3}
@media (prefers-color-scheme:dark){:root{--bg:#0F1219;--card:#181C27;--ink:#F3F4F8;--soft:#9AA1B5;--accent:#B9C3E4;--border:#272C3B;--on:#0F1219;--tint:#1F2535}}
*{box-sizing:border-box}
html{-webkit-text-size-adjust:100%}
body{margin:0;background:var(--bg);color:var(--ink);font-family:"Plus Jakarta Sans",-apple-system,BlinkMacSystemFont,"Segoe UI","Hiragino Sans","PingFang SC","Noto Sans CJK SC","Helvetica Neue",Arial,sans-serif;font-size:17px;line-height:1.6}
.wrap{max-width:820px;margin:0 auto;padding:24px 20px 56px}
nav{display:flex;gap:6px 20px;flex-wrap:wrap;align-items:center;margin-bottom:40px;font-weight:700;font-size:16px}
nav a{color:var(--ink);text-decoration:none}nav a:hover,nav a[aria-current]{color:var(--accent)}
nav .brand{margin-right:auto;font-size:21px;font-weight:800;display:flex;align-items:center;gap:10px}
nav .brand img{width:34px;height:34px;border-radius:9px}
.langs{position:relative}
.langs summary{cursor:pointer;list-style:none;color:var(--soft);font-weight:700;font-size:15px;padding:4px 0}
.langs summary::-webkit-details-marker{display:none}
.langs summary::after{content:" ▾"}
.langs ul{position:absolute;right:0;top:100%;z-index:5;margin:6px 0 0;padding:6px;list-style:none;background:var(--card);border:1px solid var(--border);border-radius:14px;min-width:170px;box-shadow:0 10px 30px rgba(20,24,40,.14)}
@media (max-width:560px){.langs{width:100%}.langs ul{position:static;box-shadow:none}}
.langs li a{display:block;padding:7px 12px;border-radius:9px;font-weight:600}
.langs li a:hover,.langs li a[aria-current]{background:var(--tint);color:var(--accent)}
h1{font-size:clamp(30px,6.6vw,46px);line-height:1.12;margin:0 0 14px;font-weight:800;letter-spacing:-.015em;text-wrap:balance}
.hero h1{color:var(--accent)}
h2{font-size:20px;font-weight:800;margin:34px 0 8px}
p,li{color:var(--ink)}p{margin:0 0 14px}ul{padding-left:22px;margin:0 0 14px}li{margin-bottom:6px}
.lead{font-size:19px;color:var(--soft);margin:0 0 26px;max-width:640px}
.updated{font-size:13px;font-weight:700;color:var(--soft);margin:0 0 26px}
.callout,.card,details.q{background:var(--card);border:1px solid var(--border);border-radius:18px}
.callout{padding:18px 20px;margin:0 0 24px}.callout strong{color:var(--accent)}
a{color:var(--accent)}
.btns{display:flex;gap:12px;flex-wrap:wrap;margin:0 0 30px}
.btn{display:inline-block;padding:13px 26px;border-radius:999px;background:var(--accent);color:var(--on);font-weight:700;text-decoration:none}
.btn.ghost{background:var(--card);color:var(--ink);border:1px solid var(--border)}
.shots{display:flex;gap:14px;overflow-x:auto;padding:4px 0 16px;margin:0 -20px 26px;padding-inline:20px;scroll-snap-type:x mandatory}
.shots img{height:440px;width:auto;border-radius:22px;scroll-snap-align:start;flex:none}
.grid{display:grid;gap:14px;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));margin:0 0 28px}
.card{padding:18px 20px}.card h3{margin:0 0 6px;font-size:17px;font-weight:800;color:var(--accent)}.card p{margin:0;color:var(--soft);font-size:15px}
.note{font-size:14px;color:var(--soft)}
.faq h3{font-size:16px;font-weight:800;margin:22px 0 6px}.faq p{margin:0 0 10px}
footer{margin-top:46px;color:var(--soft);font-size:13px;display:flex;gap:6px 18px;flex-wrap:wrap}footer a{color:var(--soft)}
.pick{display:grid;gap:12px;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));margin:24px 0}
.pick a{display:block;padding:16px 18px;border-radius:16px;background:var(--card);border:1px solid var(--border);color:var(--ink);text-decoration:none;font-weight:700}
.pick a:hover{border-color:var(--accent);color:var(--accent)}.pick small{display:block;color:var(--soft);font-weight:600;font-size:13px}
.home .wrap{max-width:1080px}
.home{--shadow:0 24px 50px -22px rgba(20,24,40,.38)}
.hero{display:grid;grid-template-columns:1fr 1fr;gap:48px;align-items:center;padding:8px 0 64px}
.hero>*{min-width:0}
.hero h1{font-size:clamp(32px,4.4vw,50px);line-height:1.08;letter-spacing:-.02em;margin:0 0 18px;color:var(--ink)}
.tag{display:inline-block;margin:0 0 18px;padding:6px 12px;border-radius:999px;background:var(--tint);color:var(--accent);font-weight:700;font-size:13px}
.hero .lead{font-size:19px;max-width:30em;margin:0 0 28px}
.hero .btns{margin-bottom:22px}
.hero .btn{padding:14px 26px}
.facts{display:flex;gap:6px 18px;flex-wrap:wrap;color:var(--soft);font-size:14px;font-weight:600;margin:0;padding:0;list-style:none}
.facts li{margin:0}.facts li::before{content:"✓ ";color:var(--accent);font-weight:800}
.posters{position:relative;aspect-ratio:1/1;max-width:100%}
.posters img{position:absolute;width:62%;height:auto;border-radius:26px;box-shadow:var(--shadow)}
.posters .p1{left:0;top:10%;transform:rotate(-3deg);z-index:2}
.posters .p2{right:0;top:0;transform:rotate(4deg)}
.sec-title{font-size:clamp(26px,3.6vw,38px);line-height:1.15;font-weight:800;letter-spacing:-.015em;margin:0 0 30px;text-wrap:balance}
.band{padding-top:72px}
.grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:18px;margin:0}
.grp{background:var(--card);border:1px solid var(--border);border-radius:24px;padding:26px 26px 12px}
.grp h3{margin:0 0 18px;font-size:13px;letter-spacing:.1em;text-transform:uppercase;color:var(--c);font-weight:800}
.grp ul{list-style:none;margin:0;padding:0}
.grp li{display:flex;gap:14px;padding:13px 0;margin:0;border-top:1px solid var(--border)}
.grp li:first-child{border-top:0;padding-top:0}
.ico{flex:none;width:40px;height:40px;border-radius:12px;display:grid;place-items:center;background:var(--tint);background:color-mix(in srgb,var(--c) 14%,transparent)}
.ico svg{width:21px;height:21px;fill:none;stroke:var(--c);stroke-width:1.9;stroke-linecap:round;stroke-linejoin:round}
.grp b{display:block;font-size:16px;line-height:1.3}
.grp p{margin:2px 0 0;color:var(--soft);font-size:14.5px;line-height:1.45}
.trio{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:18px}
.trio img{width:100%;height:auto;border-radius:24px;box-shadow:var(--shadow);display:block}
.langs-sec p{color:var(--soft);margin:-14px 0 24px;max-width:36em}
.pills{display:flex;flex-wrap:wrap;gap:8px;margin:0;padding:0;list-style:none}
.pills li{margin:0}
.pills a{display:block;padding:8px 16px;border-radius:999px;background:var(--card);border:1px solid var(--border);color:var(--ink);text-decoration:none;font-weight:700;font-size:14.5px}
.pills a:hover,.pills a[aria-current]{border-color:var(--accent);color:var(--accent);background:var(--tint)}
.cta{margin:72px 0 28px;border-radius:30px;padding:clamp(32px,6vw,56px);background:linear-gradient(135deg,#232A3D,#3C4766);color:#fff;display:flex;gap:24px;align-items:center;justify-content:space-between;flex-wrap:wrap}
.cta h2{margin:0 0 4px;color:#fff;font-size:clamp(24px,3.4vw,34px);line-height:1.15;font-weight:800;letter-spacing:-.015em}
.cta p{margin:0;color:rgba(255,255,255,.86)}
.cta .btn{background:#fff;color:#232A3D}
@media (max-width:820px){
  .hero{grid-template-columns:1fr;gap:28px}.posters{max-width:420px;margin:0 auto;width:100%}
  .grid{grid-template-columns:1fr}.trio{grid-template-columns:1fr;max-width:420px;margin-inline:auto}
}
"""

ROOT_SCRIPT = """\
<script>
(function(){
  var map={pl:'pl',en:'en',de:'de',it:'it',es:'es',fr:'fr',zh:'zh',ja:'ja'};
  var list=navigator.languages||[navigator.language||'en'];
  var folder='en';
  for(var i=0;i<list.length;i++){var c=String(list[i]).toLowerCase().split('-')[0];if(map[c]){folder=map[c];break;}}
  location.replace(folder+'/%s');
})();
</script>"""


def esc(text: str) -> str:
    return html.escape(text, quote=False)


def fill(text: str, lang: dict, page: str = "") -> str:
    return text.replace("{mail}", MAIL).replace("{privacy}", "privacy.html").replace("{support}", "support.html").replace("{terms}", "terms.html")


def head(lang: dict, page: str, title: str, description: str, depth: str = "../", body: str = "") -> str:
    alternates = "\n".join(
        f'<link rel="alternate" hreflang="{l["code"]}" href="../{l["folder"]}/{page}">' for l in LANGS)
    return f"""<!doctype html>
<html lang="{lang['html_lang']}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="theme-color" content="#2B3347">
<title>{esc(title)}</title>
<meta name="description" content="{html.escape(description)}">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(description)}">
<meta property="og:image" content="https://haker.dev/boxes-public/assets/icon.png">
<link rel="icon" href="{depth}assets/icon.png">
<link rel="stylesheet" href="{depth}assets/style.css">
{alternates}
<link rel="alternate" hreflang="x-default" href="../en/{page}">
</head>
<body{f' class="{body}"' if body else ''}>
<div class="wrap">
"""


def nav(lang: dict, page: str) -> str:
    items = "".join(
        f'<li><a href="../{l["folder"]}/{page}" hreflang="{l["code"]}" lang="{l["html_lang"]}"'
        f'{" aria-current=page" if l is lang else ""}>{esc(l["label"])}</a></li>' for l in LANGS)
    cur = lambda p: ' aria-current="page"' if page == p else ""
    return (f'<nav><a class="brand" href="index.html"><img src="../assets/icon.png" alt="">{esc(lang["app_name"])}</a>'
            f'<a href="privacy.html"{cur("privacy.html")}>{esc(lang["nav_privacy"])}</a>'
            f'<a href="terms.html"{cur("terms.html")}>{esc(lang["nav_terms"])}</a>'
            f'<a href="support.html"{cur("support.html")}>{esc(lang["nav_support"])}</a>'
            f'<details class="langs"><summary>{esc(lang["label"])}</summary><ul>{items}</ul></details></nav>\n')


def footer(lang: dict) -> str:
    return (f'<footer><span>{lang["footer_rights"]}</span>'
            f'<a href="privacy.html">{esc(lang["nav_privacy"])}</a><a href="terms.html">{esc(lang["nav_terms"])}</a>'
            f'<a href="support.html">{esc(lang["nav_support"])}</a></footer>\n'
            "</div>\n</body>\n</html>\n")


def blocks_html(lang: dict, blocks) -> str:
    out = []
    for kind, value in blocks:
        if kind == "callout":
            out.append(f'<div class="callout">{fill(value, lang)}</div>')
        elif kind == "h2":
            out.append(f"<h2>{esc(value)}</h2>")
        elif kind == "p":
            out.append(f"<p>{fill(value, lang)}</p>")
        elif kind == "ul":
            out.append("<ul>" + "".join(f"<li>{fill(v, lang)}</li>" for v in value) + "</ul>")
        elif kind == "faq":
            out.append('<div class="faq">' + "".join(
                f"<h3>{esc(q)}</h3><p>{fill(a, lang)}</p>" for q, a in value) + "</div>")
    return "\n".join(out) + "\n"


def poster(lang: dict, shot: str, alt: str, cls: str = "", lazy: bool = True) -> str:
    loading = ' loading="lazy"' if lazy else ""
    return (f'<img{f" class={chr(34)}{cls}{chr(34)}" if cls else ""} src="../assets/shots/{lang["folder"]}-{shot}.jpg"'
            f' alt="{html.escape(alt)}" width="{SHOT_W}" height="{SHOT_H}"{loading}>')


def index_page(lang: dict) -> str:
    c = lang["index"]
    name = lang["app_name"]
    chips = "".join(f"<li>{esc(t)}</li>" for t in c["chips"])
    groups = []
    per = len(c["items"]) // len(c["groups"])
    for g, title in enumerate(c["groups"]):
        items = "".join(
            f'<li><span class="ico"><svg viewBox="0 0 24 24" aria-hidden="true">{ICONS[g * per + i]}</svg></span>'
            f"<div><b>{esc(t)}</b><p>{esc(d)}</p></div></li>"
            for i, (t, d) in enumerate(c["items"][g * per:(g + 1) * per]))
        groups.append(f'<section class="grp" style="--c:{GROUP_COLORS[g]}"><h3>{esc(title)}</h3><ul>{items}</ul></section>')
    trio = "".join(poster(lang, shot, f"{name} {i + 1}") for i, shot in enumerate(ROW_SHOTS))
    pills = "".join(
        f'<li><a href="../{l["folder"]}/index.html" hreflang="{l["code"]}" lang="{l["html_lang"]}"'
        f'{" aria-current=page" if l is lang else ""}>{esc(l["label"])}</a></li>' for l in LANGS)
    return (head(lang, "index.html", c["title"], c["description"], body="home") + nav(lang, "index.html") +
            f'<header class="hero"><div><span class="tag">{esc(c["tag"])}</span><h1>{esc(c["h1"])}</h1><p class="lead">{esc(c["lead"])}</p>\n'
            f'<div class="btns"><a class="btn" href="{APP_STORE}">{esc(c["download"])}</a>'
            f'<a class="btn ghost" href="#features">{esc(c["see"])}</a></div>'
            f'<ul class="facts">{chips}</ul></div>'
            f'<div class="posters">{poster(lang, HERO_SHOTS[0], name, "p1", lazy=False)}{poster(lang, HERO_SHOTS[1], name, "p2", lazy=False)}</div></header>\n'
            f'<section id="features" class="band" style="padding-top:8px"><h2 class="sec-title">{esc(c["features_title"])}</h2><div class="grid">' + "".join(groups) + "</div></section>\n"
            f'<section class="band"><h2 class="sec-title">{esc(c["screens_title"])}</h2><div class="trio">{trio}</div></section>\n'
            f'<section class="band langs-sec"><h2 class="sec-title">{esc(c["langs_title"])}</h2><p>{esc(c["langs_text"])}</p><ul class="pills">{pills}</ul></section>\n'
            f'<div class="cta"><div><h2>{esc(c["cta_title"])}</h2><p>{esc(c["cta_text"])}</p></div>'
            f'<a class="btn" href="{APP_STORE}">{esc(c["download"])}</a></div>\n'
            f'<p class="note">{esc(c["note"])}</p>\n' + footer(lang))


def text_page(lang: dict, kind: str) -> str:
    c = lang[kind]
    page = f"{kind}.html"
    return (head(lang, page, f'{c["title"]} · {lang["app_name"]}', c["description"]) + nav(lang, page) +
            f'<h1>{esc(c["h1"])}</h1><p class="updated">{esc(c["updated"])}</p>\n' +
            blocks_html(lang, c["blocks"]) + footer(lang))


def picker(page: str, titles: dict) -> str:
    """A root page: sends the browser to its language, and lists all of them for anyone else."""
    links = "".join(
        f'<a href="{l["folder"]}/{page}" hreflang="{l["code"]}" lang="{l["html_lang"]}">{esc(l["label"])}'
        f'<small>{esc(titles[l["code"]])}</small></a>' for l in LANGS)
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Boxes · Kartony</title>
<meta name="description" content="Boxes (Kartony): an inventory of your boxes with QR labels, for iPhone, iPad and Mac. Choose your language.">
<link rel="icon" href="assets/icon.png">
<link rel="stylesheet" href="assets/style.css">
{ROOT_SCRIPT % page}
</head>
<body>
<div class="wrap">
<nav><a class="brand" href="index.html"><img src="assets/icon.png" alt="">Boxes</a></nav>
<h1>Boxes</h1>
<p class="lead">{" · ".join(l["label"] for l in LANGS)}</p>
<div class="pick">{links}</div>
</div>
</body>
</html>
"""


def build_shots(shots_dir: Path) -> None:
    from PIL import Image
    out = ROOT / "assets" / "shots"
    out.mkdir(parents=True, exist_ok=True)
    for old in out.glob("*.jpg"):
        old.unlink()
    for folder, source in SHOT_FOLDERS.items():
        for shot in HERO_SHOTS + ROW_SHOTS:
            path = shots_dir / source / f"{shot}.png"
            if not path.exists():
                print("missing", path)
                continue
            im = Image.open(path).convert("RGB")
            im = im.crop((0, 0, im.width, round(im.width * SHOT_H / SHOT_W)))
            im.resize((SHOT_W, SHOT_H), Image.LANCZOS).save(
                out / f"{folder}-{shot}.jpg", "JPEG", quality=84, optimize=True, progressive=True)


def main() -> None:
    assets = ROOT / "assets"
    (assets / "fonts").mkdir(parents=True, exist_ok=True)
    (assets / "style.css").write_text(STYLE, encoding="utf-8")
    if "--shots" in sys.argv:
        build_shots(Path(sys.argv[sys.argv.index("--shots") + 1]).resolve())
    for lang in LANGS:
        folder = ROOT / lang["folder"]
        folder.mkdir(exist_ok=True)
        (folder / "index.html").write_text(index_page(lang), encoding="utf-8")
        for kind in PAGES:
            (folder / f"{kind}.html").write_text(text_page(lang, kind), encoding="utf-8")
    (ROOT / "index.html").write_text(picker("index.html", {l["code"]: l["nav_home"] for l in LANGS}), encoding="utf-8")
    for kind in PAGES:
        (ROOT / f"{kind}.html").write_text(
            picker(f"{kind}.html", {l["code"]: l["nav_" + ("support" if kind == "support" else kind)] for l in LANGS}),
            encoding="utf-8")
    print("built", len(LANGS), "languages")


if __name__ == "__main__":
    main()
