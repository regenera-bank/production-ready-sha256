from subprocess import CompletedProcess
from unittest.mock import patch
from common import TempCase
from regenera_tools.executor import SafeExecutor, CommandRequest
from regenera_tools.errors import ExecutionDenied, SecurityError

class ExecutorTest(TempCase):
    def ex(self):
        return SafeExecutor(self.root, {"python3"}, {"SAFE_FLAG"})

    def completed(self, code=0, out="ok\n", err=""):
        return CompletedProcess(["python3"], code, out, err)

    def test_allowed(self):
        with patch("regenera_tools.executor.subprocess.run", return_value=self.completed()) as run:
            result = self.ex().run(CommandRequest(("python3", "-c", "print('ok')"), dry_run=False))
        self.assertEqual(result.stdout, "ok\n")
        self.assertTrue(result.executed)
        run.assert_called_once()

    def test_denied_executable(self):
        self.assertRaises(ExecutionDenied, self.ex().run, CommandRequest(("sh", "-c", "true"), dry_run=False))

    def test_empty(self):
        self.assertRaises(ExecutionDenied, self.ex().run, CommandRequest(tuple(), dry_run=False))

    def test_timeout_low(self):
        self.assertRaises(ExecutionDenied, self.ex().run, CommandRequest(("python3", "-V"), timeout_seconds=0, dry_run=False))

    def test_timeout_high(self):
        self.assertRaises(ExecutionDenied, self.ex().run, CommandRequest(("python3", "-V"), timeout_seconds=301, dry_run=False))

    def test_mutating_no_approval_is_dry(self):
        self.assertFalse(self.ex().run(CommandRequest(("python3", "-V"), mutating=True, dry_run=False)).executed)

    def test_mutating_dry_run(self):
        self.assertFalse(self.ex().run(CommandRequest(("python3", "-V"), mutating=True, approved=True, dry_run=True)).executed)

    def test_mutating_approved(self):
        with patch("regenera_tools.executor.subprocess.run", return_value=self.completed()):
            self.assertTrue(self.ex().run(CommandRequest(("python3", "-c", "print(1)"), mutating=True, approved=True, dry_run=False)).executed)

    def test_env_denied(self):
        self.assertRaises(ExecutionDenied, self.ex().run, CommandRequest(("python3", "-V"), env=(("BAD", "x"),), dry_run=False))

    def test_env_allowed(self):
        with patch("regenera_tools.executor.subprocess.run", return_value=self.completed()):
            self.assertTrue(self.ex().run(CommandRequest(("python3", "-c", "print('x')"), env=(("SAFE_FLAG", "1"),), dry_run=False)).executed)

    def test_cwd(self):
        (self.root / "sub").mkdir()
        with patch("regenera_tools.executor.subprocess.run", return_value=self.completed(out="sub\n")) as run:
            result = self.ex().run(CommandRequest(("python3", "-c", "print('sub')"), cwd="sub", dry_run=False))
        self.assertEqual(result.stdout.strip(), "sub")
        self.assertEqual(run.call_args.kwargs["cwd"], self.root / "sub")

    def test_cwd_escape(self):
        self.assertRaises(SecurityError, self.ex().run, CommandRequest(("python3", "-V"), cwd="../x", dry_run=False))

    def test_returncode(self):
        with patch("regenera_tools.executor.subprocess.run", return_value=self.completed(code=7)):
            self.assertEqual(self.ex().run(CommandRequest(("python3", "-c", "raise SystemExit(7)"), dry_run=False)).returncode, 7)
