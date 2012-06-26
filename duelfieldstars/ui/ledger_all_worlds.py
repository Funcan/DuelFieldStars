"""
A panel widget showing all worlds in the game.
May be filtered as All, Friend or Foe.
"""
from ui.ui_abstract.widget import Widget
from ui.ui_abstract.text import Text
import pygame
from color import COLORS
from model import game
from ui import texture_cache

class LedgerAllWorlds(Widget):
    ALL = object()
    FRIEND = object()
    FOE = object()
    
    def __init__(self,rect):
        super(LedgerAllWorlds,self).__init__(rect)
        
        self.tile_height = 1
        self.list_start = 0
        
        self.all_worlds_button = None
        self.friend_worlds_button = None
        self.foe_worlds_button = None
        self.scroll_up_button = None
        self.scroll_down_button = None
        
        self.show = self.ALL
    
        self.elements = [] # List of (Widget, Method, [args]) 3-tuples.
        
        x = y = 0
        font = pygame.font.Font(pygame.font.get_default_font(), 14)
        # Title
        def show_title(x,y):
            if self.show == self.ALL:
                string = "All worlds"
            elif self.show == self.FRIEND:
                string = "Your worlds"
            else:
                string = "Your rivals' worlds"
            widget = Text(pygame.Rect(x,y,0,0), font, COLORS["white"],
                          string)
            def nop():
                pass
            self.elements.append((widget,nop,[]))
            return (widget.width, widget.height)
        (dx,dy) = show_title(x,y)
        y += dy *1.5
        
        # Show all worlds
        def all_worlds_button(x,y):
            widget = Text(pygame.Rect(x,y,0,0), font, COLORS["white"],
                          "ALL")
            def clicked():
                self.show = self.ALL
                self.update()
            self.elements.append((widget,clicked,[]))
            return (widget.width, widget.height)
        (dx,dy) = all_worlds_button(x,y)
        x += dx *1.5
        
        # Filter friendly worlds
        def friend_worlds_button(x,y):
            widget = Text(pygame.Rect(x,y,0,0), font, COLORS["green"],
                          "FRIEND")
            def clicked():
                self.show = self.FRIEND
                self.update()
            self.elements.append((widget,clicked,[]))
            return (widget.width, widget.height)
        (dx,dy) = friend_worlds_button(x,y)
        x += dx *1.5
        
        # Filter enemy worlds
        def foe_worlds_button(x,y):
            widget = Text(pygame.Rect(x,y,0,0), font, COLORS["red"],
                          "FOE")
            def clicked():
                self.show = self.FOE
                self.update()
            self.elements.append((widget, clicked, []))
            return (widget.width, widget.height)
        (dx,dy) = foe_worlds_button(x, y)
        x = 0
        dy += dy *1.5
        
        self.list_start = dy # Start list from here.
        
        
    def on_draw(self):
        for (widget,_,_) in self.elements:
            self.surface.blit(widget.surface, widget.rect)
        
        # Draw list.
        y = self.list_start
        for world in game.galaxy.planets.values():
            if world.owner == None:
                pass
            elif self.show == self.FOE and world.owner == game.factions[0]:
                # Hide friends when filtering for foes.
                continue
            elif self.show == self.FRIEND and world.owner != game.factions[0]:
                # Hide foes when filtering for friends.
                continue
            dy = 0
            # Planet name
            if world.owner == game.factions[0]:
                color = COLORS["green"]
            else:
                color = COLORS["red"]
            string = world.name+" "+str(world.position)
            texture = texture_cache.text(None, 12, color, string)
            self.surface.blit(texture,(0,y+dy))
            dy += texture.get_height()
            
            # Income
            try:
                string = "    Income: "+str(world.income)+" rez/turn"
            except:
                string = "    No owner"
            texture = texture_cache.text(None,12,COLORS["white"],string)
            self.surface.blit(texture,(0,y+dy))
            dy += texture.get_height()
            
            # Construction
            string = "    Building: "+str(world.construction)
            texture = texture_cache.text(None,12,COLORS["white"],string)
            self.surface.blit(texture,(0,y+dy))
            dy += texture.get_height()
            
            # Next entry
            y += dy
            self.tile_height = dy
            
            