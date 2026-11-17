FROM python:3.13-bookworm

ARG PYPI_REGISTRY="https://pypi.org/simple/"

WORKDIR /app

RUN pip config set global.index-url "${PYPI_REGISTRY}"

# 先拷元数据再拷源码，最大化层缓存命中
COPY pyproject.toml README.md ./
COPY src/omni_article_markdown ./src/omni_article_markdown

# 从本地源码安装（保证镜像与仓库一致）；
# 显式安装固定版本的 playwright，使构建期下载的浏览器与运行期版本一致；
# headless=True 运行时使用 chromium-headless-shell，无需完整 chromium
RUN pip install --no-cache-dir . "playwright==1.57.0" && \
    playwright install chromium-headless-shell --with-deps && \
    rm -rf /root/.cache/pip

ENTRYPOINT ["mdcli"]
CMD ["--help"]
