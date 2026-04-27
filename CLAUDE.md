# Claude Code Instructions — docker-ckan

## What This Repo Is
Docker images and docker-compose setup for running CKAN (open data portal) on Alpine Linux. Images are published to Docker Hub (`keitaro/ckan`) and GitHub Container Registry (`ghcr.io/keitaroinc/ckan`).

## Structure
- `images/ckan/<version>/` — multi-stage Dockerfiles for each supported CKAN version (2.10, 2.11); each directory also contains a `setup/` folder with runtime scripts
- `compose/` — docker-compose setup for local/production deployments
- `compose/docker-compose.yml` — top-level compose file that includes per-service YAML files
- `compose/services/` — per-service compose definitions: `ckan`, `ckan-workers` (default/bulk/priority), `db`, `solr`, `redis`
- `compose/config/` — env files per service (`ckan/.env`, `db/.env`, `solr/.env`, `redis/.env`) plus `.global-env` for shared vars (e.g. `CKAN_VERSION`, `REDIS_VERSION`)
- `scripts/update_dockerfiles.sh` — script to auto-update pinned Alpine package versions in all Dockerfiles
- `.github/workflows/` — CI (lint + build + security scan on PRs), publish on merge to `master`, and automated Dockerfile package update workflow

## Making Changes
Build a specific version image:
```sh
docker build --tag ghcr.io/keitaroinc/ckan:2.11.2 images/ckan/2.11
```

Run the full stack locally:
```sh
cd compose
docker compose build
docker compose up -d
```

Images are automatically built and pushed to Docker Hub and GHCR on merge to `master` via GitHub Actions. The image tag is read from the `IMAGE_TAG` env var in each Dockerfile.

## Conventions
- Base image is Alpine Linux (`python:<version>-alpine`); all system packages must be pinned to exact versions (e.g. `git=2.49.1-r0`).
- Use `uv` for all Python/CKAN package installation — it is pre-installed in the images.
- To extend an image, inherit `FROM ghcr.io/keitaroinc/ckan:<version>` and install extra extensions via `uv pip install --system`.
- Custom init scripts go in `docker-entrypoint.d/` (run before `prerun.py`) and post-init scripts in `docker-afterinit.d/` (run after).
- CKAN config is managed via environment variables using the `ckanext-envvars` extension; prefix env vars with `CKAN__` to map to `ckan.ini` settings.
- The default branch is `master`.
