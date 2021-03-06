"""
Module to contain globals. 
Since only one game can be played at once a singleton seems appropriate.
"""
import logging
import pygame

from galaxy import Galaxy
import ship
import faction
from model import event_log

factions = []
ships = {}
galaxy = Galaxy()
turn_count = 1
game_mode = None

def check_elimination():
    accumulators = {}
    for faction in factions:
        accumulators[faction] = 0
    for world in galaxy.planets.values():
        if world.owner != None:
            accumulators[world.owner] += 1
    for faction in accumulators.keys():
        if accumulators[faction] < 1: # Eliminate factions with no worlds.
            faction.eliminate() 

# Generation parameters.
galaxy_size = (50,50)
world_density = float(1)/25
generation_seed = None
number_of_initial_factions = 2 

def set_galaxy_size(size):
    """Set the size of the game's galaxy."""
    global galaxy_size
    galaxy_size = size
def set_world_density(density):
    """Set the world generation density."""
    global world_density
    world_density = density
def set_galaxy_seed(seed):
    """Generate a particular galaxy."""
    global generation_seed
    generation_seed = seed    
def set_number_of_factions(num):
    """Set the number of player-character factions."""
    global number_of_initial_factions
    number_of_initial_factions = num
    
def init():
    global galaxy, factions, ships, turn_count
    global galaxy_size, world_density, generation_seed
    global number_of_initial_factions
    factions = []
    ships = {}
    (w,h) = galaxy_size
    galaxy = Galaxy(w,h, world_density, generation_seed)
    turn_count = 1
    # faction.PLAYERFACTION = factions[0]
    
    for _ in range(number_of_initial_factions):
        galaxy.add_player()
    
    for y in range(galaxy.height):
        for x in range(galaxy.width):
            ships[x,y] = []
            
    event_log.reset()

log = logging.getLogger(__name__)

def _do_end_of_turn():
    """End of turn processing."""
    global turn_count, ships
    log.debug("End of turn "+str(turn_count)+".")
    turn_count += 1
    
    event_log.reset()
    
    for faction in factions:
        faction.tick()
    for planet in galaxy.planets.values():
        planet.tick()
    ships = ship.process_ship_turn(ships)
    
    # Blockades
    for planet in galaxy.planets.values():
        for a in ships[planet.position]:
            if a.faction != planet.owner and a.attack >0 and planet.owner != None:
                # This planet is blockaded
                if planet.blockaded == False:
                    event_log.add(event_log.Event(planet.name+str(" blockaded"),
                                              planet.position,a.faction))
                planet.blockaded = True
                
    
    check_elimination()
    
    if len(factions) < 2:
        event = pygame.event.Event(pygame.USEREVENT,action="End of Game")
        pygame.event.post(event)
    
    event = pygame.event.Event(pygame.USEREVENT, action="End of Turn")
    pygame.event.post(event)
    


def end_of_turn(faction):
    """
    Mark a given faction's turn as complete.
    When all factions are marked as complete process the turn and resume.
    """
    
    ship.sensor_map_dirty = True
    
    faction.ready = True
    log.debug(faction.name+" marked ready.")
    
    def check():
        for faction in factions:
            if faction.ready == False:
                return False
        return True
            
    if check():
        _do_end_of_turn()
        for faction in factions:
            faction.ready = False
    return
    
