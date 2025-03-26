import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

import tempfile
import unittest
from command_parser import CommandParser
from process_manager import ProcessManager
from environment_manager import EnvironmentManager
from unittest.mock import patch
from io import StringIO
import os
import subprocess

class TestExternalCommands(unittest.TestCase):
    def setUp(self):
        self.env = EnvironmentManager()
        self.process_manager = ProcessManager(self.env)
        self.parser = CommandParser(self.env, self.process_manager)
        self.env.set_var("TEST_VAR", "test_value")

    def execute_command(self, command_line):
        command = self.parser.parse(command_line)
        with patch('sys.stdout', new=StringIO()) as fake_out, \
             patch('sys.stderr', new=StringIO()) as fake_err:
            exit_code = self.process_manager.execute(command)
            return fake_out.getvalue().strip(), fake_err.getvalue().strip(), exit_code

    def test_basic_external_command(self):
        output, err, code = self.execute_command("ls")
        self.assertEqual(code, 0)
        self.assertTrue(len(output) > 0)

    def test_nonexistent_command(self):
        output, err, code = self.execute_command("non_existent_command")
        self.assertNotEqual(code, 0)
        self.assertTrue("not found" in err or "No such file" in err)

    def test_environment_variables(self):
        output, err, code = self.execute_command("printenv TEST_VAR")
        self.assertEqual(output, "test_value")
        self.assertEqual(code, 0)

    def test_return_code_propagation(self):
        output, err, code = self.execute_command("false")
        self.assertEqual(code, subprocess.run("false", shell=True).returncode)

    def test_error_stream(self):
        output, err, code = self.execute_command("ls non_existent_file_12345")
        self.assertNotEqual(code, 0)
        self.assertTrue("No such file" in err or "not found" in err)

    def test_quoted_arguments(self):
        with tempfile.NamedTemporaryFile() as f:
            output, err, code = self.execute_command(f'echo "File: {f.name}"')
            self.assertEqual(output, f"File: {f.name}")

if __name__ == '__main__':
    unittest.main()
