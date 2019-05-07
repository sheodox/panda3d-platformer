from enum import Enum, auto


class TileSet:
    BLOCK = 'b'
    AIR = '.'
    START = 's'
    GOAL = 'g'


class ScanState(Enum):
    TRAVERSING_BLOCK = auto()
    SCANNING = auto()


class WorldGen:
    def __init__(self, main):
        self.main = main

    def load_level_file(self, level_name):
        with open(f'levels/{level_name}.lvl') as file:
            rows = [line.rstrip('\n') for line in file.readlines()]
            self._detect_environment(rows)

    def _detect_environment(self, level_text):
        blocks = []

        def default_info():
            return {'row': None, 'column': None, 'width': 0}

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
        print(blocks)
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
        if state is ScanState.SCANNING:
            # mark this as the start of a new block
            if tile is TileSet.BLOCK:
                return ScanState.TRAVERSING_BLOCK, {'row': row, 'column': column, 'width': 1}, False
            # still haven't found anything interesting, moving on
            elif tile is not TileSet.BLOCK:
                return ScanState.SCANNING, scan_info, False

        # if we've been iterating over contiguous block tiles, keep checking how long it goes
        elif state is ScanState.TRAVERSING_BLOCK:
            # the block continues
            if tile is TileSet.BLOCK:
                scan_info['width'] += 1
                return ScanState.TRAVERSING_BLOCK, scan_info, False
            # we've reached the end of the block, let caller know to start over
            elif tile is not TileSet.BLOCK:
                return ScanState.SCANNING, scan_info, True


WorldGen('hi').load_level_file('level-1')
