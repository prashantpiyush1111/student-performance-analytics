import os
import subprocess
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]


class SecretKeyConfigurationTests(unittest.TestCase):
    def test_config_does_not_define_predictable_fallback(self):
        env = os.environ.copy()
        env.pop("SECRET_KEY", None)

        result = subprocess.run(
            [
                sys.executable,
                "-c",
                "from config import Config; assert Config.SECRET_KEY is None",
            ],
            cwd=REPO_ROOT,
            env=env,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0, result.stderr)

    def test_application_refuses_to_start_without_secret_key(self):
        env = os.environ.copy()
        env.pop("SECRET_KEY", None)

        result = subprocess.run(
            [sys.executable, "-c", "import app"],
            cwd=REPO_ROOT,
            env=env,
            capture_output=True,
            text=True,
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn(
            "SECRET_KEY environment variable must be set",
            result.stderr,
        )

    def test_application_starts_with_explicit_secret_key(self):
        env = os.environ.copy()
        env["SECRET_KEY"] = "test-only-secret-key"

        result = subprocess.run(
            [
                sys.executable,
                "-c",
                "import app; assert app.app.config['SECRET_KEY'] == 'test-only-secret-key'",
            ],
            cwd=REPO_ROOT,
            env=env,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == "__main__":
    unittest.main()
