import name

import game
import logging
import math
import random
from model.faction import Faction

log = logging.getLogger(__name__)

def get_path(source,destination):
    """
    Obtain and return a list of the coordinates of all tiles between two points.
    """
    values = []
    (x0,y0) = source
    (x1,y1) = destination
    
    dx = x1 - x0
    dy = y1 - y0
    if dx == 0:
        gradient = dy
    else:
        if dx > 0:
            gradient = float(dy)/dx
        else:
            gradient = -float(dy)/dx
    error = 0.0
    y = y0
    
    def my_range(a,b):
        if a < b:
            return range(a,b)
        if a > b:
            return range(a,b,-1)
        if a == b:
            return [a]
    
    #print (x0,x1)
    #print gradient
    #print my_range(x0,x1)
    for x in my_range(x0,x1):
        values.append((x,y))
        error += gradient
        while error > 0.5:
            y +=1
            if error > 1.5:
                values.append((x,y))
            error -=1
        while error < -0.5:
            y -=1
            if error < -1.5:
                values.append((x,y))
            error +=1
    values.append(destination)
    return values
        
class Ship(object):
    """Abstract class for space ships."""
    type_ = "error"
    offenseValue = 0
    defenseValue = 2
    max_kill_chance = 0.5
    marines = False
    colony = False
    missile = False
    service = False
        
    def __init__(self,faction,position):
        self.faction = faction
        self.position = position # Position in pc
        self.name = name.ship_name()
        
        self.path = []
        
        self.damaged = False # True if the ship is damaged.
        
        #self.destination = self.position # Target destination.
        self.orders = [] # List of orders.
        
        game.ships[position].append(self)
                
    @property
    def attack(self): 
        """Returns the attack value modified by tech levels."""
        return round(self.offenseValue * math.sqrt(self.faction.tech["Space Weapons Technology"]),2)
    @property
    def owner(self):
        return self.faction
    @property
    def defence(self): 
        """Returns the defence value modified by tech levels."""
        return round(self.defenseValue * math.sqrt(self.faction.tech["Space Defence Technology"]),2)
    @property
    def speed(self): 
        """Speed in pc, modified by tech levels."""
        return 2 + math.sqrt(self.faction.tech["Engine Technology"])
    
    @property
    def ground_combat_value(self):
        if self.marines:
            return 2 * math.sqrt(self.faction.tech["Ground Combat Technology"])
        return 0
    
    def tick(self):
        """Process a turn."""
        return
    

def check_for_combat(x, y):
    ships = game.ships[(x,y)]
    factions = []
    for ship in ships:
        if ship.faction in factions:
            continue
        factions.append(ship.faction)
        if len(factions) > 1:
            return True # There will be a fight!
    return False
             
        
def resolve_combat(x, y):
    fleets = {} # Group ships by their faction.
    ships = game.ships[(x,y)]
    for ship in ships:
        ship.end_of_turn = True # Fighting ships take no
        # other action.
        if ship.faction in fleets.keys():
            fleets[ship.faction].append(ship)
        else:
            fleets[ship.faction] = [ship]
    attack_value = {} # Calculate per-fleet attack value
    defence_value = {} # Calculate per-fleet defence
    
    destroyed_ships = [] # Place ships to be killed here.
    
    for (faction,fleet) in fleets.items(): # Calculate per-fleet values
        fleet_attack = 0
        fleet_defence = 0
        for ship in fleet:
            fleet_attack += ship.attack
            fleet_defence += ship.defence
        attack_value[faction] = fleet_attack
        defence_value[faction] = fleet_defence
    
    for attacker in fleets.keys(): # Resolve your attack.
        for defender in fleets.keys():
            if attacker == defender:
                continue # Don't attack yourself.
            
            kill_chance = attack_value[attacker] / defence_value[faction]
            
            for ship in fleets[defender]:
                hits = 0
                a = kill_chance
                while a > 0:
                    if a > ship.max_kill_chance:
                        if random.random() < ship.max_kill_chance: # score a hit
                            hits += 1
                    else:
                        if random.random() < a: # score a hit
                            hits +=1
                    a -= ship.max_kill_chance
                
                log.debug(str(hits)+" hits scored on "+ship.name+" ("+ship.faction.name+")")
                for _ in range (hits):
                    if random.random() < 0.5: # Destroy
                        destroyed_ships.append(ship)
                        log.debug("----She is destroyed.")
                    else: # Damage
                        ship.damaged = True
                        log.debug("----She is damaged.")
                        
    for ship in destroyed_ships: # Remove destroyed ships from play.
        try:
            game.ships[ship.position].remove(ship)
        except:
            pass
                    
