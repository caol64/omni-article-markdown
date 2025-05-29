from pluggy import HookimplMarker, HookspecMarker
from typing import List, Tuple, Optional, Protocol


hookspec = HookspecMarker("mdcli")
hookimpl = HookimplMarker("mdcli")

class ReaderPlugin(Protocol):
    def can_handle(self, url: str) -> bool:
        ...

    def read(self, url: str) -> str:
        ...


@hookspec
def register_reader_plugin() -> List[Tuple[str, ReaderPlugin]]:
    """
    Plugins can implement this hook to register a reader plugin.
    Should return a list of tuples, where each tuple is (plugin_name, plugin_instance).
    The plugin_instance must implement the ReaderPlugin protocol.
    """
    ...

@hookspec(firstresult=True)
def get_custom_reader(url: str) -> Optional[ReaderPlugin]:
    """
    Allows plugins to provide a custom reader for a given URL.
    The first plugin that returns a ReaderPlugin instance will be used.
    """
    ...
