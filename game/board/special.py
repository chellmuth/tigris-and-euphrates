class Special:
    pass

class Unification(Special):
    def db_form(self):
        return '?'

class Catastrophe(Special):
    def db_form(self):
        return '!'
