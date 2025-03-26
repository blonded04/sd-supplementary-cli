from environment_manager import EnvironmentManager
from command_parser import CommandParser
from process_manager import ProcessManager
import os


class Interpreter:
    def __init__(self):
        self.env = EnvironmentManager()
        self.process_manager = ProcessManager(self.env)
        self.parser = CommandParser(self.env, self.process_manager)
        self.should_exit = False

    def run(self):
        while not self.should_exit:
            try:
                self._print_prompt()
                command = self.parser.parse(input())
                if command:
                    exit_code = self.process_manager.execute(command)
                    if exit_code == ProcessManager.FINISH:
                        self.should_exit = True
            except (KeyboardInterrupt, EOFError):
                print("\nExiting...")
                break
            except Exception as e:
                print(f"Error: {e}", file=sys.stderr)

    def _print_prompt(self):
        pwd = self.env.get("PWD", os.getcwd())
        print(f"{pwd} > ", end='', flush=True)


if __name__ == '__main__':
    Interpreter().run()
