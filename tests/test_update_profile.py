import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

SPEC = importlib.util.spec_from_file_location("update_profile", Path(__file__).resolve().parents[1] / "scripts/update_profile.py")
updater = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(updater)


def repo_fixture():
    return {"private": False, "full_name": "user/project", "name": "project", "description": None, "html_url": "https://github.com/user/project", "homepage": None, "language": "Python", "stargazers_count": 2, "forks_count": 0, "updated_at": "2026-09-01T00:00:00Z", "pushed_at": "2026-09-01T00:00:00Z", "archived": False, "fork": False}


class FakeAPI:
    token = None

    def __init__(self, responses):
        self.responses = responses

    def get(self, path, body=None):
        response = self.responses.get(path, OSError("unavailable"))
        if isinstance(response, Exception):
            raise response
        return copy.deepcopy(response)


class ProfileUpdateTests(unittest.TestCase):
    def setUp(self):
        self.config = {"username": "user", "featured_repos": ["user/project"]}
        self.previous = updater.empty_snapshot("user")
        self.previous["updated_at"] = "2026-08-01T00:00:00Z"
        self.previous["repositories"] = [updater.repository(repo_fixture(), "user/project")]

    def test_total_outage_preserves_snapshot_and_timestamp(self):
        result, failures = updater.refresh(self.config, self.previous, FakeAPI({}))
        self.assertEqual(result, self.previous)
        self.assertEqual(set(failures), {"repositories", "releases", "activity"})

    def test_one_failure_does_not_erase_good_section(self):
        api = FakeAPI({"/users/user/events/public?per_page=100": []})
        result, failures = updater.refresh(self.config, self.previous, api, now="2026-09-01T00:00:00Z")
        self.assertEqual(result["repositories"], self.previous["repositories"])
        self.assertEqual(result["activity"], [])
        self.assertEqual(result["updated_at"], self.previous["updated_at"])
        self.assertIn("repositories", failures)

    def test_private_or_malformed_repository_rejected(self):
        for overrides in ({"private": True}, {"stargazers_count": "2"}, {"full_name": "other/project"}, {"html_url": "https://evil.example/"}):
            raw = repo_fixture() | overrides
            with self.subTest(overrides=overrides), self.assertRaises(updater.DataError):
                updater.repository(raw, "user/project")

    def test_missing_and_malformed_responses_keep_last_good(self):
        for malformed in ({"message": "rate limited"}, None, [None]):
            api = FakeAPI({"/users/user/repos?type=owner&per_page=100&sort=updated&page=1": malformed, "/repos/user/project": malformed, "/users/user/events/public?per_page=100": malformed})
            result, failures = updater.refresh(self.config, self.previous, api)
            self.assertEqual(result, self.previous)
            self.assertEqual(len(failures), 3)

    def test_all_owned_repositories_are_included(self):
        second = repo_fixture() | {"full_name": "user/another", "name": "another", "html_url": "https://github.com/user/another"}
        api = FakeAPI({"/users/user/repos?type=owner&per_page=100&sort=updated&page=1": [repo_fixture(), second]})
        result, failures = updater.refresh(self.config, self.previous, api)
        self.assertEqual(len(result["repositories"]), 2)
        self.assertNotIn("repositories", failures)

    def test_fully_successful_public_refresh_advances_timestamp(self):
        api = FakeAPI({"/users/user/repos?type=owner&per_page=100&sort=updated&page=1": [repo_fixture()], "/repos/user/project": repo_fixture(), "/repos/user/project/releases?per_page=3": [], "/users/user/events/public?per_page=100": []})
        result, failures = updater.refresh(self.config, self.previous, api, now="2026-09-01T00:00:00Z")
        self.assertEqual(failures, [])
        self.assertEqual(result["updated_at"], "2026-09-01T00:00:00Z")

    def test_invalid_remote_date_keeps_previous_repository_section(self):
        raw = repo_fixture() | {"updated_at": "2026-02-31T00:00:00Z"}
        api = FakeAPI({"/users/user/repos?type=owner&per_page=100&sort=updated&page=1": [raw]})
        result, failures = updater.refresh(self.config, self.previous, api)
        self.assertEqual(result, self.previous)
        self.assertIn("repositories", failures)

    def test_pagination_failure_preserves_complete_previous_list(self):
        api = FakeAPI({"/users/user/repos?type=owner&per_page=100&sort=updated&page=1": [repo_fixture()] * 100})
        result, failures = updater.refresh(self.config, self.previous, api)
        self.assertEqual(result, self.previous)
        self.assertIn("repositories", failures)

    def test_activity_filters_private_bots_profile_push_and_duplicates(self):
        base = {"public": True, "actor": {"login": "user"}, "repo": {"name": "user/project"}, "type": "PushEvent", "payload": {}, "created_at": "2026-09-01T00:00:00Z"}
        events = [base, base, base | {"public": False}, base | {"actor": {"login": "github-actions[bot]"}}, base | {"repo": {"name": "user/user"}}]
        result = updater.activity(events, "user")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0]["repo"], "user/project")

    def test_release_drafts_are_excluded(self):
        public = {"draft": False, "name": None, "tag_name": "v1", "html_url": "https://github.com/user/project/releases/tag/v1", "published_at": "2026-09-01T00:00:00Z"}
        self.assertEqual(len(updater.releases([public, public | {"draft": True}], "user/project")), 1)

    def test_graphql_failure_keeps_calendar(self):
        self.previous["contributions"] = {"total": 5, "from": "2026-08-01", "to": "2026-08-01", "weeks": [{"days": [{"date": "2026-08-01", "count": 5, "level": 4}]}]}
        api = FakeAPI({"/graphql": {"errors": [{"message": "forbidden"}]}})
        api.token = "test-token"
        result, failures = updater.refresh(self.config, self.previous, api)
        self.assertEqual(result["contributions"], self.previous["contributions"])
        self.assertIn("contributions", failures)

    def test_calendar_levels_are_normalized(self):
        raw = {"data": {"user": {"contributionsCollection": {"startedAt": "2026-08-01", "endedAt": "2026-08-01", "contributionCalendar": {"totalContributions": 2, "weeks": [{"contributionDays": [{"date": "2026-08-01", "contributionCount": 2, "contributionLevel": "SECOND_QUARTILE"}]}]}}}}}
        self.assertEqual(updater.contributions(raw)["weeks"][0]["days"][0]["level"], 2)

    def test_unknown_calendar_is_not_zero(self):
        self.assertIsNone(updater.empty_snapshot("user")["contributions"]["total"])

    def test_snapshot_identity_mismatch_rejected(self):
        with self.assertRaises(updater.DataError):
            updater.validate_snapshot(self.previous, "another-user")

    def test_malformed_nested_snapshot_rejected(self):
        snapshot = copy.deepcopy(self.previous)
        snapshot["repositories"][0]["stargazers_count"] = "not a number"
        with self.assertRaises(updater.DataError):
            updater.validate_snapshot(snapshot, "user")

    def test_malformed_graphql_response_preserves_last_good(self):
        api = FakeAPI({"/graphql": None})
        api.token = "test-token"
        result, failures = updater.refresh(self.config, self.previous, api)
        self.assertEqual(result, self.previous)
        self.assertIn("contributions", failures)

    def test_atomic_write_round_trip(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "data.json"
            updater.atomic_write(path, self.previous)
            self.assertEqual(json.loads(path.read_text(encoding="utf-8")), self.previous)
            self.assertEqual(list(Path(directory).iterdir()), [path])


if __name__ == "__main__":
    unittest.main()
