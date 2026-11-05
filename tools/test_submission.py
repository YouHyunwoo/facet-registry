import json
import tempfile
import unittest
import zipfile
from pathlib import Path

from submission import ATTACHMENT, Rejected, add_to_index, inspect

SKIN = {"id": "sample", "name": "Aurora", "version": "1.0.0", "colors": {"Bg": "#102030"}}
PLUGIN = {"id": "my.plugin", "name": "Mine", "version": "1.0.0", "assembly": "My.dll"}


class Inspect(unittest.TestCase):
    def package(self, files):
        folder = tempfile.mkdtemp()
        path = Path(folder) / "p.zip"
        with zipfile.ZipFile(path, "w") as package:
            for name, content in files.items():
                package.writestr(name, content if isinstance(content, str) else json.dumps(content))
        return path

    def refused(self, files):
        with self.assertRaises(Rejected):
            inspect(self.package(files))

    def test_valid(self):
        self.assertEqual(inspect(self.package({"skin.json": SKIN}))[0], "skin")
        self.assertEqual(inspect(self.package({"plugin.json": PLUGIN, "My.dll": "x"}))[0], "plugin")

    def test_paths(self):
        for bad in ("../x.txt", "con.txt", "a:b.txt", "/x.txt", "a/../../x.txt"):
            self.refused({"skin.json": SKIN, bad: "x"})

    def test_manifests(self):
        self.refused({"readme.txt": "x"})
        self.refused({"skin.json": SKIN, "plugin.json": PLUGIN, "My.dll": "x"})
        self.refused({"skin.json": "not json"})
        self.refused({"skin.json": {**SKIN, "id": "../a"}})
        self.refused({"skin.json": {**SKIN, "id": "space"}})
        self.refused({"skin.json": {**SKIN, "version": "a/b"}})
        self.refused({"plugin.json": PLUGIN})

    def test_skin_is_data(self):
        self.refused({"skin.json": SKIN, "run.dll": "x"})
        self.refused({"skin.json": {**SKIN, "colors": {"Nope": "#102030"}}})
        self.refused({"skin.json": {**SKIN, "colors": {"Bg": "red"}}})
        self.refused({"skin.json": {**SKIN, "theme": {"background": "../x.png"}}})
        self.refused({"skin.json": {**SKIN, "theme": {"background": "gone.png"}}})
        self.assertEqual(inspect(self.package({"skin.json": {**SKIN, "theme": {"background": "b.png"}}, "b.png": "x"}))[0], "skin")


class Index(unittest.TestCase):
    def test_ownership_and_versions(self):
        index = {"packages": []}
        self.assertEqual(add_to_index(index, "skin", SKIN, "ann", "o/r", "a" * 64), "skin-sample-1.0.0")
        self.assertEqual(index["packages"][0]["url"], "https://github.com/o/r/releases/download/skin-sample-1.0.0/sample-1.0.0.zip")
        with self.assertRaises(Rejected):
            add_to_index(index, "skin", {**SKIN, "version": "2.0.0"}, "eve", "o/r", "b" * 64)
        with self.assertRaises(Rejected):
            add_to_index(index, "skin", SKIN, "ann", "o/r", "b" * 64)
        add_to_index(index, "skin", {**SKIN, "version": "2.0.0"}, "ann", "o/r", "b" * 64)
        self.assertEqual([row["version"] for row in index["packages"]], ["2.0.0"])


class Attachment(unittest.TestCase):
    def test_only_github_attachments(self):
        self.assertTrue(ATTACHMENT.findall("see https://github.com/user-attachments/files/123/a-1.0.zip now"))
        self.assertFalse(ATTACHMENT.findall("https://evil.example/files/123/a.zip"))


if __name__ == "__main__":
    unittest.main()
