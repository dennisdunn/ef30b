SEGMENT_TABLE = [[1,1,1,1,1,1,0],
                [0,1,1,0,0,0,0],
                [1,1,0,1,1,0,1],
                [1,1,1,1,0,0,1],
                [0,1,1,0,0,1,1],
                [1,0,1,1,0,1,1],
                [0,0,1,1,1,1,1],
                [1,1,1,0,0,0,0],
                [1,1,1,1,1,1,1],
                [1,1,1,0,0,1,1]]

SEGMENT_TABLE_DEFAULT = [0]*7

class LookupTable:
    """A lookup table with a default value."""
    def __init__(self, table, default):
        self._table = table
        self._default = default

    def get(self, value):
        try:
            return self._table[value]
        except:
            return self._default
        
    @staticmethod
    def create():
        return LookupTable(SEGMENT_TABLE,SEGMENT_TABLE_DEFAULT)
        