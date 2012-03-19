

class Faction(object):
    """
    Represents a player controlled faction in the game.
    Stores lists of all their assets.
    """
    def __init__(self):

        self.name = "Foo Imperium"

        self.rez = 0 # Resources
        self.planets = [] # List of planets owned

        self.tech = {} # Table of tech levels by key

    @property
    def income(self):

        income = 0
        for planet in self.planets:
            income += planet.income
        return income

    def tick(self):
        """Update the faction by 1 turn."""
        self.rez += self.income

        for planet in self.planets:
            planet.tick


NOFACTION = Faction()
