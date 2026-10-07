import json
import tempfile
import unittest
from pathlib import Path
from http.cookies import SimpleCookie

from fastapi import HTTPException, Response

from src import app as activities_app


class AdminAuthTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.original_teachers_file = activities_app.TEACHERS_FILE
        self.original_participants = list(activities_app.activities["Chess Club"]["participants"])
        activities_app._teacher_sessions.clear()

        salt, password_hash = activities_app.create_password_hash("teacher-secret")
        self.teachers_file = Path(self.temp_dir.name) / "teachers.json"
        self.teachers_file.write_text(
            json.dumps({
                "teachers": [{
                    "username": "teacher@example.edu",
                    "salt": salt,
                    "password_hash": password_hash,
                }]
            }),
            encoding="utf-8",
        )
        activities_app.TEACHERS_FILE = self.teachers_file

    def tearDown(self):
        activities_app.TEACHERS_FILE = self.original_teachers_file
        activities_app.activities["Chess Club"]["participants"] = self.original_participants
        activities_app._teacher_sessions.clear()
        self.temp_dir.cleanup()

    def test_activity_list_is_public_but_changes_require_teacher_login(self):
        self.assertIn("Chess Club", activities_app.get_activities())
        with self.assertRaises(HTTPException) as error:
            activities_app.require_teacher(None)
        self.assertEqual(error.exception.status_code, 401)

        protected_routes = {
            (route.path, method): route
            for route in activities_app.app.routes
            if hasattr(route, "dependant")
            for method in route.methods or []
        }
        for path, method in (
            ("/activities/{activity_name}/signup", "POST"),
            ("/activities/{activity_name}/unregister", "DELETE"),
        ):
            dependencies = protected_routes[(path, method)].dependant.dependencies
            self.assertIn(activities_app.require_teacher, [item.call for item in dependencies])

    def test_teacher_can_sign_in_and_change_registrations(self):
        response = Response()
        result = activities_app.teacher_login(
            activities_app.TeacherCredentials(
                username="teacher@example.edu",
                password="teacher-secret",
            ),
            response,
        )
        self.assertTrue(result["authenticated"])
        cookie = SimpleCookie()
        cookie.load(response.headers["set-cookie"])
        token = cookie[activities_app.SESSION_COOKIE].value
        self.assertEqual(activities_app.require_teacher(token), "teacher@example.edu")

        signup = activities_app.signup_for_activity(
            "Chess Club",
            "new-student@example.edu",
            "teacher@example.edu",
        )
        self.assertIn("Signed up", signup["message"])

        unregister = activities_app.unregister_from_activity(
            "Chess Club",
            "new-student@example.edu",
            "teacher@example.edu",
        )
        self.assertIn("Unregistered", unregister["message"])

        logout_response = Response()
        logout = activities_app.teacher_logout(logout_response, token)
        self.assertFalse(logout["authenticated"])
        with self.assertRaises(HTTPException) as error:
            activities_app.require_teacher(token)
        self.assertEqual(error.exception.status_code, 401)

    def test_invalid_teacher_credentials_are_rejected(self):
        with self.assertRaises(HTTPException) as error:
            activities_app.teacher_login(
                activities_app.TeacherCredentials(
                    username="teacher@example.edu",
                    password="wrong-password",
                ),
                Response(),
            )
        self.assertEqual(error.exception.status_code, 401)


if __name__ == "__main__":
    unittest.main()