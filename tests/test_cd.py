import sys
import os
import shutil
import tempfile
import unittest
from unittest.mock import patch
from io import StringIO

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

from command_parser import CommandParser
from process_manager import ProcessManager
from environment_manager import EnvironmentManager


class TestCd(unittest.TestCase):
    def setUp(self):
        self.env = EnvironmentManager()
        self.process_manager = ProcessManager(self.env)
        self.parser = CommandParser(self.env, self.process_manager)
        self.original_dir = os.getcwd()
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        os.chdir(self.original_dir)
        shutil.rmtree(self.temp_dir)

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

    def test_cd_no_args_goes_to_home(self):
        home = os.path.expanduser("~")

        _, _, code = self.execute_command('cd')

        self.assertEqual(os.getcwd(), home)
        self.assertEqual(code, 0)

    def test_cd_with_valid_directory(self):
        test_dir = os.path.join(self.temp_dir, "testdir")
        os.mkdir(test_dir)

        _, _, code = self.execute_command(f'cd {test_dir}')

        actual_path = os.path.realpath(os.getcwd())
        expected_path = os.path.realpath(test_dir)
        self.assertEqual(actual_path, expected_path)
        self.assertEqual(code, 0)
        self.assertEqual(os.path.realpath(self.env.get("PWD")), expected_path)

    def test_cd_with_nonexistent_path(self):
        non_existent = os.path.join(self.temp_dir, "nonexist")

        _, stderr, code = self.execute_command(f'cd {non_existent}')

        self.assertIn("No such file or directory", stderr)
        self.assertEqual(code, 1)
        self.assertEqual(os.getcwd(), self.original_dir)

    def test_cd_too_many_args(self):
        _, stderr, code = self.execute_command('cd dir1 dir2')

        self.assertEqual(code, 1)


if __name__ == '__main__':
    unittest.main()