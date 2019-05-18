from direct.interval.FunctionInterval import Func, Wait, TransparencyAttrib
from direct.interval.IntervalGlobal import Sequence
from panda3d.bullet import BulletRigidBodyNode, BulletBoxShape
from panda3d.core import TextureStage, Vec3

from ai import AI


class EnemyAI(AI):
    def __init__(self, start_pos, bullet):
        AI.__init__(self, start_pos)
        self.dead = False
        self.bullet = bullet
        self.idle_texture = loader.load_texture('art/enemy-idle.png')

        def make_walk_interval(texture1, texture2):
            return Sequence(
                Func(self.set_texture, loader.load_texture(texture1)),
                Wait(0.2),
                Func(self.set_texture, loader.load_texture(texture2)),
                Wait(0.2)
            )

        self.walking_right_interval = make_walk_interval('art/enemy-walk-right-1.png', 'art/enemy-walk-right-2.png')
        self.walking_left_interval = make_walk_interval('art/enemy-walk-left-1.png', 'art/enemy-walk-left-2.png')

        self.movement_x = -1  # +/- based on direction
        self.walking_dir = None

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

    def set_texture(self, texture):
        self.model.set_texture(texture)

    def check_for_obstacles(self):
        # ray cast in front of the enemy, if it hits something reverse direction
        pos = self.bullet_np.get_pos()
        rc_result = self.bullet.rayTestClosest(pos, pos + Vec3(self.movement_x * 0.6, 0, 0))
        # turn back if this enemy is about to hit anything except the player
        if rc_result.has_hit() and rc_result.getNode().getName() != 'player':
            self.movement_x *= -1

    def died(self):
        self.dead = True
        self.bullet_np.remove_node()
        self.bullet.removeRigidBody(self.bullet_node)

    def move(self, dt):
        if self.dead or not self.activated:
            return
        self.check_for_obstacles()
        vel = self.bullet_node.get_linear_velocity()
        self.bullet_node.set_linear_velocity(Vec3(self.movement_x, 0, vel.z))

        # check if it switched directions and loop the other animation
        if self.movement_x != self.walking_dir:
            if self.movement_x > 0:
                self.walking_left_interval.finish()
                self.walking_right_interval.loop()
            else:
                self.walking_right_interval.finish()
                self.walking_left_interval.loop()
            self.walking_dir = self.movement_x

    def update(self, dt):
        self.move(dt)

