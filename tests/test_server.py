import json
import threading
import unittest
from http.server import ThreadingHTTPServer
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from triager_app.server import TriagerHandler


class ServerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), TriagerHandler)
        cls.base_url = f"http://127.0.0.1:{cls.server.server_port}"
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join(timeout=2)

    def test_manifest_points_to_openapi_document(self):
        with urlopen(f"{self.base_url}/.well-known/ai-plugin.json", timeout=5) as response:
            manifest = json.loads(response.read().decode("utf-8"))

        self.assertEqual(manifest["name_for_model"], "issue_triager")
        self.assertEqual(manifest["api"]["url"], f"{self.base_url}/openapi.yaml")

    def test_triage_endpoint_returns_suggestions(self):
        request = Request(
            f"{self.base_url}/triage",
            data=json.dumps({"title": "Crash during setup", "body": "Install fails with an error"}).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        with urlopen(request, timeout=5) as response:
            result = json.loads(response.read().decode("utf-8"))

        self.assertIn("bug", result["labels"])
        self.assertIn("setup", result["labels"])
        self.assertEqual(result["priority"], "medium")

    def test_triage_endpoint_requires_title(self):
        request = Request(
            f"{self.base_url}/triage",
            data=json.dumps({"body": "No title"}).encode("utf-8"),
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        with self.assertRaises(HTTPError) as context:
            urlopen(request, timeout=5)

        self.assertEqual(context.exception.code, 400)


if __name__ == "__main__":
    unittest.main()
