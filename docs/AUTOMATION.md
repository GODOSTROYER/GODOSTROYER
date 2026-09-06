# Profile automation

The checked-in README and SVG artwork work without live third-party badge services. Python 3.10+ and the standard library are the only build dependencies.

```sh
python scripts/update_profile.py
python scripts/render_profile.py
python -m unittest discover -s tests -v
```

Set `GITHUB_TOKEN` in the process environment to increase GitHub API limits and attempt the contribution calendar query. No personal access token is required by the workflow. The built-in Actions token may not be authorized to query a user's calendar; in that case the last successful calendar is retained. No token values or API error response bodies are printed.

`python scripts/update_profile.py --offline` checks the existing snapshot without network access or file changes. `--config path/to/profile.config.json` and `--output path/to/activity.json` support alternate local files. The configured `username` is the source of truth; `featured_repos` contains up to 12 full `owner/repo` names.

## Sources and fallback

Requests go only to `https://api.github.com`, with redirects refused, a 15-second per-request timeout, and a response size limit. Repository metadata lists all publicly owned repositories and must explicitly report `private: false` before use. Pagination is bounded at 1,000 repositories; exceeding this limit retains the last successful repository section. Releases come from the configured featured public repositories; drafts are excluded. Activity uses the public user events endpoint, excludes bots and pushes to the profile repository, and shows up to six distinct recent supported events. GitHub's public events feed is a recent, limited feed, not a complete activity history.

The optional GraphQL contribution calendar records dates, levels, and aggregate counts only. GitHub may include anonymized private contribution counts when the profile owner has enabled their public display; this does not expose private repository names, messages, or activity details. An unavailable calendar has `total: null`, never a fabricated zero.

`data/activity.json` has schema version 1 and sections `repositories`, `releases`, `activity`, and `contributions`, plus `username` and `updated_at`. Every section is replaced only after its complete response validates. A failed request retains that section from the previous snapshot. `updated_at` advances only when all three public sections succeed, so a partially retained feed is never labeled freshly retrieved. The optional contribution calendar can be older. A total outage leaves the entire snapshot unchanged. Writes use a temporary file and atomic replacement. Invalid configuration or an invalid existing snapshot fails without replacement.

## GitHub Actions

The workflow runs daily at 03:17 UTC (08:47 IST), manually through **Actions → Refresh profile → Run workflow**, and on relevant source changes when the default branch is `main` or `master`. Source triggers include project images and font outlines. Scheduled Actions can be delayed by GitHub and may be disabled after prolonged repository inactivity. The schedule runs from the default branch.

Pull requests validate data and run `python scripts/render_profile.py --check` offline, failing on generated-file drift without rewriting it. They use read-only repository permissions, no persisted checkout credentials, and no API token passed to scripts. Run the renderer locally and commit its output alongside source edits. The refresh job is restricted to the `GODOSTROYER` owner, uses the default branch, and requests only `contents: write`. It stages only `README.md`, `data/activity.json`, and `assets/generated`; it commits only when those files change. Generated files do not match the push trigger, preventing a refresh loop. Concurrent runs are serialized. A branch rule prohibiting direct pushes will require adjusting the publishing strategy; no bypass is configured.

The only external Action is [actions/checkout v4.2.2](https://github.com/actions/checkout/releases/tag/v4.2.2), pinned to the [verified release commit](https://github.com/actions/checkout/commit/11bd71901bbe5b1630ceea73d27597364c9af683). Python comes from the Ubuntu 24.04 runner image. Update the pin deliberately after reviewing the upstream release.

Changing to another account requires updating `profile.config.json`, replacing the checked-in snapshot for the new username, and changing the workflow's owner guard. If the default branch is renamed, also update the `push.branches` filter.
