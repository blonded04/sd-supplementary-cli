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

class TestLs(unittest.TestCase):
    def setUp(self):
        self.env = EnvironmentManager()
        self.process_manager = ProcessManager(self.env)
        self.parser = CommandParser(self.env, self.process_manager)
        self.temp_dir = tempfile.mkdtemp()

        self.file1 = os.path.join(self.temp_dir, "test_ls.py")
        with open(self.file1, 'w') as f:
            f.write("test")

        self.subdir = os.path.join(self.temp_dir, "subdir")
        os.mkdir(self.subdir)

    def tearDown(self):
        os.remove(self.file1)
        os.rmdir(self.subdir)
        os.rmdir(self.temp_dir)

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

    def test_ls_no_args(self):
        stdout, _, code = self.execute_command('ls')

        output_lines = stdout.split('\n')

        self.assertIn("test_ls.py", output_lines)
        self.assertEqual(code, 0)

    def test_ls_with_directory_arg(self):
        stdout, _, code = self.execute_command(f'ls {self.subdir}')

        self.assertEqual(stdout, "")
        self.assertEqual(code, 0)

    def test_ls_with_nonexistent_dir(self):
        non_existent = os.path.join(self.temp_dir, "nonexistent")

        _, stderr, code = self.execute_command(f'ls {non_existent}')

        self.assertIn("No such file or directory", stderr)
        self.assertEqual(code, 1)

    def test_ls_too_many_args(self):
        _, stderr, code = self.execute_command('ls dir1 dir2')

        self.assertEqual(code, 1)

if __name__ == '__main__':
    unittest.main()