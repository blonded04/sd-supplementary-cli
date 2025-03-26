import sys
import os
import subprocess
from command import Command, CommandType
from environment_manager import EnvironmentManager
from typing import List, Tuple, Optional


class ProcessManager:
    def __init__(self, env: EnvironmentManager):
        self.env = env

    def execute(self, command: Command) -> int:
        if command.type == CommandType.ASSIGNMENT:
            self._handle_assignment(command)
            return 0

        if command.pipe_to:
            return self._execute_pipeline(command)

        if command.type == CommandType.BUILTIN:
            code = self._execute_builtin(command)
            return code if code is not None else 0
        else:
            return self._execute_external(command)

    def execute_capture(self, command: Command, stdin_data: Optional[str] = None) -> Tuple[str, str, int]:
        if command.type == CommandType.BUILTIN:
            return self._execute_builtin_capture(command, stdin_data)
        else:
            return self._execute_external_capture(command, stdin_data)

    def _execute_pipeline(self, command: Optional[Command]) -> int:
        current_cmd = command
        input_data = None
        exit_code = 0

        while current_cmd:
            stdout, stderr, code = self.execute_capture(
                current_cmd, input_data)
            if code != 0:
                exit_code = code
            input_data = stdout
            current_cmd = current_cmd.pipe_to
            if stderr:
                print(stderr, file=sys.stderr, end='')

        if input_data:
            print(input_data, end='')
        return exit_code

    def _execute_external_capture(self, command: Command, stdin_data: Optional[str]) -> Tuple[str, str, int]:
        try:
            proc = subprocess.run(
                [command.name] + command.args,
                input=stdin_data,
                env=self.env.get_environment(),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            return (proc.stdout, proc.stderr, proc.returncode)
        except FileNotFoundError:
            return ("", f"{command.name}: command not found", 127)
        except PermissionError:
            return ("", f"{command.name}: permission denied", 126)

    def _execute_builtin_capture(self, command: Command, stdin_data: Optional[str]) -> Tuple[str, str, int]:
        import io
        from contextlib import redirect_stdout, redirect_stderr

        stdout_buf = io.StringIO()
        stderr_buf = io.StringIO()
        code = 0

        with redirect_stdout(stdout_buf), redirect_stderr(stderr_buf):
            try:
                if command.name == 'echo':
                    print(' '.join(command.args))
                elif command.name == 'cat':
                    if not command.args:
                        raise ValueError("Missing file argument")
                    try:
                        with open(command.args[0], 'r') as f:
                            print(f.read())
                    except Exception as e:
                        print(f"cat: {e}", file=sys.stderr)
                        raise
                elif command.name == 'wc':
                    if not command.args and not stdin_data:
                        print("wc: missing file argument", file=sys.stderr)
                        code = 1
                    else:
                        content = stdin_data if not command.args else open(
                            command.args[0], 'rb').read()
                        lines = 0
                        words = 0
                        bytes_cnt = 0
                        if content is not None:
                            lines = content.count(b'\n') if isinstance(
                                content, bytes) else content.count('\n')
                            words = len(content.split())
                            bytes_cnt = len(content)
                        if command.args:
                            print(
                                f"{lines} {words} {bytes_cnt} {command.args[0]}")
                        else:
                            print(f"{lines} {words} {bytes_cnt}")
                elif command.name == 'pwd':
                    print(os.getcwd())
                elif command.name == 'exit':
                    code = self._exit([])
            except Exception as e:
                print(str(e), file=sys.stderr)
                code = 1

        return (stdout_buf.getvalue(), stderr_buf.getvalue(), code)

    def _handle_assignment(self, command: Command):
        value = ' '.join(command.args) if command.args else ''
        self.env.set_var(command.name, value)

    def _execute_builtin(self, command: Command) -> int:
        stdout, stderr, code = self._execute_builtin_capture(command, None)
        if stdout:
            print(stdout, end='')
        if stderr:
            print(stderr, end='', file=sys.stderr)
        return code

    def _execute_external(self, command: Command) -> int:
        stdout, stderr, code = self._execute_external_capture(command, None)
        if stdout:
            print(stdout, end='')
        if stderr:
            print(stderr, end='', file=sys.stderr)
        return code

    FINISH = 256

    def _exit(self, _: List[str]) -> int:
        return ProcessManager.FINISH
