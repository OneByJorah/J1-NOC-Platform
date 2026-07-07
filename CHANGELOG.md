# Changelog

All notable changes to this project are documented here, per
[Keep a Changelog](https://keepachangelog.org/) and
[Conventional Commits](https://www.conventionalcommits.org/).

## [v11.1.0] - 2026-07-07

### Added
- Engineering tooling: `ruff` lint+format, `mypy --strict`, `uv` lockfile, pre-commit suite, `commitlint`
- `/metrics` Prometheus endpoint (request count + latency) and structured JSON logging
- `/api/system/overview` endpoint with live service-health probes
- Revamped dashboard: KPI tiles, live service-status panel, device-health donut (recharts)
- CI quality gates: backend (ruff+mypy+pytest+coverage), frontend build, Trivy image scan, Syft SBOM, dependency SCA
- Branch protection requiring CI checks + 1 review

### Changed
- Backend image now runs as non-root `appuser`; SBOM generated in CI
- Schema managed exclusively via Alembic (removed `create_all` from lifespan)
- Repo hygiene: `CODEOWNERS`, `.dockerignore`, `.editorconfig`, `.gitignore` excludes build output

### Fixed
- `DATABASE_URL` in live env URL-encodes the Postgres password (`%` → `%25`)

## [1.0.0] - 2026-07-07

### Added
- Initial release
- Dockerfile improvements (backend, frontend)
- docker-compose.yml with healthchecks
- nginx.conf improvements

## [Unreleased]
