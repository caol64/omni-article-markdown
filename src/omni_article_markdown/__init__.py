from .omni_article_md import OmniArticleMarkdown

__all__ = ['OmniArticleMarkdown']

DEFAULT_PLUGINS = {
    "zhihu": "omnimd-zhihu-reader",
    "freedium": "omnimd-freedium-reader",
    "toutiao": "omnimd-toutiao-reader",
    "browser": "omnimd-browser-reader",
}
