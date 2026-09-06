#!/usr/bin/env python3
"""Fetch public profile data with section-level last-good fallback (stdlib only)."""
import argparse
import copy
from datetime import datetime, timezone
import json
import os
from pathlib import Path
import re
import sys
import tempfile
import urllib.error
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
REPO = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
USER = re.compile(r"^[A-Za-z0-9-]{1,39}$")
LEVELS = {name: i for i, name in enumerate(("NONE", "FIRST_QUARTILE", "SECOND_QUARTILE", "THIRD_QUARTILE", "FOURTH_QUARTILE"))}


class DataError(ValueError):
    pass


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise DataError("API redirect refused")


class GitHub:
    def __init__(self, token=None):
        self.token = token
        self.opener = urllib.request.build_opener(NoRedirect)

    def get(self, path, body=None):
        url = "https://api.github.com" + path
        parsed = urllib.parse.urlsplit(url)
        if parsed.hostname != "api.github.com" or not path.startswith("/") or parsed.fragment:
            raise DataError("Untrusted API URL")
        headers = {"Accept": "application/vnd.github+json", "User-Agent": "profile-public-dashboard", "X-GitHub-Api-Version": "2022-11-28"}
        if self.token:
            headers["Authorization"] = "Bearer " + self.token
        data = json.dumps(body).encode() if body else None
        if data:
            headers["Content-Type"] = "application/json"
        with self.opener.open(urllib.request.Request(url, data=data, headers=headers), timeout=15) as response:
            raw = response.read(4_000_001)
        if len(raw) > 4_000_000:
            raise DataError("Oversized API response")
        return json.loads(raw)


def text(value):
    if not isinstance(value, str):
        raise DataError("Expected text")
    return value


def number(value):
    if type(value) is not int or value < 0:
        raise DataError("Expected nonnegative integer")
    return value


def iso_date(value):
    value = text(value)
    if not re.fullmatch(r"\d{4}-\d{2}-\d{2}(?:T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2}))?", value):
        raise DataError("Expected ISO date or timestamp")
    datetime.fromisoformat(value.replace("Z", "+00:00"))
    return value


def github_url(value):
    value = text(value)
    parsed = urllib.parse.urlsplit(value)
    if parsed.scheme != "https" or parsed.netloc != "github.com":
        raise DataError("Expected GitHub URL")
    return value


def repository(raw, expected):
    if not isinstance(raw, dict) or raw.get("private") is not False:
        raise DataError("Repository is not explicitly public")
    if text(raw.get("full_name")).lower() != expected.lower():
        raise DataError("Repository identity mismatch")
    result = {k: text(raw[k]) for k in ("full_name", "name", "updated_at", "pushed_at")}
    for key in ("updated_at", "pushed_at"):
        iso_date(result[key])
    result["html_url"] = github_url(raw["html_url"])
    for key in ("description", "homepage", "language"):
        result[key] = text(raw[key]) if raw.get(key) is not None else None
    for key in ("stargazers_count", "forks_count"):
        result[key] = number(raw[key])
    for key in ("archived", "fork"):
        if type(raw[key]) is not bool:
            raise DataError("Expected boolean")
        result[key] = raw[key]
    return result


def releases(raw, repo):
    if not isinstance(raw, list):
        raise DataError("Expected releases list")
    result = []
    for item in raw:
        if not isinstance(item, dict):
            raise DataError("Invalid release")
        if item.get("draft") is not False:
            continue
        result.append({"repo": repo, "name": text(item.get("name") or item["tag_name"]), "tag": text(item["tag_name"]), "url": github_url(item["html_url"]), "published_at": iso_date(item["published_at"])})
    return result


