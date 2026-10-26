# Decisions

### 2026-10-26 · The project moves to EDamLabs

**Decision.** `damvolkov/e-serde` is transferred to `edamlabs/e-serde`; documentation moves to
`edamlabs.github.io/e-serde`. The PyPI name stays `e-serde`, the import name stays `eserde`.

**Evidence.** EDamLabs gathers the open-source libraries and services under one organisation, one GitHub App
(`eself-maintenance`) and one maintenance engine (esteward). GitHub keeps redirects from the old URLs; a PyPI
project cannot be renamed, so the distribution name is kept.

**Rejected.** A new PyPI name (breaks every existing install for a cosmetic gain).

### 2026-10-26 · Identity: lib, eager

**Decision.** `pyproject.toml` declares `[tool.edamlabs]` `kind = "lib"`, `family = "eager"`; README and the docs
home carry the same identity line.

**Evidence.** e-serde ships an importable package released to PyPI (`lib`) and is EDamLabs' own e- product, not a
binding of a third-party engine (`eager`). esteward's `drift` module checks the manifest against the fleet entry.

**Rejected.** `binding`: the codecs are EDamLabs' own surface over several engines, with no single upstream whose
syntax and releases it follows.

### 2026-10-26 · Documentation built with Zensical

**Decision.** The site builds with Zensical (`zensical build --strict --clean`); `mkdocs.yml` stays the
configuration, read natively.

**Evidence.** Material for MkDocs is in maintenance until 2026-11-05 and MkDocs 2.0 drops plugins and theme
overrides; the existing site builds unchanged with Zensical 0.0.71, and `--strict` still aborts on a broken link.
17 packages (MkDocs, Material and their dependencies) leave `uv.lock`; 2 enter (`zensical`, `deepmerge`).

**Rejected.** Pinning MkDocs 1.x on a framework leaving maintenance.

### 2026-10-26 · Renovate replaces Dependabot; routine updates merge themselves

**Decision.** `.github/renovate.json` replaces `.github/dependabot.yml`. Python tooling, GitHub actions (pinned by
digest), lock file maintenance, runtime Python patches and Rust crate patches merge themselves through GitHub
auto-merge after every required check; Rust minor and major updates wait for a human. `saphyr` stays pinned and
out of the bot's reach.

**Evidence.** The same policy runs on anytomd and etrafilatura. Dependabot has no per-rule auto-merge without an
extra workflow; Renovate expresses grouping, range strategy and auto-merge per dependency type in one file.
saphyr 0.1.0 regressed YAML null semantics (Dependabot ignored it for the same reason).

**Rejected.** Keeping Dependabot plus an auto-merge workflow (two places for one policy); a human merging every
green routine PR.

### 2026-10-26 · The organisation's GitHub App token replaces the release PAT

**Decision.** `release.yml` mints a token from the EDamLabs GitHub App (`vars.APP_CLIENT_ID`,
`secrets.APP_PRIVATE_KEY`, contents and pull-requests write) in place of the personal `RELEASE_PAT`.

**Evidence.** Pushes made with an App installation token trigger workflows, as the PAT's did, so the release PR
still gets its CI run; the token is short-lived, scoped to the two permissions the job needs, and belongs to the
organisation rather than to one account.

**Rejected.** Keeping a personal PAT after the transfer (long-lived, tied to one person); `GITHUB_TOKEN` (its
pushes do not trigger CI on the release PR).
