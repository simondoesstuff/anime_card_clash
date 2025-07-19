from card_clasher import (
    CardClasher,
    BATTLE_STATUS,
    BATTLE_STATUS_COLOR,
)
from time import sleep
from rich import print
from textwrap import dedent


def test_cc_pixel(cc: CardClasher, target_position, expected_color=None):
    print("[bold]Moving to battle status eye icon in a second for reference...[/bold]")
    sleep(1)
    cc.window().activate()
    cc.mouse_move(target_position)
    sleep(1)
    res = cc.until_pixel(
        coord=target_position,
        color=expected_color,
    )
    if res:
        print("[green]Pixel matches expected color. Test passed.[/green]")


if __name__ == "__main__":
    cc = CardClasher()

    target = input(
        dedent("""
            Specify the test you want to run...
              1. Battle Status Eye Icon for "Open Battle"
              2. Battle Status Eye Icon for "Leave Battle"
               """)
    )

    print()
    if target == "1":
        print("[magenta italic]Make sure the battle menu is open![/magenta italic]")
        test_cc_pixel(cc, BATTLE_STATUS.while_closed, BATTLE_STATUS_COLOR)
    elif target == "2":
        print("[magenta italic]Make sure the battle menu is open![/magenta italic]")
        test_cc_pixel(cc, BATTLE_STATUS.while_open, BATTLE_STATUS_COLOR)
    else:
        print("[red]Invalid option. Exiting.[/red]")
    print()
