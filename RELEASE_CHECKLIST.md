# Release checklist

## Repository

- [x] Harbor schema 1.4 dataset contains 100 tasks.
- [x] English and Chinese quick-start and Harbor guides are synchronized.
- [x] Examples use public URLs, generic endpoints, and placeholder credentials.
- [x] Local outputs, credentials, caches, and publication state are ignored.
- [x] Internal registry names, machine paths, and organization-specific security
      contacts are absent from release content.
- [x] Review the final Git diff and commit the release.
- [x] Push the release commit after maintainer approval.
- [ ] Create and push a release tag after version approval.

## Images

- [x] Confirm all 100 source images exist locally.
- [x] Review the 100-image dry-run mapping.
- [x] Authenticate Docker CLI with write access to
      `docker.io/honglifish/csbench`.
- [x] Publish all 100 unchanged images.
- [x] Verify all public tags and record their registry digests.
- [x] Run a no-model Harbor smoke test against a public Docker Hub tag.

## Validation

- [x] Run `.venv/bin/pytest -q`.
- [x] Run `python3 -m py_compile scripts/*.py`.
- [x] Run `bash -n scripts/*.sh`.
- [x] Run `git diff --check`.
- [x] Regenerate the dataset in an isolated directory and confirm an exact diff.
