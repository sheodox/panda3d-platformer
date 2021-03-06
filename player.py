import time

from direct.actor.Actor import Actor, Vec3, KeyboardButton
from panda3d.bullet import BulletBoxShape, BulletRigidBodyNode

from character import Character


def clamp(mn, mx, num):
    return min(mx, max(mn, num))


left_button = KeyboardButton.ascii_key(b'a')
right_button = KeyboardButton.ascii_key(b'd')
jump_button = KeyboardButton.space()


class Player(Character):
    def __init__(self, main, start_pos, bullet, game):
        self.main = main
        self.game = game
        self.start_pos = start_pos
        self.bullet = bullet
        self.max_linear_velocity = 8
        self.player_actor = Actor('models/block.egg')
        self.player_actor.set_sx(0.5)
        self.forces = {
            'jump': 1000,
            'move': 40
        }
        self.camera_move_max_delta = 0.5

        # units forward the camera should be pointed so more in front of the player is shown
        self.camera_side_lookahead = 1

        self.add_physics()
        self.main.frame_task(self.frame, 'player-controls')
        self.sfx_jump = loader.loadSfx('sounds/jump.wav')
        self.last_played_jump_sfx = 0

    def respawn(self):
        self.actor_bullet_np.set_pos(self.start_pos)
        self.actor_bullet_node.set_linear_velocity((0, 0, 0))

    def frame(self, task):
        if not self.game.paused:
            self.controls()
            self.center_camera()
            self.check_enemy_collision()
        return task.cont

    def ray_check_by_offset(self, dirVec, offsetVec=Vec3(0, 0, 0)):
        pos = self.actor_bullet_np.get_pos()
        rc = self.bullet.rayTestClosest(pos + offsetVec, pos + dirVec)
        if rc.has_hit():
            node = rc.getNode()
            return node.getName(), node
        return None, None

    def check_enemy_collision(self):
        right_collision, _ = self.ray_check_by_offset(Vec3(0.6, 0, 0))
        left_collision, _ = self.ray_check_by_offset(Vec3(-0.6, 0, 0))
        down_checks = [
            self.ray_check_by_offset(Vec3(0, 0, -0.6)),
            self.ray_check_by_offset(Vec3(0, 0, -0.6), offsetVec=Vec3(0.2, 0, 0)),
            self.ray_check_by_offset(Vec3(0, 0, -0.6), offsetVec=Vec3(-0.2, 0, 0)),
        ]

        if right_collision == 'enemy' or left_collision == 'enemy':
            self.game.died()

        for rc in down_checks:
            down_collision, killed_enemy = rc
            if down_collision == 'enemy':
                self.game.world_gen.kill_enemy(killed_enemy)
                vel = self.actor_bullet_node.get_linear_velocity()
                self.actor_bullet_node.set_linear_velocity((vel.x, 0, 40))
                self.play_jump_sfx()

    def center_camera(self):
        goal_pos = self.actor_bullet_np.get_pos() + Vec3(self.camera_side_lookahead, -25, 3)

        def clamp_axis(num):
            return clamp(-self.camera_move_max_delta, self.camera_move_max_delta, num)

        cam_pos = self.main.camera.get_pos()
        pos_diff = goal_pos - cam_pos
        self.main.camera.setPos(
            cam_pos.x + clamp_axis(pos_diff.x),
            goal_pos.y,
            max(7.5, cam_pos.z + clamp_axis(pos_diff.z)),
        )

    def add_physics(self):
        b_shape = BulletBoxShape(Vec3(0.25, 0.5, 0.5))
        b_node = BulletRigidBodyNode('player')
        b_node.set_mass(0.5)
        b_node.add_shape(b_shape)
        b_np = render.attachNewNode(b_node)
        self.player_actor.reparent_to(b_np)
        # correct for model offset
        self.player_actor.set_pos(-0.25, 0, -0.5)
        # move to start pos, plus a little height so it can be right on the ground without jumping out of the ground
        self.actor_bullet_np = b_np
        b_np.set_pos(Vec3(self.start_pos) + Vec3(0, 0, 0.01))
        self.actor_bullet_node = b_node
        self.actor_bullet_node.set_angular_factor(Vec3(0, 0, 0))
        self.actor_bullet_node.set_linear_factor(Vec3(1, 0, 1))
        self.actor_bullet_node.set_linear_sleep_threshold(0)
        self.bullet.attachRigidBody(b_node)

    def controls(self):
        is_down = base.mouseWatcherNode.is_button_down

        # only one direction is valid at a time
        if is_down(left_button):
            self.move_left()
        elif is_down(right_button):
            self.move_right()
        else:
            # stop moving faster
            vel = self.actor_bullet_node.get_linear_velocity()
            self.actor_bullet_node.set_linear_velocity((vel.x * 0.9, 0, vel.z))

        if is_down(jump_button):
            self.jump()

        # limit movement speed
        vel = self.actor_bullet_node.get_linear_velocity()
        mn = -self.max_linear_velocity
        mx = self.max_linear_velocity
        self.actor_bullet_node.set_linear_velocity((
            clamp(mn, mx, vel.x),
            0,
            clamp(mn, mx, vel.z)
        ))

    def move_left(self):
        self.actor_bullet_node.apply_central_force(Vec3(-self.forces['move'], 0, 0))
        self.camera_side_lookahead = -abs(self.camera_side_lookahead)

    def move_right(self):
        self.actor_bullet_node.apply_central_force(Vec3(self.forces['move'], 0, 0))
        self.camera_side_lookahead = abs(self.camera_side_lookahead)

    def play_jump_sfx(self):
        now = time.time()
        if now - self.last_played_jump_sfx > 0.1:
            self.sfx_jump.play()
            self.last_played_jump_sfx = now

    def jump(self):
        actor_pos = self.actor_bullet_np.get_pos()
        # raycast below to see if they're over the ground, with a little extra wiggle room so holding jump jumps higher
        rc_result = self.bullet.rayTestClosest(actor_pos, actor_pos - Vec3(0, 0, 1.1))

        is_falling = self.actor_bullet_node.get_linear_velocity().z < 0

        if rc_result.hasHit() and rc_result.getNode().getName() == 'ground-block' and not is_falling:
            self.actor_bullet_node.apply_central_force(Vec3(0, 0, self.forces['jump']))
            self.play_jump_sfx()
