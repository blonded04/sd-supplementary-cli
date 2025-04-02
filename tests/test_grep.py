import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

import unittest
import tempfile
from process_manager import ProcessManager
from command import Command, CommandType, CommandFactory
from environment_manager import EnvironmentManager

class TestGrepCommand(unittest.TestCase):
    def setUp(self):
        self.env = EnvironmentManager()
        self.process_manager = ProcessManager(self.env)
        
        self.temp_file = tempfile.NamedTemporaryFile(mode='w+', delete=False)
        self.temp_file.write("""Hello World
Test line
Another TEST
Line with numbers 123
Special_chars: !@#
Unicode: Привет Мір
""")
        self.temp_file.close()

    def tearDown(self):
        os.unlink(self.temp_file.name)

    def _run_grep(self, args, stdin_data=None):
        cmd = CommandFactory.create(
            CommandType.BUILTIN,
            'grep',
            args
        )
        return self.process_manager.execute_capture(cmd, stdin_data)

    def test_basic_pattern(self):
        stdout, stderr, code = self._run_grep(['Hello', self.temp_file.name])
        self.assertEqual(stdout.strip(), "Hello World")
        self.assertEqual(code, 0)

    def test_case_insensitive(self):
        stdout, stderr, code = self._run_grep(['-i', 'test', self.temp_file.name])
        self.assertIn("Test line", stdout)
        self.assertIn("Another TEST", stdout)

    def test_word_boundary(self):
        stdout, stderr, code = self._run_grep(['-w', 'Test', self.temp_file.name])
        self.assertIn("Test line", stdout)
        self.assertNotIn("Another TEST", stdout)

    def test_after_context(self):
        stdout, stderr, code = self._run_grep(['-A', '1', 'numbers', self.temp_file.name])
        output = stdout.split('\n')
        self.assertIn("Line with numbers 123", output)
        self.assertIn("Special_chars: !@#", output)
        self.assertEqual(len(output), 2)

    def test_overlapping_context(self):
        stdout, stderr, code = self._run_grep(['-A', '2', 'Test', self.temp_file.name])
        output = stdout.split('\n')
        self.assertEqual(len(output), 3)  # Test line + 2 following
        self.assertIn("Another TEST", output)

    def test_regex_special_chars(self):
        stdout, stderr, code = self._run_grep(['^Special', self.temp_file.name])
        self.assertIn("Special_chars: !@#", stdout)

    def test_unicode_support(self):
        stdout, stderr, code = self._run_grep(['-i', 'привет', self.temp_file.name])
        self.assertIn("Unicode: Привет Мір", stdout)

    def test_invalid_argument(self):
        stdout, stderr, code = self._run_grep(['-Z', 'test', self.temp_file.name])
        self.assertIn("Invalid option", stderr)
        self.assertEqual(code, 1)

    def test_missing_file(self):
        stdout, stderr, code = self._run_grep(['test', 'nonexistent.txt'])
        self.assertIn("No such file", stderr)

    def test_stdin_input(self):
        stdin_data = """First line
        Second line
        Third line"""
        stdout, stderr, code = self._run_grep(['Second'], stdin_data=stdin_data)
        self.assertIn("Second line", stdout)

    def test_invalid_regex(self):
        stdout, stderr, code = self._run_grep(['*invalid', self.temp_file.name])
        self.assertIn("invalid regex", stderr.lower())

    def test_negative_context(self):
        stdout, stderr, code = self._run_grep(['-A', '-5', 'test', self.temp_file.name])
        self.assertIn("invalid number", stderr.lower())

if __name__ == '__main__':
    unittest.main()
