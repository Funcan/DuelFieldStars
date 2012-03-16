"""
Contains the planet class, containing all data defining a world in the game's Galaxy.
"""

import random
import unittest
import math

import name

class Planet(object):
    def __init__(self, *position):
        self.name = name.name()
        
        self.baseValue = 0 # The planet's base value expressed as a percentile.
        self.currentValue = 0 # The planet's value after terraforming.
        self.realisedValue = 0 # The planet's presently realised value expressed as a percentile.
        self.growth = 0 # The planet's percentage growth per turn
        
        self.improvementLevels = [] # The planet's five mining improvement levels.
        self.realisedImprovement = 0 
        
        self.type = '' # The planet's type, expressed as one of the letters A, B, C, D or E.
        
        self.position = position # The planet's position expressed as an (x,y) tuple.
        return
    
    def generate(self,prng):
        self.baseValue = prng.randint(50,150)
        self.currentValue = self.baseValue
        self.growth = self.realisedValue = 0
        
        accumulator = prng.randint(1,20)
        self.improvementLevels = [accumulator]
        for _ in range(4):
            accumulator = accumulator + prng.randint(5,20)
            self.improvementLevels.append(accumulator)
        self.realisedImprovement = self.improvementLevels[0]
        
        self.type = prng.choice(['A','B','C','D','E'])
        return
    
    @property
    def income(self):
        income = self.realisedValue / float(100)
        for level in self.improvementLevels:
            if level <= self.realisedImprovement:
                income += 1
        return income

    def tick(self):
        """Update the planet by 1 turn."""
        self.realisedValue += self.growth

class PlanetTest(unittest.TestCase):
    def setUp(self):
        self.fixture = Planet(0,0)
        return
    
    def test_generation(self):
        self.fixture.generate(random.Random(0xDEADBEEF) )   
        return

NOPLANET = Planet()
