from panda3d.bullet import BulletWorld, BulletDebugNode
from panda3d.core import Vec3, OrthographicLens

from player import Player
from worldgen import WorldGen


class Game:
    def __init__(self, main, level_name):
        self.main = main
        self.bullet = BulletWorld()
        self.bullet.set_gravity(Vec3(0, 0, -50))

        self.world_gen = WorldGen(main, level_name, self.bullet)
        self.level = self.world_gen.get_level()
        self.main.tick_task(self.update, 'game-update')
        self.player = Player(main, self.level.start, self.bullet)
        self.main.disable_mouse()

        lens = OrthographicLens()
        lens.set_film_size(15 * 16 / 9, 15)
        self.main.cam.node().setLens(lens)
        self.init_debug()

    def init_debug(self):
        debug_node = BulletDebugNode('Debug')
        debug_node.showWireframe(True)
        debug_node.showConstraints(True)
        debug_node.showBoundingBoxes(False)
        debug_node.showNormals(False)
        debug_np = render.attachNewNode(debug_node)

        def toggle_debug():
            if debug_np.isHidden():
                debug_np.show()
            else:
                debug_np.hide()

        self.bullet.setDebugNode(debug_np.node())
        self.main.accept('f3', toggle_debug)

    def spawn_character(self):
        pass

    def update(self, dt, task):
        self.bullet.doPhysics(dt)
        return task.cont
