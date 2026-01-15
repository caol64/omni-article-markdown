# omni-article-markdown (omnimd)

**Convert web articles (blogs, news, docs) to clean Markdown — powered by Docker.**

> This image bundles **omni-article-markdown** (`mdcli`) and all official plugins.
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

## Persist Cookies / Sessions (Recommended)

Some sites (Zhihu, Toutiao, etc.) require cookies or login state.

Mount a local directory to persist data:

```bash
docker run --rm \
  -v ~/.ommimd:/root/.ommimd \
  caol64/omnimd \
  https://zhuanlan.zhihu.com/p/1915735485801828475
```

**What this does:**

| Location        | Purpose                       |
| --------------- | ----------------------------- |
| `/root/.ommimd` | Stores cookies, browser state |
| `~/.ommimd`     | Persistent storage on host    |

## Plugin Support

All official plugins are **pre-installed** in this image.

Supported sites include:

-   Medium
-   Zhihu (requires cookie)
-   WeChat Official Accounts
-   Toutiao
-   Freedium
-   Apple Developer Docs
-   Cloudflare Blog
-   InfoQ, CSDN, Juejin, Yuque, etc.

No extra setup required.

## Image Details

-   Base image: `python:3.x-alpine`
-   Entrypoint: `mdcli`
-   Plugins: all official plugins included
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
alias mdcli='docker run --rm -v ~/.ommimd:/root/.ommimd caol64/omnimd'
```

Then use it like a native CLI:

```bash
mdcli https://example.com
```
