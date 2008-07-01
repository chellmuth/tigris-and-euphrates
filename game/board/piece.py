class Piece:
    is_ruler = False


class Civilization(Piece):
    is_treasure = False

class SettlementCiv(Civilization):
    def db_form(self):
        return 's'

class FarmCiv(Civilization):
    def db_form(self):
        return 'f'

class TempleCiv(Civilization):
    def __init__(self, is_treasure=False):
        self.is_treasure = is_treasure

    def db_form(self):
        return self.is_treasure and 'T' or 't'

class MerchantCiv(Civilization):
    def db_form(self):
        return 'm'


class Ruler(Piece):
    is_ruler = True
    player_no = None
    def __init__(self, player_no):
        self.player_no = player_no

class SettlementRuler(Ruler):
    def db_form(self):
        return 'r' + self.player_no + 's'

class FarmRuler(Ruler):
    def db_form(self):
        return 'r' + self.player_no + 'f'


class TempleRuler(Ruler):
    def db_form(self):
        return 'r' + self.player_no + 't'

class MerchantRuler(Ruler):
    def db_form(self):
        return 'r' + self.player_no + 'm'


class Monument(Piece):
    pass

class GroundMonument(Monument):
    pass

class RiverMonument(Monument):
    pass