def resolve_ground_attack(ship):
    ship.end_of_turn = True # Attacking ends your movement.
    (x,y) = ship.position
    planet = game.galaxy.at(x,y)
    planet.sieged = True
    attacker = ship.ground_combat_value
    defender = planet.ground_combat_value
    
    kill_chance = float(attacker) / defender
    
    def hit_scored(attacker,planet):
        if attacker == planet.owner:
            return # Don't kill your own marines!
        log.debug("Defender on "+planet.name+" died gallantly.")
        planet.marines -= 1
        planet.realisedValue -= 1
        if planet.marines < 1:
            log.debug("Planet has been captured!")
            planet.owner = attacker
            planet.marines = 1
    while kill_chance > 0:
        if kill_chance > ship.max_kill_chance:
            if random.random() < ship.max_kill_chance:
                hit_scored(ship.faction, planet)
        else:
            if random.random() < kill_chance:
                hit_scored(ship.faction, planet)
        kill_chance -= ship.max_kill_chance
                
    
    
                    
    
        



def process_ship_turn(ships):
        """Takes a list of ships and iterates over them to produce the new ship state."""
        # Get the top speed to determine how many microticks there will be.
        def get_fastest(ships):
            fastest = 0
            for ship in sum(ships.values(),[]):
                ship.micro_movement = 0 # prepare them for the next step.
                ship.end_of_turn = False
                ship.path = [] # Force repopulation in the next step.
                if ship.speed > fastest:
                    fastest = ship.speed
                    
            return fastest
        top_speed = float(get_fastest(ships))
        
        # Iterate over all ships and perform a single microtick/move. 
        def do_microtick(top_speed, ships):
            for ship in sum(ships.values(),[]):
                ship.micro_movement += ship.speed / top_speed
                if ship.micro_movement < 1:
                    continue # Skip the rest of this function if the ship isn't
                    # fast enough
                if ship.end_of_turn:
                    continue # Skip the rest of this function if
                    # the ship engaged in combat.
                ship.micro_movement -= 1
                
                # Check tactics and combat
                (x,y) = ship.position
                if check_for_combat(x,y):
                    if ship.attack == 0:
                        pass # Colony ships escape.
                    else:
                        resolve_combat(x,y)
                        continue # Forfeit rest of turn.
                
                # Perform orders
                if ship.orders != []:
                    try:
                        (order, target) = ship.orders[0]
                    except ValueError:
                        (order) = ship.orders[0]
                        target = None
                    if order == "scrap": # Scrap ship.
                        ships[ship.position].remove(ship)
                        ship.faction.rez += 2 # Refund part of the cost, adjusted for upkeep taken.
                        continue
                    if order == "move to": # Do movement
                        if ship.path == []:
                            ship.path = get_path(ship.position, target)
                            ship.path.pop(0)
                    
                        ships[ship.position].remove(ship)
                        ship.position = ship.path.pop(0)
                        ships[ship.position].append(ship)
                        if target == ship.position:
                            ship.orders.pop(0) # If position = target, cycle to next order.
                    if order == "colony here": # Do colonisation
                        if game.galaxy.at(*target).owner != None:
                            log.debug("Planet at "+str(target)+" already colonised.")
                            ship.orders.pop(0) # If planet is already colonised
                            # then cycle to next order.
                            continue
                        def colonisable(ship,target):
                            return game.galaxy.at(*target).type_ in ship.owner.colony_types
                        if target == ship.position and colonisable(ship,target):
                            game.galaxy.at(*target).set_owner(ship.faction)
                            game.galaxy.at(*target).name = ship.name.split(' ',1)[1]
                            ships[ship.position].remove(ship)
                            continue
                        ship.orders.pop(0) # If all else fails, skip the order.
                    if order == "assault planet": # Space Marine attack
                        if game.galaxy.at(*target).realisedValue == 0:
                            log.debug("Planet at "+str(target)+" seems to have been glassed.")
                            ship.orders.pop(0) # If colony destroyed then cycle to
                            # next order.
                            continue
                        resolve_ground_attack(ship)
                        if game.galaxy.at(*target).owner == ship.faction: # Were we successful?
                            ship.orders.pop(0) # End the attack once we have won.
                        
                            
                    
                    
            return ships
        for i in range (0, int(top_speed)):
            ships = do_microtick(top_speed, ships)
        
        return ships
    
class Cruiser(Ship):
    """This class represents a Cruiser"""
    type_ = "Cruiser"
    offenseValue = 2
    defenseValue = 2
    marines = False
    colony = False
    service = False
    missile = False
    
    def __init__(self,faction,position):
        super(Cruiser,self).__init__(faction,position)
        
class MarineTransport(Ship):
    """This class represents a ground assault ship."""
    type_ = "Marine Transport"
    offenseValue = 1
    defenseValue = 2
    marines = True
    colony = False
    
    def __init__(self,faction,position):
        super(MarineTransport,self).__init__(faction,position)
        
class ColonyTransport(Ship):
    """This class represents a colony ship."""
    type_ = "Colony Transport"
    offenseValue = 0
    defenseValue = 2
    marines = False
    colony = True
    
    def __init__(self,faction,position):
        super(ColonyTransport,self).__init__(faction,position)

if __name__ == '__main__': # Test combat resolution.
    print "Test combat resolution."
    logging.basicConfig(level=logging.DEBUG)
    game.init()
    Cruiser(Faction(),(0,0))
    Cruiser(Faction(),(0,0))
    resolve_combat(0,0)
