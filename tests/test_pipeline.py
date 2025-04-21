import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

import unittest
import tempfile
from command_parser import CommandParser
from process_manager import ProcessManager
from environment_manager import EnvironmentManager
from unittest.mock import patch
from io import StringIO

class TestPipeline(unittest.TestCase):
    def setUp(self):
        self.env = EnvironmentManager()
        self.process_manager = ProcessManager(self.env)
        self.parser = CommandParser(self.env, self.process_manager)

    def execute_command(self, command_line):
        command = self.parser.parse(command_line)
        with patch('sys.stdout', new=StringIO()) as fake_out, \
             patch('sys.stderr', new=StringIO()) as fake_err:
            exit_code = self.process_manager.execute(command)
            return (
                fake_out.getvalue().strip(),
                fake_err.getvalue().strip(),
                exit_code
            )

    def test_simple_pipe(self):
        stdout, _, code = self.execute_command('echo "hello world" | wc')
        self.assertEqual(stdout, "1 2 12")
        self.assertEqual(code, 0)

    def test_chained_pipes(self):
        stdout, _, _ = self.execute_command('echo "A\nB\nC" | grep A | wc')
        self.assertEqual(stdout, "1 1 2")

    def test_error_in_pipeline(self):
        stdout, stderr, code = self.execute_command('cat missing.txt | echo ok')
        self.assertEqual(stdout, "ok")
        self.assertIn("Errno", stderr)
        self.assertNotEqual(code, 0)

    def test_pipe_with_external_commands(self):
        with tempfile.NamedTemporaryFile(mode='w+') as f:
            f.write("line1\nline2\n")
            f.flush()
            stdout, _, _ = self.execute_command(f'cat {f.name} | grep line2')
            self.assertEqual(stdout, "line2")


if __name__ == '__main__':
    unittest.main()
