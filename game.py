from panda3d.bullet import BulletWorld
from panda3d.core import Vec3, OrthographicLens

from player import Player
from worldgen import WorldGen


class Game:
    def __init__(self, main, level_name):
        self.main = main
        self.bullet = BulletWorld()
        self.bullet.set_gravity(Vec3(0, 0, -30))
        self.world_gen = WorldGen(main, level_name, self.bullet)
        self.level = self.world_gen.get_level()
        self.main.tick_task(self.update, 'game-update')
        self.player = Player(main, self.level.start, self.bullet)
        self.main.disable_mouse()

        lens = OrthographicLens()
        lens.set_film_size(15 * 16/9, 15)
        self.main.cam.node().setLens(lens)

    def spawn_character(self):
        pass

    def update(self, dt, task):
        self.bullet.doPhysics(dt)
        return task.cont
