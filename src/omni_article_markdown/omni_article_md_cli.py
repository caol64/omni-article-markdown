import argparse

from .omni_article_md import OmniArticleMarkdown

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("url_or_path", type=str, help="The URL or path to the article.")
    parser.add_argument("-s", "--save", nargs="?", const="./", help="Save result (default: ./). Provide a path to save elsewhere.")
    args = parser.parse_args()

    handler = OmniArticleMarkdown(args.url_or_path)
    article = handler.parse()
    if not args.save:
        print(article)
    else:
        handler.save(args.save)