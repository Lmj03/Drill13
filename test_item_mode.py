from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

import ball
import boy
import game_framework
import game_world
import item_mode
import pause_mode
import play_mode


def key(key_code, event_type=item_mode.SDL_KEYDOWN, repeat=0):
    return SimpleNamespace(type=event_type, key=key_code, repeat=repeat)


class ItemModeTests(unittest.TestCase):
    def setUp(self):
        game_world.clear()
        game_framework.stack = []
        play_mode.pause_started_at = None
        pause_mode.key_up_events.clear()
        with patch.object(boy, 'load_image'), patch.object(boy, 'get_time', return_value=0):
            play_mode.boy = boy.Boy()
        game_world.add_oject(play_mode.boy)
        game_framework.stack = [play_mode]
        self.addCleanup(game_world.clear)
        self.addCleanup(game_framework.stack.clear)

    def open_items(self):
        with patch.object(play_mode, 'get_events', return_value=[key(play_mode.SDLK_i)]), \
                patch.object(item_mode, 'load_image'):
            play_mode.handle_events()
        self.assertEqual(game_framework.stack, [play_mode, item_mode])

    def test_item_overlay_keeps_movement_projectiles_and_idle_timer_running(self):
        self.open_items()
        self.assertIsNone(play_mode.pause_started_at)
        with patch.object(item_mode, 'get_events', return_value=[key(boy.SDLK_RIGHT)]):
            item_mode.handle_events()
        with patch.object(ball, 'load_image'):
            shot = ball.Ball(100, 90, 10)
        game_world.add_oject(shot)
        with patch.object(boy, 'get_canvas_width', return_value=800), \
                patch.object(ball, 'get_canvas_width', return_value=800):
            item_mode.update()
        self.assertEqual(play_mode.boy.x, 405)
        self.assertEqual(shot.x, 110)
        with patch.object(item_mode, 'get_events', return_value=[key(boy.SDLK_RIGHT, boy.SDL_KEYUP)]):
            item_mode.handle_events()
        play_mode.boy.idle_started_at = 0
        with patch.object(boy, 'get_time', return_value=6), \
                patch.object(ball, 'get_canvas_width', return_value=800):
            item_mode.update()
        self.assertEqual(play_mode.boy.state, 'SLEEP')

    def test_all_number_keys_select_and_return_to_play(self):
        for number, expected in ((item_mode.SDLK_0, None),
                                 (item_mode.SDLK_1, ball.Ball.SMALL),
                                 (item_mode.SDLK_2, ball.Ball.LARGE)):
            with self.subTest(number=number):
                self.open_items()
                with patch.object(item_mode, 'get_events', return_value=[key(number)]):
                    item_mode.handle_events()
                self.assertIs(game_framework.stack[-1], play_mode)
                self.assertEqual(play_mode.boy.ball_type, expected)
                self.assertIsNone(item_mode.image)
                self.assertEqual(play_mode.boy.idle_started_at, 0)

    def test_key_release_after_selection_is_not_lost(self):
        play_mode.boy.handle_event(key(boy.SDLK_RIGHT))
        self.open_items()
        events = [key(item_mode.SDLK_2), key(boy.SDLK_RIGHT, boy.SDL_KEYUP)]
        with patch.object(item_mode, 'get_events', return_value=events):
            item_mode.handle_events()
        self.assertEqual(play_mode.boy.state, 'IDLE')
        self.assertFalse(play_mode.boy.pressed_keys)

    def test_i_closes_without_changing_selection_and_repeat_does_not_toggle(self):
        self.open_items()
        with patch.object(item_mode, 'get_events', return_value=[key(item_mode.SDLK_i, repeat=1)]):
            item_mode.handle_events()
        self.assertIs(game_framework.stack[-1], item_mode)
        with patch.object(item_mode, 'get_events', return_value=[key(item_mode.SDLK_i)]):
            item_mode.handle_events()
        self.assertIs(game_framework.stack[-1], play_mode)
        self.assertEqual(play_mode.boy.ball_type, ball.Ball.SMALL)
        with patch.object(play_mode, 'get_events', return_value=[key(play_mode.SDLK_i, repeat=1)]):
            play_mode.handle_events()
        self.assertEqual(game_framework.stack, [play_mode])

    def test_pause_still_freezes_world_and_compensates_idle_timer(self):
        with patch.object(pause_mode, 'load_image'), patch.object(play_mode, 'get_time', return_value=2):
            game_framework.push_mode(pause_mode)
        with patch.object(game_world, 'update') as update:
            pause_mode.update()
        update.assert_not_called()
        with patch.object(play_mode, 'get_time', return_value=12):
            game_framework.pop_mode()
        self.assertEqual(play_mode.boy.idle_started_at, 10)
        self.assertIsNone(play_mode.pause_started_at)

    def test_render_draws_world_before_overlay_and_presents_once(self):
        self.open_items()
        calls = Mock()
        with patch.object(item_mode, 'clear_canvas', calls.clear), \
                patch.object(game_world, 'render', calls.world), \
                patch.object(item_mode, 'image', calls.image), \
                patch.object(item_mode, 'get_canvas_width', return_value=800), \
                patch.object(item_mode, 'get_canvas_height', return_value=600), \
                patch.object(item_mode, 'update_canvas', calls.present):
            item_mode.render()
        self.assertEqual([c[0] for c in calls.mock_calls],
                         ['clear', 'world', 'image.draw', 'present'])
        calls.image.draw.assert_called_once_with(400, 300)

    def test_escape_and_window_close_quit_from_item_mode(self):
        for event in (key(item_mode.SDLK_ESCAPE), SimpleNamespace(type=item_mode.SDL_QUIT)):
            with self.subTest(event=event), \
                    patch.object(item_mode, 'get_events', return_value=[event]), \
                    patch.object(game_framework, 'quit') as quit_game:
                item_mode.handle_events()
                quit_game.assert_called_once_with()


if __name__ == '__main__':
    unittest.main()
