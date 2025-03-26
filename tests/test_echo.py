import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

import unittest
from unittest.mock import patch
from io import StringIO
from command_parser import CommandParser
from process_manager import ProcessManager
from environment_manager import EnvironmentManager

class TestEcho(unittest.TestCase):
    def setUp(self):
        self.env = EnvironmentManager()
        self.process_manager = ProcessManager(self.env)
        self.parser = CommandParser(self.env, self.process_manager)

    def execute_command(self, command_line):
        command = self.parser.parse(command_line)
        with patch('sys.stdout', new=StringIO()) as fake_out:
            exit_code = self.process_manager.execute(command)
            return fake_out.getvalue().strip(), exit_code

    def test_echo_basic(self):
        output, code = self.execute_command('echo hello')
        self.assertEqual(output, 'hello')
        self.assertEqual(code, 0)

    def test_echo_multiple_args(self):
        output, code = self.execute_command('echo hello world')
        self.assertEqual(output, 'hello world')
        self.assertEqual(code, 0)

    def test_echo_with_quotes(self):
        output, code = self.execute_command('echo "hello world"')
        self.assertEqual(output, 'hello world')
        self.assertEqual(code, 0)

    def test_echo_variable(self):
        self.env.set_var('VAR', 'value')
        output, code = self.execute_command('echo $VAR')
        self.assertEqual(output, 'value')
        self.assertEqual(code, 0)

if __name__ == '__main__':
    unittest.main()
