import inspect
import time
import body
from card_clasher import CardClasher
from rich import print

from config import LEAVE_BATTLE
import ocr
from utils.types import Rect


class CLI:
    """A class dedicated to defining the commands for the CLI."""
    def __init__(self):
        self.cc = CardClasher()

    def all(self):
        """Start the main functionality"""
        self.cc.main()
        
    def stop_pots(self):
        return self.cc.stop_pots()
    
    def stop_boss(self):
        self.cc.stop_boss()
        
    def start_pots(self):
        self.cc.start_pots()
        
    def start_boss(self):
        self.cc.start_boss()
        
    def clean(self):
        self.cc.clean()
        
    def respawn(self):
        self.cc.respawn()
    
    def rejoin(self):
        self.cc.rejoin()
    
    def pixel_coords(self):
        """For 5 seconds, prints the current mouse position and pixel color."""
        print('...')
        time.sleep(1)

        for _ in range(5):
            current_pos = body.ahk.mouse_position
            color = body.ahk.pixel_get_color(*current_pos)
            _, _, width, height = body.roblox().get_position()
            current_pos = (current_pos[0] / width, current_pos[1] / height)
            print(f"Position: {current_pos}, Color: {color}")
            time.sleep(1)

    def help(self):
        """Displays this help message, listing all available commands."""
        print("\nAvailable commands:")
        # This inspects the instance of the class passed to it
        for name, method in inspect.getmembers(self, predicate=inspect.ismethod):
            # Filter out any private/internal methods (starting with '_')
            if not name.startswith('_'):
                doc = inspect.getdoc(method)
                summary = doc.split('\n')[0] if doc else "No description available."
                print(f"  {name:<15} {summary}")
        print("  exit, quit         Exits the CLI.\n")


def run_cli_loop(cli_instance):
    """
    Runs the main interactive loop for a given CLI instance.
    """
    print("Welcome to the CLI. Type 'help' for a list of commands or 'exit' to quit.")
    while True:
        try:
            inp = input(">> ").strip()
            if not inp:
                continue

            parts = inp.split()
            command = parts[0].lower()
            args = parts[1:]

            if command in ["exit", "quit"]:
                print("Exiting CLI.")
                break

            # Check if the command exists on the instance and is callable
            if hasattr(cli_instance, command) and callable(getattr(cli_instance, command)):
                method = getattr(cli_instance, command)
                # Ensure we don't call private methods
                if command.startswith('_'):
                     print(f"Error: '{command}' is not a valid command.")
                     continue
                method(*args)
            else:
                print(f"Error: Unknown command '{command}'. Type 'help' for options.")
        except TypeError as e:
            # Provides more specific feedback on argument mismatches
            print(f"Error: Invalid arguments for '{command}'. Please check the command's requirements. Details: {e}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")


def main():
    run_cli_loop(CLI())


if __name__ == "__main__":
    main()
    # cc = CardClasher()
    # while True:
    #     # get pixel color at current
    #     current_pos = cc.ahk.mouse_position
    #     color = cc.ahk.pixel_get_color(*current_pos)
    #     _, _, width, height = cc.window().get_position()
    #     current_pos = (current_pos[0] / width, current_pos[1] / height)
    #     tprint(f"Current position: {current_pos}, Color: {color}")
