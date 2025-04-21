from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


class CommandType(Enum):
    BUILTIN = "builtin"
    EXTERNAL = "external"
    ASSIGNMENT = "assignment"
    PIPE = "pipe"


@dataclass
class Command:
    type: CommandType
    name: str
    args: List[str]
    pipe_to: Optional['Command'] = None


class CommandFactory:
    BUILTIN_COMMANDS = {'cat', 'echo', 'wc', 'pwd', 'exit', 'grep'}

    @classmethod
    def create(cls,
               command_type: CommandType,
               name: str,
               args: List[str],
               pipe_to: Optional[Command] = None) -> Command:
        return Command(
            type=command_type,
            name=name,
            args=args,
            pipe_to=pipe_to
        )
