class Cell:
    piece = None
    special = None

    def __init__(self, piece=None, special=None):
        self.piece = piece
        self.special = special

    def db_form(self):
        special = self.special and self.special.db_form() or ''
        piece = self.piece and self.piece.db_form() or ''
        
        if special and '!' in special:
            return special

        special + piece

class Ground(Cell):
    def db_form(self):
        special = self.special and self.special.db_form() or ''
        piece = self.piece and self.piece.db_form() or ''

        if special:
            return 'G' + special + piece
        if piece:
            return piece
        
        return 'G'

class River(Cell):
    def db_form(self):
        special = self.special and self.special.db_form() or ''
        piece = self.piece and self.piece.db_form() or ''

        if '?' == special:
            return 'R?'
        if '!' == special:
            return 'R!'
        if piece:
            return piece
        
        return 'R'
