import time

from math import floor
from panda3d.bullet import BulletWorld, BulletDebugNode
from panda3d.core import Vec3, OrthographicLens, NodePath

from gameui import GameUI
from player import Player
from worldgen import WorldGen


class Game:
    def __init__(self, main, level_name):
        self.main = main
        self.paused = False
        self.bullet = BulletWorld()
        self.bullet.set_gravity(Vec3(0, 0, -30))
        self.start_time = time.time()

        self.ui = GameUI()
        self.time_max = 300
        self.game_data = {
            'coins': 0,
            'lives': 3,
            'time': self.time_max
        }
        self.world_gen = WorldGen(main, level_name, self.bullet)
        self.level = self.world_gen.get_level()
        self.main.tick_task(self.update, 'game-update')
        self.player = Player(main, self.level.start, self.bullet, self)
        self.main.disable_mouse()

        camera_width_base = 15
        aspect = 16 / 9
        self.camera_diameter = camera_width_base * aspect
        lens = OrthographicLens()
        lens.set_film_size(self.camera_diameter, camera_width_base)

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
        self.paused = True
        self.ui.show_win()

    def lost(self):
        self.paused = True
        self.ui.show_lose()

    def died(self):
        self.game_data['lives'] -= 1
        if self.game_data['lives'] == 0:
            self.lost()
        self.player.respawn()

    def update(self, dt, task):
        self.bullet.doPhysics(dt)
        kill_check = self.bullet.contact_test_pair(self.world_gen.kill_plane_node, self.player.actor_bullet_node)
        if kill_check.get_num_contacts() == 1:
            self.died()

        win_check = self.bullet.contact_test_pair(self.world_gen.goal_node, self.player.actor_bullet_node)
        if win_check.get_num_contacts() == 1:
            self.won()

        coin_check = self.bullet.contact_test(self.player.actor_bullet_node)
        for contact in coin_check.get_contacts():
            node = contact.getNode1()
            if node.getName() == 'coin':
                self.game_data['coins'] += 1
                self.world_gen.remove_coin(node)

            if self.game_data['coins'] == 100:
                self.game_data['coins'] = 0
                self.game_data['lives'] += 1

        # show full numbers, don't allow going below zero
        if not self.paused:
            self.game_data['time'] = max(0, floor(self.time_max - (time.time() - self.start_time)))
            if self.game_data['time'] == 0:
                self.lost()

        self.world_gen.activate_enemies(self.camera_diameter, self.main.camera.get_pos())

        self.ui.update(self.game_data)
        return task.cont
