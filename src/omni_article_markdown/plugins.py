import pluggy

from . import hookspecs

pm = pluggy.PluginManager("mdcli")
pm.add_hookspecs(hookspecs)

_loaded_plugins = False

def load_mdcli_plugins():
    global _loaded_plugins
    if _loaded_plugins:
        return
    pm.load_setuptools_entrypoints("mdcli")
    _loaded_plugins = True

# 在应用启动时调用
load_mdcli_plugins()
