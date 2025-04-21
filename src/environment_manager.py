import os
import re
from typing import Dict


class EnvironmentManager:
    def __init__(self):
        self.local_vars: Dict[str, str] = {}
        self.system_vars = os.environ.copy()

    def set_var(self, name: str, value: str) -> None:
        if not name.isidentifier():
            raise ValueError(f"Invalid variable name: {name}")
        self.local_vars[name] = value

    def unset_var(self, name: str) -> None:
        if name in self.local_vars:
            del self.local_vars[name]

    def get(self, name: str, default: str = "") -> str:
        return self.local_vars.get(name, self.system_vars.get(name, default))

    def expand(self, input_str: str) -> str:
        pattern = re.compile(
            r'(?<!\\)'
            r'\$'
            r'({)?'
            r'([a-zA-Z_][\w]*)'
            r'(?(1)})'
        )

        def replace(m: re.Match) -> str:
            var_name = m.group(2)
            return self.get(var_name, "")

        in_single_quote = False
        in_double_quote = False
        result = []
        i = 0

        while i < len(input_str):
            if input_str[i] == "'" and not in_double_quote:
                in_single_quote = not in_single_quote
                result.append("'")
                i += 1
                continue

            if input_str[i] == '"' and not in_single_quote:
                in_double_quote = not in_double_quote
                result.append('"')
                i += 1
                continue

            if in_single_quote:
                result.append(input_str[i])
                i += 1
            else:
                m = pattern.search(input_str, pos=i)
                if m and m.start() == i:
                    result.append(replace(m))
                    i = m.end()
                else:
                    result.append(input_str[i])
                    i += 1

        return ''.join(result)

    def get_environment(self) -> Dict[str, str]:
        env = self.system_vars.copy()
        env.update(self.local_vars)
        return env
