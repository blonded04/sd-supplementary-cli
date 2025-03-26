import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

import unittest
from command_parser import CommandParser
from process_manager import ProcessManager
from environment_manager import EnvironmentManager

class TestExit(unittest.TestCase):
    def setUp(self):
        self.env = EnvironmentManager()
        self.process_manager = ProcessManager(self.env)
        self.parser = CommandParser(self.env, self.process_manager)

    def test_exit_command(self):
        command = self.parser.parse('exit')
        code = self.process_manager.execute(command)
        self.assertEqual(code, ProcessManager.FINISH)

if __name__ == '__main__':
    unittest.main()
