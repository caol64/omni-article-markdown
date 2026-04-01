import sys

import click
from click_default_group import DefaultGroup

from .omni_article_md import OmniArticleMarkdown
from .reader import ReaderFactory


def stderr_reporter(message: str):
    click.echo(click.style(message, fg="yellow"), err=True)


def stderr(message: str):
    click.echo(click.style(message, fg="red"), err=True)


@click.group(cls=DefaultGroup, default="parse", default_if_no_args=True)
def cli():
    """
    A CLI tool to parse web articles and export clean Markdown.
    """
    ...


@cli.command(name="parse")
@click.argument("url_or_path")
@click.option(
    "--no-verify-ssl", is_flag=True, default=False, help="Disable SSL certificate verification (not recommended)."
)
@click.option(
    "-s",
    "--save",
    help="Save result. Use -s alone to save to './', or -s /path to save elsewhere.",
    type=click.Path(dir_okay=True, writable=True),
    is_flag=False,
    flag_value="./",
    default=None,
)
def parse_article(url_or_path: str, save: str | None, no_verify_ssl: bool):
    """
    Parses an article from a URL or local path and outputs/saves it as Markdown.
    """
    verify_ssl = not no_verify_ssl
    try:
        handler = OmniArticleMarkdown(url_or_path, reporter=stderr_reporter, verify_ssl=verify_ssl)
        handler.parse()
        if save is None:
            click.echo(handler.result())
        else:
            save_path = handler.save(save)
            stderr_reporter(f"Article saved to: {save_path}")
    except Exception as e:
        stderr(f"Error: {str(e)}")
        sys.exit(1)


@cli.command(name="read")
@click.argument("url_or_path")
@click.option(
    "--no-verify-ssl", is_flag=True, default=False, help="Disable SSL certificate verification (not recommended)."
)
def read(url_or_path: str, no_verify_ssl: bool):
    """
    Reads an article from a URL or local path.
    """
    verify_ssl = not no_verify_ssl
    try:
        reader = ReaderFactory.create(url_or_path, reporter=stderr_reporter, verify_ssl=verify_ssl)
        raw_html = reader.read()
        click.echo(raw_html)
    except Exception as e:
        stderr(f"Error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    cli()
