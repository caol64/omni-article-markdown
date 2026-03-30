import importlib
import pkgutil
from pathlib import Path
from typing import Any


def load_plugins[T](base_class: type[T], package_name: str, *args: Any, **kwargs: Any) -> list[T]:
    """
    通用插件加载器
    :param base_class: 插件必须继承的基类 (如 Extractor 或 Reader)
    :param package_name: 存放插件的子包名 (如 "extractors")
    :param args/kwargs: 实例化插件类时透传的参数
    """
    package_path = Path(__file__).parent / package_name
    plugins = []

    # 遍历子包下的所有模块
    for _, module_name, _ in pkgutil.iter_modules([str(package_path.resolve())]):
        # 动态导入模块
        full_module_name = f"omni_article_markdown.{package_name}.{module_name}"
        module = importlib.import_module(full_module_name)

        # 遍历模块中的所有属性
        for attr_name in dir(module):
            cls = getattr(module, attr_name)

            # 校验逻辑：是类、继承自基类、且不是基类本身
            if isinstance(cls, type) and issubclass(cls, base_class) and cls is not base_class:
                # 实例化并传入参数
                plugins.append(cls(*args, **kwargs))

    return plugins
