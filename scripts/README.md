# Workspace maintenance tools

Learners should start with the [Workspace README](../README.md) and the `python -m oee_workspace` CLI. Scripts in this directory maintain the public catalogue, review OEE release changes and test the published files. They are not an alternate course generator.

Use Python 3.11 from the repository root. Learner CLI commands read an already installed, signed OEE curriculum selected by [`oee-curriculum.lock.json`](../oee-curriculum.lock.json). They do not accept a Git checkout or revision, fetch an archive or run learner programs.

## Scripts at a glance

| Script | Purpose |
| --- | --- |
| `install-official-curriculum.py` | Check six official release assets before installing the checked wheel, then verify and install the signed archive offline |
| `check-resources.py` | Validate the catalogue and any active release-keyed resource maps |
| `render-resource-guides.py` | Generate or check reading guides for approved, matching resource maps |
| `run-pinned-toolkit.py` | Verify the installed Toolkit identity and run it in isolated Python |
| `verify-oee-export.py` | Check the course export v2 structure and source identity |
| `verify-assessment-context.py` | Check context v1 against the course export, manifest and reviewed source ranges |
| `report-oee-drift.py` | Compare reviewed installed releases without changing learner locks or files |
| `verify-external-workspace.py` | Run independent learner-flow smoke with a disposable test-signed OEE release |
| `verify-official-workspace.py` | Exercise real published Toolkit and curriculum assets against the Workspace CLI |

## Validate repository contracts

The repository currently has no active release-keyed resource maps. The public catalogue still works, and missing optional reading plans never block course scaffolding.

```sh
python scripts/check-resources.py
python scripts/render-resource-guides.py --check
python -m unittest discover -s tests -p 'test_*.py' -v
python -m oee_workspace --help
npx --yes markdownlint-cli2@0.24.0
```

The tests need `jsonschema==4.23.0` for the JSON Schema contract checks. CI installs it separately. Most CLI operations also require the exact official Toolkit distribution and an already installed signed release. The [learner CLI setup guide](../docs/CLI-SETUP.md) covers installation, and the [release trust record](../docs/OEE-RELEASE-TRUST.md) records the approved technical identities.

A reviewed, release-keyed map can be checked using the exact lock and a verified store:

```sh
python scripts/check-resources.py --lock ./oee-curriculum.lock.json
python scripts/render-resource-guides.py --lock ./oee-curriculum.lock.json --check
```

These commands validate active maps when they exist. They do not create or approve maps from editorial notes. Resource maps use schema v3 and Toolkit exports use exportVersion 2. See [resource review](../resources/README.md).

## Verify the published OEE release

The [official-release smoke workflow](../.github/workflows/official-release-smoke.yml) downloads the Toolkit `0.2.0` wheel/sdist and curriculum `2026.11.1` archive, attestation, signature and public key. It validates their independently pinned hashes before executing the wheel, verifies the real steward-signed archive and runs the learner CLI on Linux, macOS and Windows. It compares the course export and assessment context digests across platforms.

To check the downloaded assets before installation:

```sh
python -I scripts/install-official-curriculum.py --artifacts oee-official-assets --verify-only
```

After installing the exact wheel and hash-pinned verification dependencies, the [installer](install-official-curriculum.py) and `verify-official-workspace.py` can run offline against those assets. The [CLI setup guide](../docs/CLI-SETUP.md) gives the learner download and install sequence. Never use a disposable CI signing key as an official learner trust anchor.

The [independent readiness workflow](../.github/workflows/release-readiness.yml) is separate: it builds and signs a disposable OEE test release, then checks Toolkit export, `doctor`, SEF1/SEF10 folders, no-overwrite behavior and evidence operations without any official signing key. Its temporary release is not approved for students.

## Review curriculum changes

A new curriculum release does not update existing learners or make editorial maps approved. Once two releases and their locks have been independently reviewed and installed, compare them with:

```sh
python scripts/report-oee-drift.py --lock ./oee-curriculum.lock.json --target-lock ./reviewed-next-release.lock.json --course SEF1
```

The example requires an existing active SEF1 resource map; none has been approved yet, so running it now reports no active maps. Optional `--store` and `--target-store` select existing verified release stores. The advisory comparison reports changed course source hashes, outcomes, assessments and lesson locators. It never selects a new release, transfers chapter mappings or edits learner work.

Read [OEE upstream drift](../docs/OEE-UPSTREAM-DRIFT.md) before reviewing a new resource map, and [CONTRIBUTING](../CONTRIBUTING.md#releases) before publishing another Workspace version.

## Preserve learner files

Course publication stages new directories and refuses existing destinations. Evidence creation and export use exclusive file publication to avoid overwriting records. If the filesystem cannot support the required safe operation, the command fails. Concurrent external mutations or abrupt termination may still require manual inspection.

Exports include selected JSON attempt records, not referenced artifact bytes. Neither scripts nor CLI submit learner data, certify work or operate a hosted grading service. See the [evidence guide](../evidence/README.md) and [AI safety boundaries](../docs/AI-SAFETY.md).
