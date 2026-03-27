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

- 先阅读`README`了解项目功能
- 阅读`src/omni_article_markdown/extractors`目录下已有的功能，找到开发规律
- 对于新接入的网站，在`src/omni_article_markdown/extractors`下新建一个独立文件并继承`Extractor`类，引擎会自动加载
- 使用工具抓取网站`html`，由于内容一般较大，建议保存成临时文件，提供如下工具抓取网页：
  - 普通抓取，使用`requests`库进行简单抓取
    - `uv run python scripts/fetch_url.py <url>`
    - `uv run python scripts/fetch_url.py <url> --curl`，伪装成`curl`
  - 使用无头浏览器进行抓取，适用于需要`javascript`的网站
    - `uv run python scripts/fetch_url_playwright.py <url>`，适用于大多数静态或加载较快的动态网页
    - `uv run python scripts/fetch_url_playwright.py <url> -m scroll`，适用于需要时间加载且必须滚动到底部才能加载完整内容的 SPA（单页应用）
- 如果使用工具无法抓取到正文，可能是`js`后台异步请求了一些接口，你可以用以下工具嗅探一下`js`的后台请求：
  - `uv run python scripts/log_js_request.py <url>`
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
- 最后：
  - 使用该命令进行验证`uv run mdcli <url>`
  - 如果必须使用`playwright`，说明一下原因以及记录到开发日志中

## 开发日志

`AGENT_NOTES.md`是你的开发日志，是你对本次开发过程的总结。

- 重要：不要事无巨细的把工作内容全部记录下来。开发某个网站的`extractor`是**一次性工作**，只把你认为其它网站也可能遇到的**通用型问题**记录下来
  - 例如：某个`extractor`的某个函数实现很有通用性，很多网站可以参考这个实现，你可以单独记录到开发日志中
- 把踩过坑的地方记录下来，避免再次踩坑

开发日志这样编写：

```
## {当前时间}

- 内容1
- 内容2
...
```

在每次开始工作前将`AGENT_NOTES.md`的内容加载到你的系统指令中。
