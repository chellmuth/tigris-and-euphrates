class Special:
    pass

class Unification(Special):
    def db_form(self):
        return '?' + self.piece[0]

class Catastrophe(Special):
    def db_form(self):
        return '!'
