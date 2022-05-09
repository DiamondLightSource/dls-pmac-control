# See here for image contents: https://github.com/microsoft/vscode-dev-containers/tree/v0.231.6/containers/python-3/.devcontainer/base.Dockerfile

ARG BASE="mcr.microsoft.com/vscode/devcontainers/python:0-3.10-bullseye"
ARG ENTRYPOINT=python
FROM ${BASE}

# things to make pyQt5 work
RUN apt-get update && export DEBIAN_FRONTEND=noninteractive && \
    apt-get install -y --no-install-recommends \
    ffmpeg libsm6 libxext6 libqt5gui5 libxcb-xinerama0
ENV XDG_RUNTIME_DIR=/tmp/runtime-vscode

# for testing
RUN apt-get install -y x11-apps

# install runtime from DIST if this is one
RUN test -d dist && pip install dist/*.whl || :

ENTRYPOINT ${ENTRYPOINT}
