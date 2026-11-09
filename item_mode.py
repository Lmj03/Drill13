from pathlib import Path

from pico2d import *

import game_framework
import game_world
from ball import Ball

# The play world and its idle timer keep running beneath this overlay.
pauses_underlying = False
image = None
ball_choices = {SDLK_0: None, SDLK_1: Ball.SMALL, SDLK_2: Ball.LARGE}


def init():
    global image
    image = load_image(str(Path(__file__).with_name('item_select.png')))


def handle_events():
    import play_mode

    close_requested = False
    for event in get_events():
        if (event.type == SDL_QUIT or
                (event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE)):
            game_framework.quit()
            return
        if (event.type == SDL_KEYDOWN and event.key in ball_choices
                and not getattr(event, 'repeat', 0)):
            play_mode.boy.select_ball(ball_choices[event.key])
            close_requested = True

    if close_requested:
        game_framework.pop_mode()


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
