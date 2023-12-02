
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
        