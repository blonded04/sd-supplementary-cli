import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

import unittest
from command_parser import CommandParser
from process_manager import ProcessManager
from environment_manager import EnvironmentManager
from unittest.mock import patch
from io import StringIO

class TestEnvironment(unittest.TestCase):
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

    def test_var_assignment(self):
        _, _, code = self.execute_command('MY_VAR=test_value')
        self.assertEqual(code, 0)
        self.assertEqual(self.env.get("MY_VAR"), "test_value")

    def test_var_usage_in_echo(self):
        self.execute_command('MY_VAR=hello')
        stdout, _, _ = self.execute_command('echo $MY_VAR')
        self.assertEqual(stdout, "hello")

    def test_quoted_var_expansion(self):
        self.execute_command('NAME=World')
        stdout, _, _ = self.execute_command('echo "Hello, $NAME!"')
        self.assertEqual(stdout, "Hello, World!")

    def test_undefined_var(self):
        stdout, _, _ = self.execute_command('echo $UNDEFINED_VAR')
        self.assertEqual(stdout, "")

if __name__ == '__main__':
    unittest.main()
