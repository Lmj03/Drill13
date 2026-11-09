from pathlib import Path

from pico2d import *

import game_framework
import game_world

# The play world and its idle timer keep running beneath this overlay.
pauses_underlying = False
image = None


def init():
    global image
    image = load_image(str(Path(__file__).with_name('item_select.png')))


def handle_events():
    for event in get_events():
        if (event.type == SDL_QUIT or
                (event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE)):
            game_framework.quit()
            return


def update():
    game_world.update()


def render():
    clear_canvas()
    game_world.render()
    image.draw(get_canvas_width() // 2, get_canvas_height() // 2)
    update_canvas()


def finish():
    global image
    image = None
