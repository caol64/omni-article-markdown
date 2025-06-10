from pluggy import HookimplMarker, HookspecMarker
from typing import Optional, Protocol


hookspec = HookspecMarker("mdcli")
hookimpl = HookimplMarker("mdcli")

class ReaderPlugin(Protocol):
    def can_handle(self, url: str) -> bool:
        ...

    def read(self, url: str) -> str:
        ...


@hookspec(firstresult=True)
def get_custom_reader(url: str) -> Optional[ReaderPlugin]:
    """
    Allows plugins to provide a custom reader for a given URL.
    The first plugin that returns a ReaderPlugin instance will be used.
    """
    ...
