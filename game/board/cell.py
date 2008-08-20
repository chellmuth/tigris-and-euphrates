class Cell:
    piece = None
    special = None
    is_ground = False

    def __init__(self, piece=None, special=None):
        self.piece = piece
        self.special = special

    def db_form(self):
        special = self.special and self.special.db_form() or ''
        piece = self.piece and self.piece.db_form() or ''
        
        if special and '!' in special:
            return special

        return special + piece

    def has_piece(self):
        return self.piece is not None

    def has_special(self):
        return self.special is not None

    def has_ruler(self):
        return self.has_piece() and self.piece.is_ruler

    def treasure_info(self):
        if not (self.has_piece() and (not self.piece.is_ruler) and self.piece.treasure):
            return None

        return self.piece.treasure

    def css_class_name(self):
        return self.piece.css_class_name()

class Ground(Cell):
    is_ground = True

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
