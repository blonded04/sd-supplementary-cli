from typing import Optional, List, Tuple
from command import CommandType, Command, CommandFactory
from environment_manager import EnvironmentManager


class CommandParser:
    def __init__(self, env: EnvironmentManager):
        self.env = env

    def parse(self, input_str: str) -> Optional[Command]:
        input_str = input_str.strip()
        if not input_str:
            return None

        if '=' in input_str and not input_str.startswith('='):
            return self._parse_assignment(input_str)

        tokens = self._tokenize(input_str)
        if not tokens:
            return None

        cmd_name = self._expand(tokens[0])
        args = [self._expand(t) for t in tokens[1:]]

        return self._create_command(cmd_name, args)

    def _parse_assignment(self, s: str) -> Command:
        var, value = s.split('=', 1)
        var = var.strip()
        if not var.isidentifier():
            raise ValueError(f"Invalid variable name: {var}")
        return CommandFactory.create(
            CommandType.ASSIGNMENT,
            var,
            [self._expand(value.strip())]
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

    def _expand(self, s: str) -> str:
        result = []
        i = 0
        while i < len(s):
            if s[i] == '$' and (i == 0 or s[i-1] != '\\'):
                var_name, i = self._read_var(s, i+1)
                result.append(self.env.get(var_name, ''))
            else:
                result.append(s[i])
                i += 1
        return ''.join(result).replace('\\$', '$')

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
