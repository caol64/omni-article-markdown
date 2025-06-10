import click
import sys
from runpy import run_module
from click_default_group import DefaultGroup

from .omni_article_md import OmniArticleMarkdown
from . import DEFAULT_PLUGINS

@click.group(cls=DefaultGroup, default='parse', default_if_no_args=True)
def cli():
    """
    A CLI tool to parse articles and save them as Markdown.
    It also supports installing plugins.
    """
    pass

@cli.command(name="parse")
@click.argument("url_or_path")
@click.option(
    "-s", "--save",
    default=None,
    help="Save result (default: ./). Provide a path to save elsewhere.",
    is_flag=False,
    flag_value="./"
)
def parse_article(url_or_path, save):
    """
    Parses an article from a URL or local path and outputs/saves it as Markdown.
    """
    handler = OmniArticleMarkdown(url_or_path)
    article = handler.parse()

    if save is None:
        click.echo(article)
    else:
        handler.save(save)
        click.echo(f"Article saved to: {handler.save_path}")

@cli.command()
@click.argument("plugin_name")
@click.option(
    "-U", "--upgrade", is_flag=True, help="Upgrade the plugin if already installed."
)
@click.option(
    "-e", "--editable", is_flag=True, help="Install the editable package based on the provided local file path"
)
def install(plugin_name, upgrade, editable):
    """
    Installs a plugin for this application.
    For example, to install the 'zhihu' plugin: mdcli install zhihu
    """
    actual_package_name = plugin_name if editable or plugin_name not in DEFAULT_PLUGINS else DEFAULT_PLUGINS[plugin_name]

    click.echo(f"Attempting to install plugin: {actual_package_name}...")
    args = ["pip", "install"]
    if upgrade:
        args.append("--upgrade")
    args.append(actual_package_name)

    original_argv = sys.argv
    try:
        sys.argv = args
        run_module("pip", run_name="__main__")
        click.echo(f"Plugin '{actual_package_name}' processed by pip.")
        click.echo("If the plugin provides new functionality, it should now be available.")
        click.echo("You might need to restart the application for changes to take full effect if it involves runtime loading during startup.")
    except Exception as e:
        click.echo(f"Failed to process plugin '{actual_package_name}' with pip: {e}", err=True)
        click.echo("Please ensure pip is installed and the package name is correct.", err=True)
    finally:
        sys.argv = original_argv

@cli.command()
@click.argument("plugin_name")
@click.option(
    "-y", "--yes", is_flag=True, help="Don't ask for confirmation before uninstalling."
)
def uninstall(plugin_name, yes):
    """
    Uninstalls a plugin for this application.
    For example, to uninstall the 'zhihu' plugin: mdcli uninstall zhihu
    """
    actual_package_name = plugin_name if plugin_name not in DEFAULT_PLUGINS else DEFAULT_PLUGINS[plugin_name]

    click.echo(f"Attempting to uninstall plugin: {actual_package_name}...")
    args = ["pip", "uninstall"]
    if yes:
        args.append("-y")
    args.append(actual_package_name)

    original_argv = sys.argv
    try:
        sys.argv = args
        run_module("pip", run_name="__main__")
        click.echo(f"Plugin '{actual_package_name}' uninstallation processed by pip.")
        click.echo("The plugin's functionality should no longer be available after the next application start (or if dynamically unloaded).")
    except Exception as e:
        click.echo(f"Failed to process uninstallation of plugin '{actual_package_name}' with pip: {e}", err=True)
        click.echo("Please ensure pip is installed and the package name is correct.", err=True)
    finally:
        sys.argv = original_argv


if __name__ == "__main__":
    cli()
