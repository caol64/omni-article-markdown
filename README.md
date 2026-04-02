# 墨探 (omni-article-markdown)

[![PyPI](https://img.shields.io/pypi/v/omni-article-markdown)](https://pypi.org/project/omni-article-markdown/)
![Python](https://img.shields.io/pypi/pyversions/omni-article-markdown)
[![License](https://img.shields.io/github/license/caol64/omni-article-markdown)](LICENSE)
[![PyPI Downloads](https://static.pepy.tech/personalized-badge/omni-article-markdown?period=total&units=INTERNATIONAL_SYSTEM&left_color=GRAY&right_color=GREEN&left_text=downloads)](https://pepy.tech/projects/omni-article-markdown)
[![Docker Pulls](https://img.shields.io/docker/pulls/caol64/omnimd)](https://hub.docker.com/r/caol64/omnimd)
[![Stars](https://img.shields.io/github/stars/caol64/omni-article-markdown?style=social)](https://github.com/caol64/omni-article-markdown)

轻松将网页文章（博客、新闻、文档等）转换为 `Markdown` 格式。

![](data/1.gif)

## 简介

墨探的开发初衷，是为了解决一个问题：如何将来自互联网上各种不同网站的文章内容，精准且高效地转换成统一的Markdown格式。

众所周知，万维网上的网站设计风格迥异，其HTML结构也呈现出千差万别的特点。这种多样性给自动化内容提取和格式转换带来了巨大的困难。要实现一个能够适应各种复杂HTML结构的通用解决方案，并非易事。

我的想法是：从特定的网站开始适配，以点到面，逐步抽取出通用的解决方案，最后尽可能多的覆盖更多网站。

## 功能介绍

- 支持大部分 html 元素转换
- 部分页面支持katex公式转换（示例：[https://quantum.country/qcvc](https://quantum.country/qcvc)）
- 部分页面支持github gist（示例：[https://towardsdatascience.com/hands-on-multi-agent-llm-restaurant-simulation-with-python-and-openai](https://towardsdatascience.com/hands-on-multi-agent-llm-restaurant-simulation-with-python-and-openai)）
- 支持保存成文件或输出至`stdout`
- 支持突破某些网站的防爬虫策略（通过`playwright`）

以下是一些网站示例，大家可以自己测试下效果。

|站点|链接|备注|
--|--|--
|Medium|[link](https://medium.com/perry-street-software-engineering/architectural-linting-for-swift-made-easy-75d7f9f569cd)||
|csdn|[link](https://blog.csdn.net/weixin_41705306/article/details/148787220)||
|掘金|[link](https://juejin.cn/post/7405845617282449462)||
|公众号|[link](https://mp.weixin.qq.com/s/imHIKy7dqMmpm032eIhIJg)||
|网易|[link](https://www.163.com/dy/article/K2SPPGSK0514R9KE.html)||
|简书|[link](https://www.jianshu.com/p/20bd2e9b1f03)||
|Towards Data Science|[link](https://towardsdatascience.com/hands-on-multi-agent-llm-restaurant-simulation-with-python-and-openai/)||
|Quantamagazine|[link](https://www.quantamagazine.org/matter-vs-force-why-there-are-exactly-two-types-of-particles-20250623/)||
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
|人人都是产品经理|[link](https://www.woshipm.com/data-analysis/6276761.html)||
|Jetbrains博客|[link](https://blog.jetbrains.com/teamcity/2025/10/the-state-of-cicd/)||
|Claude文档|[link](https://docs.claude.com/en/docs/build-with-claude/prompt-caching)||
|Anthropic|[link](https://www.anthropic.com/news/claude-sonnet-4-5)||
|Meta博客|[link](https://engineering.fb.com/2025/10/06/developer-tools/openzl-open-source-format-aware-compression-framework/)||
|Android Developers Blog|[link](https://android-developers.googleblog.com/2025/11/jetpack-navigation-3-is-stable.html)||
|Spring Blog|[link](https://spring.io/blog/2026/01/13/spring-ai-generic-agent-skills)||
|Hackernoon|[link](https://hackernoon.com/attention-is-currency-ai-is-the-printing-press)||
|领英博客|[link](https://www.linkedin.com/blog/engineering/infrastructure/scalable-multi-language-service-discovery-at-linkedin)||
|华尔街见闻|[link](https://wallstreetcn.com/articles/3763051)||
|苹果开发者文档|[link](https://developer.apple.com/documentation/technologyoverviews/adopting-liquid-glass)||
|百家号|[link](https://baijiahao.baidu.com/s?id=1846135703319246634)||
|Snowflake 技术博客|[link](https://www.snowflake.com/en/blog/project-snowwork-business-users/)||
|知乎专栏|[link](https://zhuanlan.zhihu.com/p/1915735485801828475)||
|今日头条|[link](https://www.toutiao.com/article/7283050053155947062/)||
|X Articles|[link](https://x.com/Huxpro/status/2036993665965416601)||
|飞书|[link](https://feishu.feishu.cn/docx/ICI7dp1Uioh4EvxXn0HcxUapn0c)||
|~~Freedium~~|[link](https://freedium.cfd/https://medium.com/@devlink/ai-killed-my-coding-brain-but-im-rebuilding-it-8de7e1618bca)|已失效|

## 安装方式

### 方式一：pip（推荐）

```sh
pip install omni-article-markdown
```

安装完成后即可使用：

```bash
mdcli --help
```

## 基本用法

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

## 架构说明

![](data/1.jpg)

墨探主要分为三个模块：

- **Reader** 模块的功能是读取整个网页内容
- **Extractor** 模块的功能是提取正文内容，清理无用数据
- **Parser** 模块的功能是将 HTML 转换为 Markdown

## 贡献与反馈
- 发现解析问题？欢迎提交 [Issue](https://github.com/caol64/omni-article-markdown/issues)
- 改进解析？欢迎贡献 [Pull Request](https://github.com/caol64/omni-article-markdown/pulls)

## 赞助

如果你觉得墨探对你有帮助，可以给我家猫咪买点罐头 ❤️

[https://yuzhi.tech/sponsor](https://yuzhi.tech/sponsor)

## License

MIT License
