import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

import unittest
import tempfile
import os
from command_parser import CommandParser
from process_manager import ProcessManager
from environment_manager import EnvironmentManager
from unittest.mock import patch
from io import StringIO

class TestCat(unittest.TestCase):
    def setUp(self):
        self.env = EnvironmentManager()
        self.parser = CommandParser(self.env)
        self.process_manager = ProcessManager(self.env)

    def execute_command(self, command_line):
        command = self.parser.parse(command_line)
        with patch('sys.stdout', new=StringIO()) as fake_out:
            exit_code = self.process_manager.execute(command)
            return fake_out.getvalue(), exit_code

    def test_cat_file(self):
        content = 'test content'
        with tempfile.NamedTemporaryFile(mode='w+', delete=False) as f:
            f.write(content)
            f.close()
            output, code = self.execute_command(f'cat {f.name}')
            self.assertEqual(output.strip(), content)
            self.assertEqual(code, 0)
        os.unlink(f.name)

    def test_cat_nonexistent(self):
        output, code = self.execute_command('cat missing.txt')
        self.assertTrue('Errno' in output)
        self.assertNotEqual(code, 0)

if __name__ == '__main__':
    unittest.main()
