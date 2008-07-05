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
    
class FarmCiv(Civilization):
    def db_form(self):
        return 'f'

    def unique_id(self):
        return 'f' + str(self.id)

    def css_class_name(self):
        return 'farm'
    
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
    
class MerchantCiv(Civilization):
    def db_form(self):
        return 'm'

    def unique_id(self):
        return 'm' + str(self.id)

    def css_class_name(self):
        return 'merchant'
    
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