def activity(raw, username):
    if not isinstance(raw, list):
        raise DataError("Expected events list")
    result = []
    seen = set()
    for event in raw:
        if not isinstance(event, dict):
            raise DataError("Invalid event")
        if event.get("public") is not True:
            continue
        actor = event.get("actor", {}).get("login", "")
        if actor.lower() != username.lower() or actor.lower().endswith("[bot]"):
            continue
        repo = text(event.get("repo", {}).get("name"))
        if not REPO.fullmatch(repo):
            raise DataError("Invalid event repository")
        kind, payload = event.get("type"), event.get("payload", {})
        url, title = "https://github.com/" + repo, None
        if kind == "PushEvent":
            if repo.lower() == f"{username}/{username}".lower():
                continue
            title = "Pushed to " + repo.split("/", 1)[1]
        elif kind in ("PullRequestEvent", "IssuesEvent"):
            item = payload.get("pull_request" if kind == "PullRequestEvent" else "issue", {})
            title = text(payload.get("action")) + ": " + text(item.get("title"))
            url = github_url(item.get("html_url"))
        elif kind == "ReleaseEvent":
            item = payload.get("release", {})
            if item.get("draft") is not False:
                continue
            title = "Released " + text(item.get("tag_name"))
            url = github_url(item.get("html_url"))
        elif kind == "CreateEvent" and payload.get("ref_type") == "repository":
            title = "Created " + repo.split("/", 1)[1]
        if title is None:
            continue
        key = (kind, repo, title, url)
        if key not in seen:
            result.append({"type": kind, "repo": repo, "title": title, "url": url, "date": iso_date(event.get("created_at"))})
            seen.add(key)
    return sorted(result, key=lambda item: item["date"], reverse=True)[:6]


def contributions(raw):
    if raw.get("errors"):
        raise DataError("GraphQL returned errors")
    collection = raw["data"]["user"]["contributionsCollection"]
    calendar = collection["contributionCalendar"]
    weeks = []
    for week in calendar["weeks"]:
        days = [{"date": iso_date(day["date"]), "count": number(day["contributionCount"]), "level": LEVELS[day["contributionLevel"]]} for day in week["contributionDays"]]
        if not 1 <= len(days) <= 7:
            raise DataError("Invalid calendar week")
        weeks.append({"days": days})
    if not weeks:
        raise DataError("Empty contribution calendar")
    return {"total": number(calendar["totalContributions"]), "from": iso_date(collection["startedAt"]), "to": iso_date(collection["endedAt"]), "weeks": weeks}


def empty_snapshot(username):
    return {"schema_version": 1, "username": username, "updated_at": None, "repositories": [], "releases": [], "activity": [], "contributions": {"total": None, "from": None, "to": None, "weeks": []}}


def validate_snapshot(data, username):
    if not isinstance(data, dict) or data.get("schema_version") != 1 or text(data.get("username", "")).lower() != username.lower():
        raise DataError("Snapshot schema or username mismatch")
    if data.get("updated_at") is not None:
        iso_date(data["updated_at"])
    for section in ("repositories", "releases", "activity"):
        if not isinstance(data.get(section), list) or any(not isinstance(item, dict) for item in data[section]):
            raise DataError("Invalid snapshot section: " + section)
    for item in data["repositories"]:
        name = text(item.get("full_name"))
        if not REPO.fullmatch(name):
            raise DataError("Invalid repository identity")
        repository(item | {"private": False}, name)
    for item in data["releases"]:
        for key in ("repo", "name", "tag", "published_at"):
            text(item[key])
        github_url(item["url"])
        iso_date(item["published_at"])
    for item in data["activity"]:
        for key in ("type", "repo", "title", "date"):
            text(item[key])
        github_url(item["url"])
        iso_date(item["date"])
    calendar = data.get("contributions")
    if not isinstance(calendar, dict) or not isinstance(calendar.get("weeks"), list):
        raise DataError("Invalid contribution snapshot")
    if calendar.get("total") is not None:
        number(calendar["total"])
        iso_date(calendar["from"])
        iso_date(calendar["to"])
    for week in calendar["weeks"]:
        if not isinstance(week, dict) or not isinstance(week.get("days"), list) or not 1 <= len(week["days"]) <= 7:
            raise DataError("Invalid contribution week")
        for day in week["days"]:
            iso_date(day["date"])
            number(day["count"])
            if number(day["level"]) > 4:
                raise DataError("Invalid contribution level")
    return data


