import unittest

from triager_app import triage_issue


class TriageIssueTests(unittest.TestCase):
    def test_bug_with_security_keywords_is_high_priority_security(self):
        result = triage_issue("Token leak causes crash", "A secret token appears in logs after an exception.")

        self.assertIn("bug", result["labels"])
        self.assertIn("security", result["labels"])
        self.assertEqual(result["priority"], "high")
        self.assertEqual(result["type"], "security")

    def test_feature_request_is_low_priority_feature(self):
        result = triage_issue("Feature request: add CSV export", "Users would like export support.")

        self.assertIn("enhancement", result["labels"])
        self.assertEqual(result["priority"], "low")
        self.assertEqual(result["type"], "feature")

    def test_unclear_issue_gets_needs_triage_label(self):
        result = triage_issue("Something unexpected happened")

        self.assertEqual(result["labels"], ["needs-triage"])
        self.assertEqual(result["type"], "task")


if __name__ == "__main__":
    unittest.main()
