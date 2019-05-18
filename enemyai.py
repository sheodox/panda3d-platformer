from direct.interval.FunctionInterval import Func, Wait, TransparencyAttrib
from direct.interval.IntervalGlobal import Sequence
from panda3d.bullet import BulletRigidBodyNode, BulletBoxShape
from panda3d.core import TextureStage, Vec3

from ai import AI


class EnemyAI(AI):
    def __init__(self, start_pos, bullet):
        AI.__init__(self, start_pos)
        self.bullet = bullet
        self.idle_texture = loader.load_texture('art/enemy-idle.png')
        self.walking_textures = [
            loader.load_texture('art/enemy-walk-1.png'),
            loader.load_texture('art/enemy-walk-2.png')
        ]
        self.walking_interval = Sequence(
            Wait(0.2),
            Func(self.set_texture, self.walking_textures[0]),
            Wait(0.2),
            Func(self.set_texture, self.walking_textures[1])
        )

        self.movement_x = -1  # +/- based on direction

        self.model = loader.loadModelCopy('models/block.egg')
        self.model.set_transparency(TransparencyAttrib.M_alpha)
        self.model.set_pos(Vec3(-0.5, 0, -0.5))
        self.bullet_node = BulletRigidBodyNode('enemy')
        self.bullet_node.set_mass(0.5)
        self.bullet_node.set_angular_factor(Vec3(0, 0, 0))
        self.bullet_node.set_linear_factor(Vec3(1, 0, 1))
        self.bullet_node.set_linear_sleep_threshold(0)
        shape = BulletBoxShape(Vec3(0.5, 0.5, 0.5))
        self.bullet_node.add_shape(shape)
        self.bullet_np = render.attachNewNode(self.bullet_node)
        self.bullet_np.set_pos(Vec3(0.5, 0, 0.5) + start_pos)
        self.model.reparent_to(self.bullet_np)
        self.bullet.attachRigidBody(self.bullet_node)
        self.set_texture(self.idle_texture)
        self.walking_interval.loop()

    def set_texture(self, texture):
        self.model.set_texture(texture)

    def check_for_obstacles(self):
        # ray cast in front of the enemy, if it hits something reverse direction
        pos = self.bullet_np.get_pos()
        rc_result = self.bullet.rayTestClosest(pos, pos + Vec3(self.movement_x * 0.6, 0, 0))
        # turn back if this enemy is about to hit anything except the player
        if rc_result.has_hit() and rc_result.getNode().getName() != 'player':
            self.movement_x *= -1

    def move(self, dt):
        self.check_for_obstacles()
        vel = self.bullet_node.get_linear_velocity()
        self.bullet_node.set_linear_velocity(Vec3(self.movement_x, 0, vel.z))

    def update(self, dt):
        self.move(dt)

