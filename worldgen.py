from panda3d.bullet import BulletBoxShape, BulletRigidBodyNode, BulletPlaneShape, BulletGhostNode
from panda3d.core import TextureStage, Texture, Vec3, Material, PointLight, VBase4, AmbientLight

from enemyai import EnemyAI
from levelparser import LevelParser


class WorldGen:
    def __init__(self, main, level_name, bullet):
        self.main = main
        self.bullet = bullet
        self.coin_nps = {}
        self.enemies = []
        self.enemy_bullet_map = {}
        self.enemy_np_map = {}
        self.parser = LevelParser(level_name)
        self.level = level = self.parser.load_level_file()
        for block in level.blocks:
            self._create_block(block['pos'], block['width'])

        self._create_kill_plane()
        self._create_goal()
        self._create_coins()
        self._create_enemies()

        self.main.tick_task(self.update, 'worldgen-update')

        alight = AmbientLight('alight')
        alight.setColor(VBase4(1, 1, 1, 1))
        alnp = render.attachNewNode(alight)
        render.set_light(alnp)

    def _create_enemies(self):
        for pos in self.level.enemies:
            enemy = EnemyAI(pos, self.bullet)
            self.enemies.append(enemy)
            self.enemy_bullet_map[enemy.bullet_node] = enemy
            self.enemy_np_map[enemy.bullet_np] = enemy

    def update(self, dt, task):
        for np in render.findAllMatches('coin'):
            np.set_hpr(np.get_hpr() + (300 * dt, 0, 0))

        for enemy in self.enemies:
            enemy.update(dt)
        return task.cont

    def activate_enemies(self, cam_diameter, cam_pos):
        cam_radius = cam_diameter / 2
        for enemy_np in render.findAllMatches('enemy'):
            enemy_x = enemy_np.get_x()
            if cam_pos.x - cam_radius <= enemy_x <= cam_pos.x + cam_radius:
                self.enemy_np_map[enemy_np].activate()

    def _create_coins(self):
        coin_mat = Material()
        coin_mat.set_ambient((1, 0.9, 0.2, 1))
        coin_mat.set_shininess(5.0)

        for coin_pos in self.level.coins:
            coin_model = loader.loadModelCopy('models/coin.egg')
            coin_model.set_material(coin_mat)

            coin_node = BulletGhostNode('coin')
            coin_shape = BulletBoxShape(Vec3(0.4, 0.5, 0.4))
            coin_node.add_shape(coin_shape)
            coin_np = render.attachNewNode(coin_node)
            coin_np.set_pos(Vec3(0.5, 0, 0.5) + coin_pos)
            coin_model.reparent_to(coin_np)
            self.bullet.attachGhost(coin_node)

            self.coin_nps[coin_node] = coin_np

    def remove_coin(self, node):
        self.bullet.removeGhost(node)
        self.coin_nps[node].remove_node()
        del self.coin_nps[node]

    def kill_enemy(self, node):
        self.enemy_bullet_map[node].died()

    def _create_kill_plane(self):
        # kill plane
        kill_plane_shape = BulletPlaneShape(Vec3(0, 0, 1), -2)
        kill_plane_ghost = BulletGhostNode('kill-plane-ghost')
        kill_plane_ghost.add_shape(kill_plane_shape)
        self.kill_plane = render.attachNewNode(kill_plane_ghost)
        self.kill_plane.set_pos((0, 0, -2))
        self.kill_plane_node = kill_plane_ghost

    def _create_goal(self):
        # goal
        goal_model = loader.load_model('models/goal-flag.egg')
        self.goal_node = BulletGhostNode('goal')
        goal_shape = BulletBoxShape(Vec3(0.5, 0.5, 2))
        self.goal_node.add_shape(goal_shape)
        goal_bullet_np = render.attachNewNode(self.goal_node)
        goal_bullet_np.set_pos(self.level.goal)
        goal_model.reparent_to(goal_bullet_np)


    def get_level(self):
        return self.level

    def _create_block(self, pos, width):
        block = self.main.loader.loadModelCopy('models/block')
        block.set_pos(pos)
        block.set_sx(width)
        block.reparent_to(self.main.render)

        # add physics
        b_node = BulletRigidBodyNode('ground-block')
        b_shape = BulletBoxShape(Vec3(0.5 * width, 0.5, 0.5))
        b_node.add_shape(b_shape)
        b_np = render.attachNewNode(b_node)
        # align with the block's position
        b_np.set_pos(block.get_pos() + Vec3(0.5 * width, 0, 0.5))
        self.bullet.attachRigidBody(b_node)

        self._texture_block(block, width, 'art/block.png')

    def _texture_block(self, np, block_width, texture_path):
        texture = base.loader.load_texture(texture_path)
        ts = TextureStage('ts')

        np.setTexScale(ts, block_width, 1)
        np.set_texture(ts, texture, 1)
        texture.setWrapU(Texture.WM_repeat)
        texture.setWrapV(Texture.WM_repeat)

