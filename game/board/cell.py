class Cell:
    piece = None
    special = None

class Ground(Cell):
    def db_form(self):
        return 'G'

class River(Cell):
    def db_form(self):
        return 'R'
