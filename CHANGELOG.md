# Changelog

All notable changes to this project are documented here, per
[Keep a Changelog](https://keepachangelog.org/) and
[Conventional Commits](https://www.conventionalcommits.org/).

## [Unreleased]

### Added
- Engineering tooling: `ruff` (lint+format), `mypy --strict`, `uv` lockfile, pre-commit suite, commitlint.
- Repo hygiene: `CODEOWNERS`, `.dockerignore`, `.editorconfig`, `j1.yaml`, `CHANGELOG.md`.
- Hardened non-root container images with SBOM generation.
- Prometheus `/metrics` endpoint + structured JSON logging to Loki.
- CI hardening: lint + type-check + coverage gate + Trivy image scan + SCA.
- Revamped dashboard with live health, service status, and metrics cards.
