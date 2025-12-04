CI and Coverage

- CI workflows:
  - CI: .github/workflows/ci.yml — lint, type-check, tests, coverage XML, Codecov upload
  - Coverage: .github/workflows/coverage.yml — focused coverage run with failure threshold

Minimum coverage and failure behavior
- Pytest in CI uses `--cov-fail-under=90` to fail the job if overall coverage drops below 90%.
- Codecov thresholds (codecov.yml):
  - Project coverage target: 90% (fails Codecov status if lower)
  - Patch (changed lines) target: 95% (fails Codecov status if lower)
- The Codecov upload step is configured with `fail_ci_if_error: true` to fail the job if upload fails.

Codecov setup (private repo)
1) Install the Codecov GitHub App and grant it access to this repo. With the App installed, CI uploads can be tokenless (recommended). Our CI uses codecov/codecov-action@v5 without a token.
2) Badge token for private repos (used in README):
   - In Codecov → Repo Settings → Badge, copy the tokenized badge URL parameter (e.g., `?token=abc123`)
   - Edit README.md and replace `REPLACE_WITH_CODECOV_BADGE_TOKEN` with that token.

Manual troubleshooting
- Re-run latest CI job: use GitHub UI “Re-run all jobs” or CLI:
  - `gh run list --workflow=CI --limit 5`
  - `gh run view <run_id> --verbose`
- Check coverage locally: `make coverage`
