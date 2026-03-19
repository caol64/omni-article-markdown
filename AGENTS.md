# AGENTS.md

## First Message

If the user did not give you a concrete task in their first message, read `task.md` to get the core objectives outlined in the file.

## Project Context
This project uses the `uv` package manager and `pyproject.toml` for dependency management and configuration. The target Python version is 3.13. All commands must be run within the `uv` managed environment.

## Agent Instructions
When working on this project, the agent **MUST** adhere to the following rules:

- **ALWAYS** use `uv run <command>` instead of invoking `python`, `pytest`, or other tools directly.
- **NEVER** use `pip` or `pip3` for installing or managing packages.
- **ALWAYS** run `uv sync` to install/update dependencies after changes to `pyproject.toml`.
- **ALWAYS** run quality checks (`format`, `lint`, `typecheck`, `test`) before proposing any changes.
- **MAINTAIN** existing code formatting and style, primarily enforced by `ruff` and `mypy`.

## Useful Commands (for the AI Agent)

- **Install dependencies**: `uv sync`
- **Run a script**: `uv run python script.py`
- **Run tests**: `uv run pytest`
- **Run linting**: `uv run ruff check .`
- **Format code**: `uv run ruff format .`
- **Run type checking**: `uv run mypy`
- **Add a new package**: `uv add <package-name>`
- **Remove a package**: `uv remove <package-name>`
- **Create a virtual environment** (if needed): `uv venv`

## Project Structure
- `src/`: Contains all application-level code.
- `tests/`: Contains all unit and integration tests (using `pytest`).
- `pyproject.toml`: The main configuration and dependency file.
- `AGENTS.md`: This file, providing context and instructions.
- `plugins/`: Contains all plugin project.

## 开发流程

- 先阅读`README`了解项目功能，项目使用`requests`库对`url`进行访问，把抓取到的`html`使用`beautifulsoup4`进行转换
- 阅读`src/omni_article_markdown/extractors`目录下已有的功能，找到开发规律
- 对于新接入的网站，在`src/omni_article_markdown/extractors`下新建一个独立文件并继承`Extractor`类，引擎会自动加载
- 使用工具抓取网站`html`，由于内容一般较大，建议保存成临时文件，工具使用方法：
  - `uv run python scripts/fetch_url.py <url>`
  - `uv run python scripts/fetch_url.py <url> --curl`，如果上述命令无法抓取到正文，可以尝试用这个命令再次抓取一次
- 如果上面的工具无法抓取到正文（比如网站需要开启`javascript`，或者需要`cookie`），你可以尝试用以下工具：
  - `uv run python scripts/fetch_url_playwright.py <url>`
- 如果目标网站遇到以下情况，立刻停止并记录开发日志
  - 无论如何无法抓取到正文
  - 网站有人机交互检查
  - 网站无法访问（连接中断、404、500等）
  - 需要登录才能访问
- 对正文做最后的检查，过滤掉以下内容：
  - 广告
  - 作者介绍、用户头像等
  - 求关注、推广链接等
  - 菜单、目录、`TOC`等与正文无关内容
- 如果你确定使用`playwright`模拟浏览器浏览即可获取到正文，无需新增新的`extractor`，只需在`src/utils.py`中的`BROWSER_TARGET_HOSTS`添加网站域名即可

## 开发规范

- `src/utils.py`中有很多工具函数开箱可用
- 不要直接使用下述写法，用`filter_tag`包装一下
  ```
  # wrong:
  wiki_box = soup.find("div", class_="wikiSSRBox")
  for script in soup.find_all("script"):
    s = script.string

  # right:
  wiki_box = filter_tag(soup.find("div", class_="wikiSSRBox"))
  for script in soup.find_all("script"):
    script_tag = filter_tag(script)
  ```

## 开发日志

`AGENT_NOTES.md`是你的开发日志，你会把你开发中遇到的问题记录在案。注意，不要事无巨细的全部记录下来，把你认为重要，可以为你之后开发提升效率或者带来帮助的内容记录下来。此外，对一些明显踩过坑的方案，也要记录下来，避免再次踩坑。

开发日志这样编写：

```
## {当前时间}

- 内容1
- 内容2
...
```

在每次开始工作前将`AGENT_NOTES.md`的内容加载到你的系统指令中。
