from time import sleep

from utils.cc import CardClasher

if __name__ == "__main__":
    sleep(1)
    CardClasher().main()

    # cc = CardClasher()
    # while True:
    #     # get pixel color at current
    #     current_pos = cc.ahk.mouse_position
    #     color = cc.ahk.pixel_get_color(*current_pos)
    #     _, _, width, height = cc.window().get_position()
    #     current_pos = (current_pos[0] / width, current_pos[1] / height)
    #     tprint(f"Current position: {current_pos}, Color: {color}")
