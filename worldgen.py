from levelparser import LevelParser
from texturer import Texturer


class WorldGen:
    def __init__(self, main):
        self.main = main
        self.parser = LevelParser()
        self.main.camera.set_pos(7, -49, 5)
        self.texturer = Texturer()

    def load(self, level):
        level = self.parser.load_level_file(level)
        for block in level.blocks:
            self._create_block(block['pos'], block['width'])
        return level

    def _create_block(self, pos, width):
        block = self.main.loader.loadModelCopy('models/block')
        block.set_pos(pos)
        block.set_sx(width)
        block.reparent_to(self.main.render)
        self.texturer.texture_block(block, width, 'art/block.png')

