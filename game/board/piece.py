class Piece:
    is_ruler = False

class Civilization(Piece):
    is_treasure = False

    def __init__(self, id=None): # XXX FIXME
        self.id = id

class SettlementCiv(Civilization):
    def db_form(self):
        return 's'

    def unique_id(self):
        return 's' + str(self.id)

    def css_class_name(self):
        return 'settlement'
    
    def name(self):
        return 'civ-settlement'

class FarmCiv(Civilization):
    def db_form(self):
        return 'f'

    def unique_id(self):
        return 'f' + str(self.id)

    def css_class_name(self):
        return 'farm'
    
    def name(self):
        return 'civ-farm'

class TempleCiv(Civilization):
    def __init__(self, id=None, is_treasure=False):
        Civilization.__init__(self, id)
        self.is_treasure = is_treasure

    def db_form(self):
        return self.is_treasure and 'T' or 't'

    def unique_id(self):
        return 't' + str(self.id)

    def css_class_name(self):
        return 'temple'
    
    def name(self):
        return 'civ-temple'

class MerchantCiv(Civilization):
    def db_form(self):
        return 'm'

    def unique_id(self):
        return 'm' + str(self.id)

    def css_class_name(self):
        return 'merchant'
    
    def name(self):
        return 'civ-merchant'


class Ruler(Piece):
    is_ruler = True
    player_no = None
    def __init__(self, player_no):
        self.player_no = player_no

class SettlementRuler(Ruler):
    def db_form(self):
        return 'r' + self.player_no + 's'

    def name(self):
        return 'ruler-settlement'

class FarmRuler(Ruler):
    def db_form(self):
        return 'r' + self.player_no + 'f'

    def name(self):
        return 'ruler-farm'

class TempleRuler(Ruler):
    def db_form(self):
        return 'r' + self.player_no + 't'

    def name(self):
        return 'ruler-temple'

class MerchantRuler(Ruler):
    def db_form(self):
        return 'r' + self.player_no + 'm'

    def name(self):
        return 'ruler-merchant'

class Monument(Piece):
    pass

class GroundMonument(Monument):
    pass

class RiverMonument(Monument):
    pass
