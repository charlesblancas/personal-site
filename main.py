from pathlib import Path
from datetime import date
from html import escape
import re
import shutil

import pypandoc


ROOT = Path(__file__).parent
SOURCE = ROOT / "src"
OUTPUT = ROOT / "build"
TEMP_OUTPUT = ROOT / "build-tmp"
CONTENT = ROOT / "content" / "notes-to-self"
TEMPLATE = ROOT / "templates" / "notes-to-self.html"


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
        pypandoc.convert_file(
            str(source_path),
            "html",
            outputfile=str(TEMP_OUTPUT / "notes-to-self" / f"{slug}.html"),
            extra_args=["--standalone", f"--template={TEMPLATE}"],
        )

    existing = index_path.read_text(encoding="utf-8")
    cards_marker = "                <!-- blog-cards -->"
    if cards_marker not in existing:
        raise ValueError(f"{index_path}: missing generated-content marker")

    index_path.write_text(existing.replace(cards_marker, "".join(cards)), encoding="utf-8")

    if OUTPUT.exists():
        shutil.rmtree(OUTPUT)
    TEMP_OUTPUT.replace(OUTPUT)


if __name__ == "__main__":
    build()
