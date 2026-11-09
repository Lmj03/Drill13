from pathlib import Path

from pico2d import *
import game_framework
import game_world

image = None
key_up_events = []


def init():
    global image
    image = load_image(str(Path(__file__).with_name('pause.png')))
    key_up_events.clear()


def handle_events():
    for event in get_events():
        if event.type == SDL_QUIT:
            game_framework.quit()
            return
        elif event.type == SDL_KEYDOWN:
            if event.key == SDLK_ESCAPE:
                game_framework.quit()
                return
            elif event.key == SDLK_p and not getattr(event, 'repeat', 0):
                game_framework.pop_mode()
                return
        elif event.type == SDL_KEYUP:
            key_up_events.append(event)


def update():
    pass


def render():
    clear_canvas()
    game_world.render()
    image.draw(get_canvas_width() // 2, get_canvas_height() // 2, 560, 320)
    update_canvas()


def finish():
    global image
    image = None
