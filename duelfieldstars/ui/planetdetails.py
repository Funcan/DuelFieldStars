import pygame

from ui_abstract.widget import Widget

import texture_cache
from color import COLORS
from ui.ui_abstract.button import Button
from model import game
from assets.png import PNG
import assets
from model.ship import get_sensor_value

fontSize = 16

class PlanetDetails(Widget):
    """
    Simple panel containing details about a selected planet.
    """
    def __init__(self,rect,planet):
        super(PlanetDetails,self).__init__(rect)
        
        self.planet = planet
        self.cancel_button = None
        
        
        
    def on_draw(self):
        self.surface.fill((205,205,193))
        
        detected = get_sensor_value(game.factions[0], self.planet.position) > 0
        
        y = 0
        
        # Header
        texture = texture_cache.text(None, fontSize, COLORS["black"], 
                                     "Planet at "+str(self.planet.position)+":")
        self.surface.blit(texture,(0,y))
        y += 14
        
        if not detected:
            texture = texture_cache.text(None, fontSize, COLORS["black"],
                                         self.planet.starname)
            self.surface.blit(texture, (0,y))
            y += 14
        else:
            texture = texture_cache.text(None, fontSize, COLORS["blue"], 
                                         self.planet.name)
            self.surface.blit(texture, (0,y))
            y += 14

        # Owner
        if self.planet.owner != None and detected:
            texture = texture_cache.text(None, fontSize, COLORS["black"],
                                         "Faction: ")
            self.surface.blit(texture, (0,y))
            
            texture = texture_cache.text(None, fontSize, COLORS["blue"],
                                         self.planet.owner.name)
            self.surface.blit(texture, (50,y))
        y += 14
        
        # Type
        texture = texture_cache.text(None, fontSize, COLORS["black"],
                                     "Type, ")
        self.surface.blit(texture, (20,y))
        
        texture = texture_cache.text(None, fontSize, COLORS["black"],
                                     self.planet.type_)
        self.surface.blit(texture, (self.width-100,y))
        y += 14
        
        # Value
        texture = texture_cache.text(None, fontSize, COLORS["black"],
                                     "Value, ")
        self.surface.blit(texture, (20,y))
        if detected:
         
            color = COLORS["black"]
            if self.planet.currentValue < 75:
                color = COLORS["red"]
            if self.planet.currentValue > 125:
                color = COLORS["blue"]
            
            texture = texture_cache.text(None, fontSize, color,
                                         str(self.planet.currentValue)+"%")
            self.surface.blit(texture, (self.width-100,y,0,0))
        
        color = COLORS["black"]
        if self.planet.baseValue < 75:
            color = COLORS["red"]
        if self.planet.baseValue > 125:
            color = COLORS["blue"]
            
        texture = texture_cache.text(None, fontSize, color,
                                     "("+str(self.planet.baseValue)+"%)")
        self.surface.blit(texture, (self.width-50,y))
        y += 14
        
        # Realisation
        if self.planet.owner != None and detected:
            
            texture = texture_cache.text(None, fontSize, COLORS["black"],
                                         "Realisation, ")
            self.surface.blit(texture, (20,y))
            color = COLORS["black"]
            if self.planet.realisedValue < 75:
                color = COLORS["red"]
            if self.planet.realisedValue > 125:
                color = COLORS["blue"]
                
            texture = texture_cache.text(None, fontSize, color,
                                         str(self.planet.realisedValue)+"%")
            self.surface.blit(texture, (self.width-75,y))
        y += 14
        
        # Growth
        
        
        
        if self.planet.owner != None and detected:
            
            texture = texture_cache.text(None, fontSize, COLORS["black"],
                                     "Growth, ")
            self.surface.blit(texture, (20,y))
            
            texture = texture_cache.text(None, fontSize, COLORS["black"],
                                         "+"+str(self.planet.growth)+"%")
            self.surface.blit(texture, (self.width-100,y))
                
        y += 14
        
        # Income
        if self.planet.owner != None and detected:
            
            texture = texture_cache.text(None, fontSize, COLORS["black"],
                                         "Income, ")
            self.surface.blit(texture, (20,y))
            
            texture = texture_cache.text(None, fontSize, COLORS["black"],
                                         str(self.planet.income)+" rez/turn")
            self.surface.blit(texture, (self.width-75,y))
        y += 14
        
        # Construction?
        if self.planet.owner == game.factions[0]:
            texture = texture_cache.text(None, fontSize, COLORS["black"],
                                       "Building... ")
            self.surface.blit(texture, (20,y))
        
            if self.planet.construction == None:
                texture = texture_cache.text(None,fontSize,COLORS["black"],
                                             "Nothing")
                self.surface.blit(texture, (self.width-75,y))
                self.cancel_button = None
            else:
                
            
                # Cancel button
                def cancel_construction():
                    self.planet.construction = None
                    self.planet.owner.rez += 2
                    event = pygame.event.Event(pygame.USEREVENT+2,action = "cancelled construction")
                    pygame.event.post(event)
                texture = assets.get(PNG,"cancel_32")
                self.cancel_button = Button(pygame.Rect(self.width-40,y,32,32), texture, texture, cancel_construction)
                self.cancel_button._draw()
                self.surface.blit(self.cancel_button.surface, self.cancel_button.rect)
                y += 14
                texture = texture_cache.text(None,fontSize,COLORS["blue"],
                                                 self.planet.construction.type_)
                self.surface.blit(texture, (20,y))
            
        
        y += 14
        
        # Space
        y += 14
                
        # Improvement Levels
        if self.planet.owner == game.factions[0]:
            texture = texture_cache.text(None, fontSize, COLORS["black"],
                                         "Mining Improvement Levels")
            self.surface.blit(texture, (0,y))
            y += 14
            x = 14
            for level in self.planet.improvementLevels:
                if level <= self.planet.realisedImprovement:
                    color = COLORS["blue"]
                else:
                    color = COLORS["red"]
                    
                texture = texture_cache.text(None, fontSize, color,
                                             str(level) )
                self.surface.blit(texture, (x,y))
                x += 28
        y += 14
        
        # Space
        y += 14
        
        # Ships in tile
        #if game.ships[self.planet.position] != []:
        if True:
            # Number of ships
            #texture = texture_cache.text(None, fontSize, COLORS["black"],
            #                              str(len(game.ships[self.planet.position]))+" ship(s) in orbit")
            #self.surface.blit(texture, (0,y))
            y += 14
            shiplist_y = y
            (shiplist_x,_,_,_) = self.rect
            shiplist_x += 5
            shiplist_height = self.surface.get_height() - shiplist_y - 5
            shiplist_width = self.surface.get_width() - 10
            #print (shiplist_x, shiplist_y, shiplist_width, shiplist_height)
            
            event = pygame.event.Event(pygame.USEREVENT, action="show embedded ship list", position=self.planet.position,
                                       rect=pygame.Rect(shiplist_x,shiplist_y,shiplist_width,shiplist_height))
            pygame.event.post(event)
        else:
            event = pygame.event.Event(pygame.USEREVENT, action="hide embedded ship list")
            pygame.event.post(event)
            
    def on_mouse(self,event):
        # Call cancel button on click.
        if self.cancel_button != None:
            (x,y) = event.pos
            (widget_x,widget_y,_,_) = self.rect
            x = x - widget_x
            y = y - widget_y
            if self.cancel_button.rect.colliderect(pygame.Rect(x,y,0,0)):
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    return self.cancel_button._mouse(event)
            