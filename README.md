## Build

This is a small custom static-site generator. Pages are written in HTML and
Markdown, then `main.py` uses Pandoc to produce the deployable `build/`
directory.

Install the single build dependency and generate the site:

```sh
python -m pip install -r requirements.txt
python main.py
```

On Windows, use `py` in place of `python` if Python is not on your PATH.

Serve `build/` with any static file server.
