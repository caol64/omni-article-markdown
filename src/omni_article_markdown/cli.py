import click

from .omni_article_md import OmniArticleMarkdown

@click.command()
@click.argument("url_or_path")
@click.option(
    "-s", "--save",
    default=None,
    help="Save result (default: ./). Provide a path to save elsewhere.",
    is_flag=False,
    flag_value="./"
)
def cli(url_or_path, save):
    """
    The URL or path to the article.
    """
    handler = OmniArticleMarkdown(url_or_path)
    article = handler.parse()

    if save is None:
        print(article)
    else:
        handler.save(save)

if __name__ == "__main__":
    cli()
