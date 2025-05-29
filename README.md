# **omni-article-markdown**

轻松将网页文章（博客、新闻、文档等）转换为 `Markdown` 格式。

---

## Recent changes:

- 添加对github gist的支持
  - 示例：https://towardsdatascience.com/hands-on-multi-agent-llm-restaurant-simulation-with-python-and-openai
- 添加对katex公式的支持
  - 示例：https://quantum.country/qcvc

---

## **1. 功能介绍**
此脚本的开发初衷，是为了解决一个问题：如何将来自互联网上各种不同网站的文章内容，精准且高效地转换成统一的Markdown格式。

众所周知，万维网上的网站设计风格迥异，其HTML结构也呈现出千差万别的特点。这种多样性给自动化内容提取和格式转换带来了巨大的困难。要实现一个能够适应各种复杂HTML结构的通用解决方案，并非易事。

我的想法是：从特定的网站开始适配，以点到面，逐步抽取出通用的解决方案，最后尽可能多的覆盖更多网站。目前支持较好的网站有：

- 掘金
- Medium
- Freedium（先保存至本地）
- 公众号
- 简书
- 知乎专栏（先保存至本地）
- 今日头条（先保存至本地）
- towardsdatascience
- quantamagazine

其它网站暂未适配，但理论上都可以转换。需要注意的是有些网站不支持python直接抓取，或者有防机器人检测机制，这样的网站需要手动保存为 HTML 文件，再使用本工具。

---

## **2. 安装与运行**

首先，安装必要依赖项：
```sh
uv pip install -r requirements.txt
```

然后，可以使用以下两种形式运行：
```sh
uv run mdcli
```

或者：

```sh
python -m omni_article_markdown.cli
```

---

## **3. 参数说明**

运行命令及参数如下：

```sh
mdcli <URL_OR_PATH> [-s [SAVE_PATH]]
```

| 参数               | 说明 |
|--------------------|------|
| `URL_OR_PATH`     | **必填**，目标网页 URL 或本地 HTML 文件路径。 |
| `-s, --save`      | **可选**，启用保存：<br> - 仅 `-s`：默认保存至 `./`。<br> - `-s <SAVE_PATH>`：保存至指定路径。 |

---

## **4. 使用示例**

### **4.1 仅转换，不保存**
```sh
mdcli https://example.com
```

### **4.2 转换并保存到默认路径**
```sh
mdcli https://example.com -s
```

### **4.3 转换并保存到指定路径**
```sh
mdcli https://example.com -s /home/user/data.txt
```

---

## **5. 贡献与反馈**
- 发现解析问题？欢迎提交 [Issue](https://github.com/caol64/omni-article-markdown/issues)
- 改进解析？欢迎贡献 [Pull Request](https://github.com/caol64/omni-article-markdown/pulls)

---

## **6. 赞助**

如果您觉得不错，可以给我家猫咪买点罐头吃。[喂猫❤️](https://yuzhi.tech/sponsor)

---

## **7. License**

MIT License
