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

class TestWc(unittest.TestCase):
    def setUp(self):
        self.env = EnvironmentManager()
        self.process_manager = ProcessManager(self.env)
        self.parser = CommandParser(self.env, self.process_manager)

    def execute_command(self, command_line):
        command = self.parser.parse(command_line)
        with patch('sys.stdout', new=StringIO()) as fake_out:
            exit_code = self.process_manager.execute(command)
            return fake_out.getvalue().strip(), exit_code

    def test_wc_counts(self):
        content = 'hello world\nsecond line\n'
        with tempfile.NamedTemporaryFile(mode='w+', delete=False) as f:
            f.write(content)
            f.close()
            expected = f'2 4 {len(content.encode())} {f.name}'
            output, code = self.execute_command(f'wc {f.name}')
            self.assertEqual(output, expected)
            self.assertEqual(code, 0)
        os.unlink(f.name)

if __name__ == '__main__':
    unittest.main()
