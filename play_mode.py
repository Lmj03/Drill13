from pico2d import *
import game_framework
import game_world
import pause_mode
from boy import Boy
from grass import Grass

pause_started_at = None

def handle_events():
    event_list = get_events()
    for event in event_list:
        if event.type == SDL_QUIT:
            game_framework.quit()
            return
        elif event.type == SDL_KEYDOWN and event.key == SDLK_ESCAPE:
            game_framework.quit()
            return
        elif (event.type == SDL_KEYDOWN and event.key == SDLK_p
              and not getattr(event, 'repeat', 0)):
            game_framework.push_mode(pause_mode)
            return
        else:
            boy.handle_event(event)



def init():
    global boy

    boy = Boy()
    game_world.add_oject(boy)

    grass = Grass()
    game_world.add_oject(grass, 0)



def update():
    game_world.update()


def render():
    clear_canvas()
    game_world.render()
    update_canvas()

def finish():
    pass


def pause():
    global pause_started_at
    pause_started_at = get_time()


def resume():
    global pause_started_at
    if pause_started_at is not None:
        boy.idle_started_at += get_time() - pause_started_at
        pause_started_at = None

    # Apply keys released while paused so movement does not get stuck.
    for event in pause_mode.key_up_events:
        boy.handle_event(event)
    pause_mode.key_up_events.clear()

