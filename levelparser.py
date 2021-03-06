from enum import Enum, auto
from level import Level


class TileSet:
    BLOCK = 'b'
    AIR = '.'
    START = 's'
    GOAL = 'g'
    COIN = 'c'
    ENEMY = 'e'


class ScanState(Enum):
    TRAVERSING_BLOCK = auto()
    SCANNING = auto()


class LevelParser:
    def __init__(self, level_name):
        self.level_name = level_name

    def _assert_level_integrity(self, rows):
        assert_prefix = f'[level parser: {self.level_name}] - '
        str_level = ''.join(rows)
        num_s = str_level.count('s')
        num_g = str_level.count('g')
        assert num_s == 1, f'{assert_prefix}levels need one location for player start (s), there are {num_s}'
        assert num_g == 1, f'{assert_prefix}levels need one location for the goal (g), there are {num_g}'
        assert all(len(row) == len(rows[0]) for row in rows), f'{assert_prefix}all rows must be the same length'

    def load_level_file(self):
        with open(f'levels/{self.level_name}') as file:
            rows = [line.rstrip('\n') for line in file.readlines()]
            self._assert_level_integrity(rows)
            # make it read bottom up, so row/column indices can be used as 3d space coordinates
            rows.reverse()
            return Level(
                blocks=self._detect_environment(rows),
                start=self._find_char_pos(rows, TileSet.START),
                goal=self._find_char_pos(rows, TileSet.GOAL),
                coins=self._find_all_char_pos(rows, TileSet.COIN),
                enemies=self._find_all_char_pos(rows, TileSet.ENEMY)
            )

    def _find_char_pos(self, rows, char):
        for r_index, row in enumerate(rows):
            for c_index, tile in enumerate(row):
                if tile == char:
                    return c_index, 0, r_index

    def _find_all_char_pos(self, rows, char):
        positions = []
        for r_index, row in enumerate(rows):
            for c_index, tile in enumerate(row):
                if tile == char:
                    positions.append((c_index, 0, r_index))
        return positions

    def _detect_environment(self, level_text):
        blocks = []

        def default_info():
            return {'pos': (None, 0, None), 'width': 0}

        # scan all rows
        for row_index, row in enumerate(level_text):
            columns = list(row)
            scan_info = default_info()
            state = ScanState.SCANNING
            # scan all columns
            for column_index, tile in enumerate(columns):
                # process each tile until we've reached the end of a new contiguous block in this row
                state, scan_info, block_end = self._process_tile(tile, state, scan_info, row_index, column_index)
                # if we've reached the end of a new contiguous block then record it and start looking again
                if block_end:
                    blocks.append(scan_info)
                    scan_info = default_info()

            # don't miss out on blocks that end at the end of the row
            if scan_info['width'] > 0:
                blocks.append(scan_info)
        return blocks

    @staticmethod
    def _process_tile(tile, state, scan_info, row, column):
        """
        scanning FSM to map out contiguous blocks
        :param tile: the character representing the current process we're
        :param state: a ScanState value representing the previous state returned from this function
        :param scan_info: row/column/width of the current contiguous block we're traversing (if any)
        :param row: the current row index
        :param column: the current column index
        :return: (ScanState, scan_info, if_block_ended)
        """

        # if we've yet to encounter a new block, see if we've found one this time
        if state == ScanState.SCANNING:
            # mark this as the start of a new block
            if tile == TileSet.BLOCK:
                return ScanState.TRAVERSING_BLOCK, {'pos': (column, 0, row), 'width': 1}, False
            # still haven't found anything interesting, moving on
            elif tile != TileSet.BLOCK:
                return ScanState.SCANNING, scan_info, False

        # if we've been iterating over contiguous block tiles, keep checking how long it goes
        elif state == ScanState.TRAVERSING_BLOCK:
            # the block continues
            if tile == TileSet.BLOCK:
                scan_info['width'] += 1
                return ScanState.TRAVERSING_BLOCK, scan_info, False
            # we've reached the end of the block, let caller know to start over
            elif tile != TileSet.BLOCK:
                return ScanState.SCANNING, scan_info, True

