FROM python:3.13-bookworm

ARG PYPI_REGISTRY="https://pypi.org/simple/"

WORKDIR /app

RUN pip config set global.index-url "${PYPI_REGISTRY}"
RUN pip install playwright==1.57.0 && \
    playwright install chromium --with-deps
RUN pip install omni-article-markdown
RUN mdcli install zhihu
RUN mdcli install toutiao
RUN mdcli install freedium
RUN mdcli install browser

ENTRYPOINT ["mdcli"]
CMD []
