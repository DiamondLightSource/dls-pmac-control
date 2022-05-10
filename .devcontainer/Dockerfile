# See here for image contents: https://github.com/microsoft/vscode-dev-containers/tree/v0.231.6/containers/python-3/.devcontainer/base.Dockerfile

ARG BASE="mcr.microsoft.com/vscode/devcontainers/python:0-3.10-bullseye"
FROM ${BASE} as base

# things to make pyQt5 work
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive && \
    apt-get install -y --no-install-recommends \
    ffmpeg libsm6 libxext6 libqt5gui5 libxcb-xinerama0
ENV XDG_RUNTIME_DIR=/tmp/runtime-vscode

# for testing
RUN apt-get install -y x11-apps

FROM base as developer

COPY . workspace
# install runtime from DIST if there is one
RUN test -d /workspace/dist && pip install $([ -f requirements.txt ] && echo -r requirements.txt ) /workspace/dist/*.whl || :

FROM developer as runtime

CMD ["dls-pmac-control"]