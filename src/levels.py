from time import sleep
from types import SimpleNamespace
from body import click, key, keys, roblox
from card_clasher import CardClasher
from config import FIGHT
from utils.try_convert import is_float


# TODO: remove the cicular dependency between this class & card_clasher

EMINENCE = [
(0.501, 0.369),
(0.637, 0.419),
(0.355, 0.371)
]


def start_fight():
    click(FIGHT)


def interpret_instruction(instruction: str):
    """
    Expects an instruction language in the form: "1.2wa 3.2 .5> <"...
    > and < correspond to right and left respectively
    """

    terms = instruction.split()
    
    for term in terms:
        if is_float(term):
            sleep(float(term))
        else:
            pivot = None

            for i, char in enumerate(term):
                if not (char.isnumeric() or char == "."):
                    pivot = i
                    break
            
            if pivot is None:
                raise ValueError("Unrecognized form.")
                
            left = term[:pivot]
            right = term[pivot:]
            
            if not is_float(left):
                if len(left) == 0:
                    left = "0"
                else:
                    raise ValueError("Unrecognized form.")
                
            duration = float(left)
            operations = list()
            
            for op in right:
                if op == '>':
                    operations.append("right")
                elif op == "<":
                    operations.append("left")
                else:
                    operations.append(op)
                    
            keys(operations, duration, simultaneous=True)


def start_eminence(cc: CardClasher):
    # TODO: implement a general teleport
    roblox().activate()
    interpret_instruction("1.25> 1.9w .7wd 1w 1.1wa 1.7w")
    click(FIGHT)
    
if __name__ == "__main__":
    start_eminence(None)