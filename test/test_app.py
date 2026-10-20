
"""Automated security tests for the LLM Security Defense Lab."""

import unittest

from app.app import User, authorize, execute_mock_tool, validate_input


class TestAuthorization(unittest.TestCase):

    def test_analyst_cannot_view_restricted_records(self):
        user = User(user_id="test-analyst", role="analyst")

        result = execute_mock_tool(user, "view_restricted_record")

        self.assertIn("BLOCKED", result)

    def test_support_cannot_view_restricted_records(self):
        user = User(user_id="test-support", role="support")

        result = execute_mock_tool(user, "view_restricted_record")

        self.assertIn("BLOCKED", result)

    def test_admin_can_view_restricted_records(self):
        user = User(user_id="test-admin", role="admin")

        result = execute_mock_tool(user, "view_restricted_record")

        self.assertIn("C002", result)
        self.assertIn("Bola Sample", result)

    def test_analyst_can_generate_demo_report(self):
        user = User(user_id="test-analyst", role="analyst")

        result = execute_mock_tool(user, "generate_demo_report")

        self.assertIn("3 synthetic records", result)

    def test_unknown_tool_is_blocked(self):
        user = User(user_id="test-admin", role="admin")

        result = execute_mock_tool(user, "delete_customer_database")

        self.assertIn("BLOCKED", result)

    def test_authorization_rejects_unknown_tool(self):
        user = User(user_id="test-admin", role="admin")

        self.assertFalse(authorize(user, "unknown_tool"))


class TestInputValidation(unittest.TestCase):

    def test_empty_input_is_rejected(self):
        with self.assertRaises(ValueError):
            validate_input("   ")

    def test_input_over_200_characters_is_rejected(self):
        with self.assertRaises(ValueError):
            validate_input("A" * 201)

    def test_valid_input_is_trimmed(self):
        self.assertEqual(validate_input("  hello  "), "hello")


if __name__ == "__main__":
    unittest.main()
