from panda3d.bullet import BulletWorld, BulletDebugNode
from panda3d.core import Vec3, OrthographicLens

from gameui import GameUI
from player import Player
from worldgen import WorldGen


class Game:
    def __init__(self, main, level_name):
        self.main = main
        self.bullet = BulletWorld()
        self.bullet.set_gravity(Vec3(0, 0, -30))

        self.ui = GameUI()
        self.ui_data = {
            'coins': 0,
            'lives': 3,
            'time': 300
        }
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

    def won(self):
        self.ui.show_win()

    def lost(self):
        self.ui.show_lose()

    def update(self, dt, task):
        self.bullet.doPhysics(dt)
        kill_check = self.bullet.contact_test_pair(self.world_gen.kill_plane_node, self.player.actor_bullet_node)
        if kill_check.get_num_contacts() == 1:
            self.ui_data['lives'] -= 1
            if self.ui_data['lives'] == 0:
                self.lost()
            self.player.respawn()

        win_check = self.bullet.contact_test_pair(self.world_gen.goal_node, self.player.actor_bullet_node)
        if win_check.get_num_contacts() == 1:
            self.won()

        self.ui.update(self.ui_data)
        return task.cont
