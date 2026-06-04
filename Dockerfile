# The devcontainer should use the developer target and run as root with podman
# or docker with user namespaces.
FROM ghcr.io/diamondlightsource/ubuntu-devcontainer:noble AS developer

# Add any system dependencies for the developer/build environment here.
# PyQt6 from PyPI bundles its own Qt6, so only the dynamic libs it loads at
# import time (libEGL/libGL, X11/xcb, glib) are needed here.
RUN apt-get update -y && apt-get install -y --no-install-recommends \
    graphviz \
    libsm6 \
    libxext6 \
    libgl1 \
    libegl1 \
    libglib2.0-0 \
    libxcb-cursor0 \
    libxkbcommon-x11-0 \
    qt6-base-dev \
    && apt-get dist-clean \
    && rm -rf /var/lib/apt/lists/*

ENV XDG_RUNTIME_DIR=/tmp/runtime-vscode

# The build stage installs the context into the venv
FROM developer AS build

# Change the working directory to the `app` directory
# and copy in the project
WORKDIR /app
COPY . /app
RUN chmod o+wrX .

# Tell uv sync to install python in a known location so we can copy it out later
ENV UV_PYTHON_INSTALL_DIR=/python

# Sync the project without its dev dependencies
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-editable --no-dev --managed-python


FROM build AS debug


# Set origin to use ssh
RUN git remote set-url origin git@github.com:DiamondLightSource/dls-pmac-control.git


# For this pod to understand finding user information from LDAP
RUN apt update
RUN DEBIAN_FRONTEND=noninteractive apt install libnss-ldapd -y
RUN sed -i 's/files/ldap files/g' /etc/nsswitch.conf

# Make editable and debuggable
RUN uv pip install debugpy
RUN uv pip install -e .
ENV PATH=/app/.venv/bin:$PATH

# Alternate entrypoint to allow devcontainer to attach
# ENTRYPOINT [ "/bin/bash", "-c", "--" ]
# CMD [ "while true; do sleep 30; done;" ]


# The runtime stage copies the built venv into a runtime container
FROM ubuntu:noble AS runtime

# Runtime libs needed by the PyQt6 wheel (which bundles Qt6 but loads these
# from the system at import time).
RUN apt-get update && apt-get install -y --no-install-recommends \
    libegl1 \
    libgl1 \
    libglib2.0-0 \
    libxkbcommon0 \
    libxcb-cursor0 \
    libxcb-xinerama0 \
    libfontconfig1 \
    libdbus-1-3 \
    && rm -rf /var/lib/apt/lists/*

# Copy the python installation from the build stage
COPY --from=build /python /python

# Copy the environment, but not the source code
COPY --from=build /app/.venv /app/.venv
ENV PATH=/app/.venv/bin:$PATH
ENV XDG_RUNTIME_DIR=/tmp/runtime-:$USER

# change this entrypoint if it is not the same as the repo
ENTRYPOINT ["dls-pmac-control"]
