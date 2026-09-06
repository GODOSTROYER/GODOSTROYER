"""Behavior checks for truthful counts, safe links, responsive assets and drift."""
import copy
from html.parser import HTMLParser
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import render_profile as renderer
import update_profile as updater

SVG = "{http://www.w3.org/2000/svg}"


class MarkupAudit(HTMLParser):
    def __init__(self):
        super().__init__()
        self.unsafe = []

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "iframe", "object"):
            self.unsafe.append(tag)
        for key, value in attrs:
            if key.startswith("on") or (key in ("href", "src") and value.lower().startswith("javascript:")):
                self.unsafe.append((key, value))


class RendererTests(unittest.TestCase):
    def setUp(self):
        self.config = json.loads((ROOT / "profile.config.json").read_text(encoding="utf-8"))
        self.snapshot = updater.empty_snapshot(self.config["username"])

    def test_work_map_counts_only_active_original_public_projects(self):
        username = self.config["username"]
        self.snapshot["repositories"] = [
            {"name": "one", "language": "Python", "fork": False, "archived": False},
            {"name": "two", "language": "Python", "fork": False, "archived": False},
            {"name": "three", "language": None, "fork": False, "archived": False},
            {"name": "fork", "language": "Python", "fork": True, "archived": False},
            {"name": "old", "language": "Python", "fork": False, "archived": True},
            {"name": username.lower(), "language": "Python", "fork": False, "archived": False},
        ]
        for mobile in (False, True):
            svg = ET.fromstring(renderer.work_map(self.snapshot, "light", mobile))
            self.assertEqual(len(svg.findall(f"{SVG}circle")), 3)
            accessible = svg.find(f"{SVG}desc").text
            self.assertIn("Python: 2", accessible)
            self.assertIn("Other: 1", accessible)

    def test_unknown_contributions_render_without_inventing_counts(self):
        outputs = renderer.render_all(self.config, self.snapshot)
        readme = outputs[ROOT / "README.md"]
        self.assertNotIn("0 contributions", readme.lower())
        self.assertNotIn("streak", readme.lower())
        self.assertNotIn("Last refreshed", readme)
        self.assertIsNone(self.snapshot["contributions"]["total"])

    def test_unsafe_links_are_rejected(self):
        for value in ("javascript:alert(1)", "data:text/html,evil", "http://example.com", "//example.com", "https://secret:token@example.com"):
            with self.subTest(value=value), self.assertRaises(ValueError):
                renderer.link("Open", value)

    def test_untrusted_text_and_url_quotes_cannot_inject_markup(self):
        malicious = '\"><script>alert(1)</script><img src=x onerror="alert(1)"> & test'
        config = copy.deepcopy(self.config)
        project = config["projects"][0]
        for key in ("title", "subtitle", "description", "alt", "note"):
            project[key] = malicious
        project["stack"] = [malicious]
        project["demo_url"] = 'https://example.com/?q=" onmouseover="alert(1)'
        result = renderer.render_readme(config, self.snapshot)
        parser = MarkupAudit()
        parser.feed(result)
        self.assertEqual(parser.unsafe, [])
        self.assertIn("&lt;script&gt;", result)
        self.assertIn("&quot;", result)

    def test_language_labels_remain_xml_text(self):
        self.snapshot["repositories"] = [{"name": "safe", "language": '<script>alert("x")</script> & language', "fork": False, "archived": False}]
        result = ET.fromstring(renderer.work_map(self.snapshot, "dark"))
        self.assertEqual(result.findall(f".//{SVG}script"), [])
        self.assertIn('<script>alert("x")</script>', result.find(f"{SVG}desc").text)

    def test_mobile_and_theme_variants_are_real_self_contained_assets(self):
        outputs = renderer.render_all(self.config, self.snapshot)
        for stem in ("hero", "work-map"):
            for theme in ("dark", "light"):
                desktop = ROOT / f"assets/generated/{stem}-{theme}.svg"
                mobile = ROOT / f"assets/generated/{stem}-mobile-{theme}.svg"
                self.assertIn(mobile, outputs)
                mobile_svg = ET.fromstring(outputs[mobile])
                desktop_svg = ET.fromstring(outputs[desktop])
                self.assertLess(float(mobile_svg.attrib["width"]), float(desktop_svg.attrib["width"]))
                for element in mobile_svg.iter():
                    self.assertNotIn(element.tag, (SVG + "script", SVG + "foreignObject"))
                    for attribute, value in element.attrib.items():
                        if attribute.endswith("href"):
                            self.assertTrue(value.startswith("#"), "SVG must not fetch external dependencies")
        readme = outputs[ROOT / "README.md"]
        self.assertIn("hero-mobile-dark.svg", readme)
        self.assertIn("hero-mobile-light.svg", readme)

    def test_check_mode_reports_drift_without_rewriting_files(self):
        with tempfile.TemporaryDirectory() as directory:
            temporary = Path(directory)
            (temporary / "data").mkdir()
            (temporary / "profile.config.json").write_text("{}", encoding="utf-8")
            (temporary / "data/activity.json").write_text("{}", encoding="utf-8")
            target = temporary / "README.md"
            target.write_text("hand edited", encoding="utf-8")
            with patch.object(renderer, "ROOT", temporary), patch.object(renderer, "render_all", return_value={target: "generated"}), patch.object(sys, "argv", ["render_profile.py", "--check"]):
                self.assertEqual(renderer.main(), 1)
            self.assertEqual(target.read_text(encoding="utf-8"), "hand edited")


if __name__ == "__main__":
    unittest.main()
