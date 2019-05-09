import sys
from direct.showbase.ShowBase import ShowBase, loadPrcFileData

from game import Game
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
        self._ticks_per_second = 60
        self.clean_up()
        self.load_level('level-1')

    def load_level(self, name):
        self.clean_up()
        Game(self, name)

    def clean_up(self):
        # self.task_mgr.removeTasksMatching(prefix_task_name('*'))
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

    def tick_task(self, fn, name):
        name = prefix_task_name(name)
        print('TODO IMPLEMENT TICK TASK')



app = Main()
app.run()