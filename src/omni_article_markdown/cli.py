import click
from click_default_group import DefaultGroup

from .omni_article_md import OmniArticleMarkdown


def stderr_reporter(message: str):
    click.echo(click.style(message, fg="yellow"), err=True)


@click.group(cls=DefaultGroup, default="parse", default_if_no_args=True)
def cli():
    """
    A CLI tool to parse articles and save them as Markdown.
    """
    ...


@cli.command(name="parse")
@click.argument("url_or_path")
@click.option(
    "-s",
    "--save",
    help="Save result. Use -s alone to save to './', or -s /path to save elsewhere.",
    type=click.Path(dir_okay=True, writable=True),
    is_flag=False,
    flag_value="./",
    default=None,
)
def parse_article(url_or_path: str, save: str | None):
    """
    Parses an article from a URL or local path and outputs/saves it as Markdown.
    """
    try:
        handler = OmniArticleMarkdown(url_or_path, reporter=stderr_reporter)
        parser_ctx = handler.parse()
    except Exception as e:
        click.echo(click.style(f"Error: {str(e)}", fg="red"), err=True)
        return

    if save is None:
        click.echo(parser_ctx.markdown)
    else:
        save_path = handler.save(parser_ctx, save)
        click.echo(f"Article saved to: {save_path}")


if __name__ == "__main__":
    cli()
