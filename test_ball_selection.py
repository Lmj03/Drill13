import unittest
from unittest.mock import Mock, patch

import ball
import boy
import game_world


class BallSelectionTests(unittest.TestCase):
    def setUp(self):
        game_world.clear()
        ball.Ball.images.clear()
        self.addCleanup(game_world.clear)
        self.addCleanup(ball.Ball.images.clear)

    def make_boy(self):
        with patch.object(boy, 'load_image'), patch.object(boy, 'get_time', return_value=0):
            return boy.Boy()

    def test_each_size_uses_its_own_cached_sprite(self):
        small_image, large_image = Mock(), Mock()
        with patch.object(ball, 'load_image', side_effect=[small_image, large_image]) as load:
            small = ball.Ball(100, 90, 10)
            large = ball.Ball(100, 90, 10, ball.Ball.LARGE)
            another_small = ball.Ball(100, 90, 10)
        self.assertTrue(load.call_args_list[0].args[0].endswith('ball21x21.png'))
        self.assertTrue(load.call_args_list[1].args[0].endswith('ball41x41.png'))
        self.assertEqual(load.call_count, 2)
        self.assertIs(another_small.image, small.image)
        small.draw()
        large.draw()
        small_image.draw.assert_called_once_with(100, 90)
        large_image.draw.assert_called_once_with(100, 90)

    def test_selection_applies_to_future_shots_and_none_disables_firing(self):
        player = self.make_boy()
        with patch.object(ball, 'load_image'):
            player.fire_ball()
            small = game_world.world[1][0]
            player.select_ball(ball.Ball.LARGE)
            player.face_dir = -1
            player.fire_ball()
            large = game_world.world[1][1]
            player.select_ball(None)
            player.fire_ball()
        self.assertEqual(small.ball_type, ball.Ball.SMALL)
        self.assertEqual(large.ball_type, ball.Ball.LARGE)
        self.assertEqual(large.velocity, -10)
        self.assertEqual(len(game_world.world[1]), 2)

    def test_both_sizes_move_and_leave_the_world(self):
        with patch.object(ball, 'load_image'), patch.object(ball, 'get_canvas_width', return_value=800):
            for size in (ball.Ball.SMALL, ball.Ball.LARGE):
                shot = ball.Ball(795, 90, 10, size)
                game_world.add_oject(shot)
                shot.update()
                self.assertEqual(shot.x, 805)
                self.assertNotIn(shot, game_world.world[1])


if __name__ == '__main__':
    unittest.main()
