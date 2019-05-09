from panda3d.core import TextureStage, Texture, TransformState


class Texturer:
    def texture_block(self, np, block_width, texture_path):
        texture = base.loader.load_texture(texture_path)
        ts = TextureStage('ts')

        np.setTexScale(ts, block_width, 1)
        np.set_texture(ts, texture, 1)
        texture.setWrapU(Texture.WM_repeat)
        texture.setWrapV(Texture.WM_repeat)
