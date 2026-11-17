import inspect
import sys
from importlib import metadata

import click
from click_default_group import DefaultGroup

from .omni_article_md import OmniArticleMarkdown
from .reader import ReaderFactory
from .truncate import truncate_markdown

help_msg = inspect.cleandoc("""
Parse web articles into clean Markdown.

Examples:

\b
Parse an article and print Markdown:
  mdcli <url>
Parse and save to a specific directory:
  mdcli <url> -s /path/to/save


Notes:

--no-verify-ssl disables certificate validation.
""")


def get_version():
    try:
        return metadata.version("omni-article-markdown")
    except metadata.PackageNotFoundError:
        return "0.0.0-dev"


def stderr_reporter(message: str):
    click.echo(click.style(message, fg="yellow"), err=True)


def stderr(message: str):
    click.echo(click.style(message, fg="red"), err=True)


def _optional_value_option(*decls, **attrs):
    """
    构造“可裸用”的取值选项装饰器：不带值时使用 flag_value，带值时使用值。

    click<=8.2 会从 flag_value 自动推导内部标志 _flag_needs_value；
    click>=8.3 改为仅当 default 未显式给出时才推导，导致 is_flag=False +
    flag_value + default=None 的组合在裸用时报 "requires an argument"。
    这里显式置位以保持跨版本一致的行为。
    """

    def decorator(f):
        opt = click.Option(decls, is_flag=False, default=None, **attrs)
        opt._flag_needs_value = True
        f.__click_params__ = getattr(f, "__click_params__", [])
        f.__click_params__.append(opt)
        return f

    return decorator


@click.group(
    cls=DefaultGroup,
    default="parse",
    default_if_no_args=False,
    no_args_is_help=True,
    context_settings={"help_option_names": ["-h", "--help"]},
    help=help_msg,
)
@click.version_option(version=get_version())
def cli(): ...


@cli.command(name="parse")
@click.argument("url_or_path")
@click.option(
    "--no-verify-ssl", is_flag=True, default=False, help="Disable SSL certificate verification (not recommended)."
)
@_optional_value_option(
    "-s",
    "--save",
    help="Save result. Use -s alone to save to './', or -s /path to save elsewhere.",
    type=click.Path(dir_okay=True, writable=True),
    flag_value="./",
)
@_optional_value_option(
    "--truncate",
    "truncate_tokens",
    type=int,
    help="Truncate output Markdown to N tokens (heuristic estimate: ~4 bytes/token for "
    "Latin text, ~2.2 for CJK). Use --truncate alone for the default of 800.",
    flag_value=800,
)
def parse_article(url_or_path: str, save: str | None, no_verify_ssl: bool, truncate_tokens: int | None):
    """
    Parses an article from a URL or local path and outputs/saves it as Markdown.
    """
    verify_ssl = not no_verify_ssl
    try:
        handler = OmniArticleMarkdown(url_or_path, reporter=stderr_reporter, verify_ssl=verify_ssl)
        handler.parse()
        markdown = handler.result()
        if truncate_tokens is not None:
            markdown = truncate_markdown(markdown, truncate_tokens)
        if save is None:
            click.echo(markdown)
        else:
            save_path = handler.save(save, markdown=markdown)
            stderr_reporter(f"Article saved to: {save_path}")
    except Exception as e:
        stderr(f"Error: {str(e)}")
        sys.exit(1)


@cli.command(name="read")
@click.argument("url_or_path")
@click.option(
    "--no-verify-ssl", is_flag=True, default=False, help="Disable SSL certificate verification (not recommended)."
)
@click.option("-p", "--prettify", is_flag=True, default=False, help="Prettify the HTML output.")
def read(url_or_path: str, no_verify_ssl: bool, prettify: bool):
    """
    Reads and formats an article from a URL or local path.
    """
    verify_ssl = not no_verify_ssl
    try:
        reader = ReaderFactory.create(url_or_path, reporter=stderr_reporter, verify_ssl=verify_ssl)
        raw_html = reader.read()
        if prettify:
            from bs4 import BeautifulSoup

            soup = BeautifulSoup(raw_html, "html5lib")
            click.echo(soup.prettify())
        else:
            click.echo(raw_html)
    except Exception as e:
        stderr(f"Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    cli()
