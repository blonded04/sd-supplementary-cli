from typing import Optional, List, Tuple
from command import CommandType, Command, CommandFactory
from environment_manager import EnvironmentManager


class CommandParser:
    def __init__(self, env: EnvironmentManager, process_manager):
        self.env = env
        self.process_manager = process_manager

    def parse(self, input_str: str) -> Optional[Command]:
        input_str = input_str.strip()
        if not input_str:
            return None

        if '=' in input_str and not input_str.startswith('='):
            return self._parse_assignment(input_str)

        parts = self._split_pipes(input_str)
        if not parts:
            return None

        commands = []
        for part in parts:
            tokens = self._tokenize(part)
            if not tokens:
                return None
            cmd_name = self._expand(tokens[0], handle_command_sub=True)
            args = [self._expand(t, handle_command_sub=True)
                    for t in tokens[1:]]
            commands.append(self._create_command(cmd_name, args))

        for i in range(len(commands)-1):
            commands[i].pipe_to = commands[i+1]

        return commands[0] if commands else None

    def _split_pipes(self, s: str) -> List[str]:
        parts = []
        current = []
        quote = None
        escape = False

        for c in s:
            if escape:
                current.append(c)
                escape = False
            elif c == '\\':
                escape = True
                current.append(c)
            elif c in ('"', "'"):
                if quote == c:
                    quote = None
                elif not quote:
                    quote = c
                current.append(c)
            elif c == '|' and not quote:
                parts.append(''.join(current).strip())
                current = []
            else:
                current.append(c)
        if current:
            parts.append(''.join(current).strip())
        return parts

    def _parse_assignment(self, s: str) -> Command:
        var, value = s.split('=', 1)
        var = var.strip()
        if not var.isidentifier():
            raise ValueError(f"Invalid variable name: {var}")
        return CommandFactory.create(
            CommandType.ASSIGNMENT,
            var,
            [self._expand(value.strip(), handle_command_sub=True)]
        )

    def _tokenize(self, s: str) -> List[str]:
        tokens = []
        buffer = []
        quote = None
        escape = False

        for c in s:
            if escape:
                buffer.append(c)
                escape = False
            elif c == '\\':
                escape = True
            elif c in ('"', "'"):
                if quote == c:
                    quote = None
                elif not quote:
                    quote = c
                else:
                    buffer.append(c)
            elif not quote and c.isspace():
                if buffer:
                    tokens.append(''.join(buffer))
                    buffer = []
            else:
                buffer.append(c)
        if buffer:
            tokens.append(''.join(buffer))
        return tokens

    def _expand(self, s: str, handle_command_sub: bool = False) -> str:
        result = []
        i = 0
        while i < len(s):
            if s[i] == '$' and (i == 0 or s[i-1] != '\\'):
                if i+1 < len(s) and s[i+1] == '(' and handle_command_sub:
                    cmd_output, i = self._read_command_substitution(s, i+2)
                    result.append(cmd_output)
                else:
                    var_name, i = self._read_var(s, i+1)
                    result.append(self.env.get(var_name, ''))
            else:
                result.append(s[i])
                i += 1
        return ''.join(result).replace('\\$', '$')

    def _read_command_substitution(self, s: str, start: int) -> Tuple[str, int]:
        depth = 1
        i = start
        while i < len(s):
            if s[i] == '(':
                depth += 1
            elif s[i] == ')':
                depth -= 1
                if depth == 0:
                    break
            i += 1
        if i >= len(s):
            raise ValueError("Unclosed command substitution")
        command_str = s[start:i]
        output = self._execute_command_substitution(command_str)
        return output, i+1

    def _execute_command_substitution(self, command_str: str) -> str:
        from command_parser import CommandParser
        temp_parser = CommandParser(self.env, self.process_manager)
        command = temp_parser.parse(command_str)
        if not command:
            return ""
        stdout, _, _ = self.process_manager.execute_capture(command)
        return stdout.strip()

    def _read_var(self, s: str, start: int) -> Tuple[str, int]:
        if start >= len(s):
            return '', start

        if s[start] == '{':
            end = s.find('}', start+1)
            if end == -1:
                return s[start+1:], len(s)
            return s[start+1:end], end+1

        end = start
        while end < len(s) and (s[end].isalnum() or s[end] == '_'):
            end += 1
        return s[start:end], end

    def _create_command(self, name: str, args: List[str]) -> Command:
        if name in CommandFactory.BUILTIN_COMMANDS:
            return CommandFactory.create(
                CommandType.BUILTIN,
                name,
                args
            )
        return CommandFactory.create(
            CommandType.EXTERNAL,
            name,
            args
        )
