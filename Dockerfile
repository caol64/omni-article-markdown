FROM python:3.13-alpine

ARG PYPI_REGISTRY="https://pypi.org/simple/"

WORKDIR /app

RUN pip config set global.index-url "${PYPI_REGISTRY}"
RUN pip install omni-article-markdown

ENTRYPOINT ["mdcli"]
CMD []
