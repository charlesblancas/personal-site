from pathlib import Path
from datetime import date
from html import escape
import json
import re
import shutil

import pypandoc


ROOT = Path(__file__).parent
SOURCE = ROOT / "src"
OUTPUT = ROOT / "build"
TEMP_OUTPUT = ROOT / "build-tmp"
CONTENT = ROOT / "content" / "notes-to-self"
TEMPLATE = ROOT / "templates" / "notes-to-self.html"
SITE_URL = "https://charlesblancas.com"


def read_frontmatter(path: Path) -> dict[str, str]:
    lines = path.read_text(encoding="utf-8").splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValueError(f"{path}: frontmatter must start with ---")

    metadata: dict[str, str] = {}
    for line in lines[1:]:
        if line.strip() == "---":
            return metadata
        if ": " not in line:
            raise ValueError(f"{path}: invalid frontmatter line: {line}")
        key, value = line.split(": ", 1)
        metadata[key.strip()] = value.strip()

    raise ValueError(f"{path}: frontmatter is missing a closing ---")


def slugify(value: str) -> str:
    return re.sub(r"[^a-z0-9-]+", "-", value.lower()).strip("-")


def generate_blog_card(frontmatter: dict[str, str], filename: str) -> str:
    title = escape(frontmatter.get("title", filename))
    date = escape(frontmatter.get("date", ""))
    return (
        f'<a href="./{filename}.html" class="nav-card-link">'
        f'<article id="{filename}" class="nav-card">'
        f'<p class="card-label">{date}</p>'
        f'<h2 class="blog-title">{title} <span aria-hidden="true">↗</span></h2>'
        "</article></a>\n"
    )


def plain_text(markdown: str) -> str:
    text = re.sub(r"!\[([^]]*)\]\([^)]*\)", r"\1", markdown)
    text = re.sub(r"\[([^]]+)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"[`*_>#]", "", text)
    return " ".join(text.split())


def page_url(path: Path) -> str:
    relative = path.relative_to(TEMP_OUTPUT).as_posix()
    if relative.endswith("index.html"):
        relative = relative[: -len("index.html")]
    return f"{SITE_URL}/{relative}"


def write_crawl_files() -> None:
    pages = sorted(
        path
        for path in TEMP_OUTPUT.rglob("*.html")
        if path.relative_to(TEMP_OUTPUT).parts[0] != "components"
    )
    sitemap_urls = "\n".join(
        f"    <url><loc>{escape(page_url(path))}</loc></url>" for path in pages
    )
    (TEMP_OUTPUT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        f"{sitemap_urls}\n"
        "</urlset>\n",
        encoding="utf-8",
    )
    (TEMP_OUTPUT / "robots.txt").write_text(
        f"User-agent: *\nAllow: /\nSitemap: {SITE_URL}/sitemap.xml\n",
        encoding="utf-8",
    )


def build() -> None:
    if TEMP_OUTPUT.exists():
        shutil.rmtree(TEMP_OUTPUT)
    shutil.copytree(SOURCE, TEMP_OUTPUT)

    index_path = TEMP_OUTPUT / "notes-to-self" / "index.html"
    posts = []
    slugs = set()
    for source_path in CONTENT.rglob("*.md"):
        slug = slugify(source_path.stem)
        if not slug:
            raise ValueError(f"{source_path}: filename does not create a valid slug")
        if slug in slugs:
            raise ValueError(f"{source_path}: duplicate post slug: {slug}")
        slugs.add(slug)
        metadata = read_frontmatter(source_path)
        if not metadata.get("description"):
            first_paragraph = next(
                (
                    paragraph
                    for paragraph in source_path.read_text(encoding="utf-8").split("\n\n")
                    if paragraph.strip() and not paragraph.lstrip().startswith("---")
                ),
                "",
            )
            metadata["description"] = plain_text(first_paragraph)[:160]
        try:
            published = date.fromisoformat(metadata["date"])
        except KeyError as error:
            raise ValueError(f"{source_path}: missing date in frontmatter") from error
        except ValueError as error:
            raise ValueError(f"{source_path}: date must use YYYY-MM-DD") from error
        posts.append((published, slug, metadata, source_path))

    cards = []
    for _, slug, metadata, source_path in sorted(posts, reverse=True):
        cards.append(generate_blog_card(metadata, slug))
        canonical_url = f"{SITE_URL}/notes-to-self/{slug}.html"
        schema = {
            "@context": "https://schema.org",
            "@type": "BlogPosting",
            "headline": metadata["title"],
            "description": metadata["description"],
            "datePublished": metadata["date"],
            "author": {"@type": "Person", "name": "Charles Blancas", "url": f"{SITE_URL}/"},
            "mainEntityOfPage": canonical_url,
        }
        safe_schema = json.dumps(schema, ensure_ascii=False).replace("<", "\\u003c")
        pypandoc.convert_file(
            str(source_path),
            "html",
            outputfile=str(TEMP_OUTPUT / "notes-to-self" / f"{slug}.html"),
            extra_args=[
                "--standalone",
                f"--template={TEMPLATE}",
            ],
        )
        post_path = TEMP_OUTPUT / "notes-to-self" / f"{slug}.html"
        post_html = post_path.read_text(encoding="utf-8")
        replacements = {
            "<!-- seo-description -->": escape(metadata["description"], quote=True),
            "<!-- canonical-url -->": escape(canonical_url, quote=True),
            "<!-- social-title -->": escape(f"{metadata['title']} · Charles Blancas", quote=True),
            "<!-- published-date -->": escape(metadata["date"], quote=True),
            "<!-- article-schema -->": safe_schema,
        }
        for marker, value in replacements.items():
            post_html = post_html.replace(marker, value)
        post_path.write_text(post_html, encoding="utf-8")

    existing = index_path.read_text(encoding="utf-8")
    cards_marker = "                <!-- blog-cards -->"
    if cards_marker not in existing:
        raise ValueError(f"{index_path}: missing generated-content marker")

    index_path.write_text(existing.replace(cards_marker, "".join(cards)), encoding="utf-8")
    write_crawl_files()

    if OUTPUT.exists():
        shutil.rmtree(OUTPUT)
    TEMP_OUTPUT.replace(OUTPUT)


if __name__ == "__main__":
    build()
