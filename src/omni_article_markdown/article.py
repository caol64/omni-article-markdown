from dataclasses import dataclass

from bs4.element import Tag


@dataclass
class Article:
    title: str
    url: str | None
    description: str | None
    body: Tag | str
