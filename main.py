import os
import sys
from direct.showbase.ShowBase import ShowBase, loadPrcFileData
from direct.showbase.ShowBaseGlobal import globalClock

from game import Game
from menuui import MenuUI
from worldgen import WorldGen

win_w = 1440
win_h = 900
win_aspect = win_w / win_h
loadPrcFileData('', f'win-size {win_w} {win_h}')


def prefix_task_name(name):
    return f'sheodox-task.{name}'


class Main(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)
        self.set_background_color(0.1, 0.6, 0.7)
        self._ticks_per_second = 60
        self.clean_up()
        self.game_stats = {'coins': 0, 'lives': 3}
        self.levels = os.listdir('levels')
        self.levels.sort()
        self.level_index = 0
        self.main_menu()

    def start_game(self):
        self.load_level(self.levels[self.level_index])

    def main_menu(self):
        MenuUI().show_main_menu(self.start_game)

    def next_level(self, stats):
        self.game_stats = stats
        num_levels = len(self.levels)
        self.level_index += 1
        if num_levels != self.level_index:
            self.load_level(self.levels[self.level_index])
        else:
            # they beat the game
            self.beat_game()

    def beat_game(self):
        self.clean_up()
        MenuUI().show_beat_game()
        self.later_task(sys.exit, 'quit', 2)

    def load_level(self, name):
        self.clean_up()
        Game(self, name, self.game_stats)

    def clean_up(self):
        self.task_mgr.removeTasksMatching(prefix_task_name('*'))
        self.ignore_all()
        # clean up all 3d and 2d nodes
        for child in self.render.get_children():
            if child != self.camera:
                child.remove_node()
        for child in self.aspect2d.get_children():
            child.remove_node()
        self.accept("escape", sys.exit)  # Escape quits

    def frame_task(self, fn, name):
        name = prefix_task_name(name)
        self.task_mgr.add(fn, name)

    def later_task(self, fn, name, delay):
        name = prefix_task_name(name)
        self.task_mgr.do_method_later(delay, fn, name)

    def tick_task(self, fn, name):
        name = prefix_task_name(name)

        def tick_wrapper(task):
            dt = globalClock.getDt()
            return fn(dt, task)

        self.task_mgr.add(tick_wrapper, name)

app = Main()
app.run()