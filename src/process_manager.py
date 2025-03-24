import sys
import os
import subprocess
from command import Command, CommandType
from environment_manager import EnvironmentManager
from typing import List


class ProcessManager:
    def __init__(self, env: EnvironmentManager):
        self.env = env

    def execute(self, command: Command) -> int:
        if command.type == CommandType.ASSIGNMENT:
            self._handle_assignment(command)
            return 0

        if command.type == CommandType.BUILTIN:
            code = self._execute_builtin(command)
            if code is None: return 0
            return code

        return self._execute_external(command)

    def _handle_assignment(self, command: Command):
        value = ' '.join(command.args) if command.args else ''
        self.env.set_var(command.name, value)

    def _execute_builtin(self, command: Command) -> int:
        try:
            handler = {
                'echo': self._echo,
                'cat': self._cat,
                'wc': self._wc,
                'pwd': self._pwd,
                'exit': self._exit
            }[command.name]
            return handler(command.args)
        except KeyError:
            print(f"Unknown builtin command: {command.name}")
            return 1
        except Exception as e:
            print(f"{command.name}: {e}")
            return 1

    def _execute_external(self, command: Command) -> int:
        try:
            proc = subprocess.run(
                [command.name] + command.args,
                env=self.env.get_environment(),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            if proc.stdout:
                print(proc.stdout, end='')
            if proc.stderr:
                print(proc.stderr, end='', file=sys.stderr)
            
            return proc.returncode
            
        except FileNotFoundError:
            print(f"{command.name}: command not found", file=sys.stderr)
            return 127
        except PermissionError:
            print(f"{command.name}: permission denied", file=sys.stderr)
            return 126

    def _echo(self, args: List[str]):
        print(' '.join(args))

    def _cat(self, args: List[str]):
        if not args:
            raise ValueError("Missing file argument")
        with open(args[0], 'r') as f:
            print(f.read())

    def _wc(self, args: List[str]):
        if not args:
            raise ValueError("Missing file argument")
        with open(args[0], 'rb') as f:
            content = f.read()
            required_ch = b'\n'
            print(
                f"{content.count(required_ch)} {len(content.split())} {len(content)} {args[0]}")

    def _pwd(self, _: List[str]):
        print(os.getcwd())

    FINISH = 256

    def _exit(self, _: List[str]) -> int:
        return ProcessManager.FINISH
