from panda3d.bullet import BulletBoxShape, BulletRigidBodyNode, BulletPlaneShape, BulletGhostNode
from panda3d.core import TextureStage, Texture, Vec3

from levelparser import LevelParser


class WorldGen:
    def __init__(self, main, level_name, bullet):
        self.main = main
        self.bullet = bullet
        self.parser = LevelParser(level_name)
        self.level = level = self.parser.load_level_file()
        for block in level.blocks:
            self._create_block(block['pos'], block['width'])

        kill_plane_shape = BulletPlaneShape(Vec3(0, 0, 1), 0)
        kill_plane_ghost = BulletGhostNode('kill-plane-ghost')
        kill_plane_ghost.add_shape(kill_plane_shape)
        self.kill_plane = render.attachNewNode(kill_plane_ghost)
        self.kill_plane.set_pos((0, 0, -2))
        self.kill_plane_node = kill_plane_ghost

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