def refresh(config, previous, api, now=None):
    username = config["username"]
    result = copy.deepcopy(validate_snapshot(previous, username))
    succeeded = False
    failures = []

    def attempt(section, fetch):
        nonlocal succeeded
        try:
            result[section] = fetch()
            succeeded = True
        except (DataError, KeyError, TypeError, ValueError, AttributeError, OSError, urllib.error.URLError):
            failures.append(section)

    repos = config.get("featured_repos", [])
    def fetch_repositories():
        found = []
        for page in range(1, 11):
            raw = api.get(f"/users/{username}/repos?type=owner&per_page=100&sort=updated&page={page}")
            if not isinstance(raw, list):
                raise DataError("Expected repository list")
            for item in raw:
                if not isinstance(item, dict):
                    raise DataError("Invalid repository")
                full_name = text(item.get("full_name"))
                if not REPO.fullmatch(full_name) or full_name.split("/", 1)[0].lower() != username.lower():
                    raise DataError("Repository owner mismatch")
                found.append(repository(item, full_name))
            if len(raw) < 100:
                return found
        raise DataError("Repository pagination limit reached")
    attempt("repositories", fetch_repositories)
    def fetch_releases():
        # Public metadata is checked independently before release retrieval.
        found = []
        for repo in repos:
            repository(api.get("/repos/" + repo), repo)
            found.extend(releases(api.get("/repos/" + repo + "/releases?per_page=3"), repo))
        return sorted(found, key=lambda item: item["published_at"], reverse=True)[:4]
    attempt("releases", fetch_releases)
    attempt("activity", lambda: activity(api.get(f"/users/{username}/events/public?per_page=100"), username))
    if api.token:
        query = "query($login:String!){user(login:$login){contributionsCollection{startedAt endedAt contributionCalendar{totalContributions weeks{contributionDays{date contributionCount contributionLevel}}}}}}"
        attempt("contributions", lambda: contributions(api.get("/graphql", {"query": query, "variables": {"login": username}})))
    # The shared date is displayed beside public activity. Never label a retained
    # public section as freshly retrieved; optional calendar failure is separate.
    if succeeded and not {"repositories", "releases", "activity"}.intersection(failures):
        result["updated_at"] = now or datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    return result, failures


def atomic_write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent, delete=False, newline="\n") as handle:
            temp = Path(handle.name)
            json.dump(data, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp, path)
    finally:
        if temp and temp.exists():
            temp.unlink()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=ROOT / "profile.config.json")
    parser.add_argument("--output", type=Path, default=ROOT / "data/activity.json")
    parser.add_argument("--offline", action="store_true", help="Validate existing data without network or writes")
    args = parser.parse_args()
    try:
        config = json.loads(args.config.read_text(encoding="utf-8"))
        if not USER.fullmatch(config.get("username", "")):
            raise DataError("Invalid configured username")
        repos = config.get("featured_repos", [])
        if not isinstance(repos, list) or len(repos) > 12 or any(not isinstance(repo, str) or not REPO.fullmatch(repo) for repo in repos):
            raise DataError("Invalid featured_repos; expected at most 12 owner/repo names")
        previous = json.loads(args.output.read_text(encoding="utf-8")) if args.output.exists() else empty_snapshot(config["username"])
        validate_snapshot(previous, config["username"])
        if args.offline:
            if not args.output.exists():
                raise DataError("Offline snapshot does not exist")
            print("Profile snapshot validated offline.")
            return 0
        result, failures = refresh(config, previous, GitHub(os.environ.get("GITHUB_TOKEN")))
        if result != previous:
            atomic_write(args.output, result)
        for section in failures:
            print(f"Warning: {section} unavailable; retained last successful data.", file=sys.stderr)
        if not args.output.exists():
            raise DataError("No snapshot available; retry when GitHub is reachable")
        print("Profile refresh completed.")
        return 0
    except (DataError, ValueError, OSError, TypeError, KeyError):
        print("Profile update failed: check configuration and snapshot structure. Existing data was not replaced.", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
