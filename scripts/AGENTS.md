# Scripts

Start and stop scripts for the Docker container.

## Mac/Linux

```
bash scripts/start.sh   # docker build + docker run detached
bash scripts/stop.sh    # docker stop + docker rm
```

## Windows

```
scripts\start.bat
scripts\stop.bat
```

Both run the container named `pm-app`, exposing it on host port 8000. The stop script no-ops if the container isn't running.
