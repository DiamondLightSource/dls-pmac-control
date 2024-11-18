# Run in a container

Pre-built containers with dls-pmac-control and its dependencies already
installed are available on [Github Container Registry](https://ghcr.io/DiamondLightSource/dls-pmac-control).

## Starting the container

To pull the container from github container registry and run:

```
$ docker run ghcr.io/diamondlightsource/dls-pmac-control:latest --version
```

To get a released version, use a numbered release instead of `latest`.
