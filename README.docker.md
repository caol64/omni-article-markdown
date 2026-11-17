# omni-article-markdown (omnimd)

**Convert web articles (blogs, news, docs) to clean Markdown — powered by Docker.**

> This image bundles **omni-article-markdown** (`mdcli`) with its Chromium headless shell.
> No local Python environment required.

## Quick Start

### Pull image

```bash
docker pull caol64/omnimd
```

### Show help

```bash
docker run --rm caol64/omnimd --help
```

## Basic Usage

Convert a web page to Markdown and print to stdout:

```bash
docker run --rm caol64/omnimd https://example.com/article
```

Save result to current directory:

```bash
docker run --rm \
  -v $(pwd):/output \
  caol64/omnimd \
  https://example.com/article -s /output
```

## Truncate Output for AI Agents

Long articles can blow up an LLM context. `--truncate` limits the output to N tokens
(a heuristic estimate; plain `--truncate` defaults to 800). Truncation happens at
paragraph boundaries and appends a `…[truncated]` marker:

```bash
docker run --rm caol64/omnimd https://example.com/article --truncate
docker run --rm caol64/omnimd https://example.com/article --truncate 1500
```

## Persist Cookies / Sessions (Optional)

Some sites (Zhihu, etc.) rely on cached cookies. The readers obtain them automatically
via the bundled browser when no cache exists, so mounting a volume is only needed to
**reuse** sessions across container runs:

```bash
docker run --rm \
  -v ~/.config/ommimd:/root/.config/ommimd \
  caol64/omnimd \
  https://zhuanlan.zhihu.com/p/1915735485801828475
```

**What this does:**

| Location                  | Purpose                                        |
| ------------------------- | ---------------------------------------------- |
| `/root/.config/ommimd`    | Stores cookies / session data inside container |
| `~/.config/ommimd`        | Persistent storage on host                     |

## Built-in Site Adapters

All site-specific readers and extractors ship inside the package — there is nothing to
install separately. Dynamic-rendering sites (Zhihu, Toutiao, Huxiu, InfoQ CN, OSCHINA
blogs, Medium, …) are handled automatically with the bundled headless Chromium.

For the full list of tested sites, see [docs/sites.md](docs/sites.md).

## Image Details

-   Base image: `python:3.13-bookworm` (Debian)
-   Browser: Playwright `chromium-headless-shell` (installed at build time)
-   Entrypoint: `mdcli`
-   Architecture: `linux/amd64`, `linux/arm64`

## Example: Pipe to File

```bash
docker run --rm caol64/omnimd https://example.com/article > article.md
```

## Project Links

-   GitHub: [https://github.com/caol64/omni-article-markdown](https://github.com/caol64/omni-article-markdown)
-   PyPI: [https://pypi.org/project/omni-article-markdown/](https://pypi.org/project/omni-article-markdown/)
-   Issues: [https://github.com/caol64/omni-article-markdown/issues](https://github.com/caol64/omni-article-markdown/issues)

## License

MIT License

### Tip

For frequent usage, consider creating an alias:

```bash
alias mdcli='docker run --rm -v ~/.config/ommimd:/root/.config/ommimd caol64/omnimd'
```

Then use it like a native CLI:

```bash
mdcli https://example.com
```
