# 墨探 (omni-article-markdown)

[![PyPI](https://img.shields.io/pypi/v/omni-article-markdown?logo=pypi)](https://pypi.org/project/omni-article-markdown/)
![Python](https://img.shields.io/pypi/pyversions/omni-article-markdown?logo=python)
[![License](https://img.shields.io/github/license/caol64/omni-article-markdown)](LICENSE)
![PyPI Downloads](https://img.shields.io/pypi/dm/omni-article-markdown?logo=pypi)
[![Stars](https://img.shields.io/github/stars/caol64/omni-article-markdown?style=social)](https://github.com/caol64/omni-article-markdown)

轻松将网页文章（博客、新闻、文档等）转换为 `Markdown` 格式。

![](data/1.gif)

---

## 项目简介
墨探的开发初衷，是为了解决一个问题：如何将来自互联网上各种不同网站的文章内容，精准且高效地转换成统一的Markdown格式。

众所周知，万维网上的网站设计风格迥异，其HTML结构也呈现出千差万别的特点。这种多样性给自动化内容提取和格式转换带来了巨大的困难。要实现一个能够适应各种复杂HTML结构的通用解决方案，并非易事。

我的想法是：从特定的网站开始适配，以点到面，逐步抽取出通用的解决方案，最后尽可能多的覆盖更多网站。

---

## 功能介绍

- 支持大部分 html 元素转换
- 部分页面支持katex公式转换（示例：[https://quantum.country/qcvc](https://quantum.country/qcvc)）
- 部分页面支持github gist（示例：[https://towardsdatascience.com/hands-on-multi-agent-llm-restaurant-simulation-with-python-and-openai](https://towardsdatascience.com/hands-on-multi-agent-llm-restaurant-simulation-with-python-and-openai)）
- 支持保存成文件或输出至`stdout`
- 支持突破某些网站的防爬虫策略（需安装插件）

以下是一些网站示例，大家可以自己测试下效果。

|站点|链接|备注|
--|--|--
|Medium|[link](https://medium.com/perry-street-software-engineering/architectural-linting-for-swift-made-easy-75d7f9f569cd)||
|csdn|[link](https://blog.csdn.net/weixin_41705306/article/details/148787220)||
|掘金|[link](https://juejin.cn/post/7405845617282449462)||
|知乎专栏|[link](https://zhuanlan.zhihu.com/p/1915735485801828475)|需安装zhihu插件|
|公众号|[link](https://mp.weixin.qq.com/s/imHIKy7dqMmpm032eIhIJg)||
|今日头条|[link](https://www.toutiao.com/article/7283050053155947062/)|需安装toutiao插件|
|网易|[link](https://www.163.com/dy/article/K2SPPGSK0514R9KE.html)||
|简书|[link](https://www.jianshu.com/p/20bd2e9b1f03)||
|Freedium|[link](https://freedium.cfd/https://medium.com/@devlink/ai-killed-my-coding-brain-but-im-rebuilding-it-8de7e1618bca)|需安装freedium插件|
|Towards Data Science|[link](https://towardsdatascience.com/hands-on-multi-agent-llm-restaurant-simulation-with-python-and-openai/)||
|Quantamagazine|[link](https://www.quantamagazine.org/matter-vs-force-why-there-are-exactly-two-types-of-particles-20250623/)||
|苹果开发者文档|[link](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)|需安装browser插件|
|Cloudflare博客|[link](https://blog.cloudflare.com/20-percent-internet-upgrade/)||
|阿里云开发者社区|[link](https://developer.aliyun.com/article/791514)||
|微软技术文档|[link](https://learn.microsoft.com/en-us/dotnet/ai/get-started-app-chat-template)||
|InfoQ|[link](https://www.infoq.com/articles/ai-ml-data-engineering-trends-2025/)||
|博客园|[link](https://www.cnblogs.com/hez2010/p/19097937/runtime-async)||
|思否|[link](https://segmentfault.com/a/1190000047273730)||
|开源中国|[link](https://my.oschina.net/SeaTunnel/blog/18694930)||
|Forbes|[link](https://www.forbes.com/sites/danalexander/2025/10/10/trump-is-now-one-of-americas-biggest-bitcoin-investors/)||
|少数派|[link](https://sspai.com/post/102861)||
|语雀|[link](https://www.yuque.com/yuque/ng1qth/about)||
|腾讯云开发者社区|[link](https://cloud.tencent.com/developer/article/2571935)||

---

## 快速开始

1. 安装

```sh
pip install omni-article-markdown
```

2. 运行说明

**仅转换**

```sh
mdcli https://example.com
```

**保存到当前目录**

```sh
mdcli https://example.com -s
```

**保存到指定路径**

```sh
mdcli https://example.com -s /home/user/
```

---

## 插件机制

[「墨探」是如何使用插件机制构建可扩展架构的](https://babyno.top/posts/2025/06/a-deep-dive-into-the-extensible-architecture-of-omni-article-markdown/)

**安装插件**

安装插件和`pip`命令格式相同：

```sh
mdcli install <PLUGIN_NAME_OR_PACKAGE_NAME> [-U] [-e]
```

**示例：安装知乎解析插件**

```sh
mdcli install zhihu
```

或者，你可以使用 `-e` 参数安装本地可编辑的包。

```sh
mdcli install -e "./plugins/omnimd-zhihu-reader"
```

**升级插件**

```sh
mdcli install zhihu -U
```

**卸载插件**

如果你想移除一个已安装的插件，可以使用 `mdcli` 提供的 `uninstall` 命令。

```sh
mdcli uninstall zhihu
```

或者，使用插件的全称删除

```sh
mdcli uninstall omnimd-zhihu-reader
```

**已支持的插件**

目前已发布4个插件，你可以按需安装：

| 命令                             | 说明                                                     |
|----------------------------------|----------------------------------------------------------|
| `mdcli install zhihu`              | 知乎专栏 |
| `mdcli install toutiao`            | 今日头条                         |
| `mdcli install freedium`           | Freedium                         |
| `mdcli install browser`           | 需要启用浏览器的JS功能才能访问的页面（如Apple Developer Documentation）                         |

**开发自己的插件**

文档编写中。

---

## 架构说明

![](data/1.jpg)

墨探主要分为三个模块：

- **Reader** 模块的功能是读取整个网页内容
- **Extractor** 模块的功能是提取正文内容，清理无用数据
- **Parser** 模块的功能是将 HTML 转换为 Markdown

---

## 贡献与反馈
- 发现解析问题？欢迎提交 [Issue](https://github.com/caol64/omni-article-markdown/issues)
- 改进解析？欢迎贡献 [Pull Request](https://github.com/caol64/omni-article-markdown/pulls)
- 开发插件？文档正在筹备中

---

## 赞助

如果您觉得不错，可以给我家猫咪买点罐头吃。[喂猫❤️](https://yuzhi.tech/sponsor)

---

## License

MIT License
