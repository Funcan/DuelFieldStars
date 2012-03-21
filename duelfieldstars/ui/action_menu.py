import pygame

from color import COLORS

from ui_abstract.menu import Menu
from ui_abstract.text import Text

from model import game

class ActionMenu (Menu):
    
    def __init__(self,rect, source, destination):
        super(ActionMenu,self).__init__(rect)
        
        self.source = source
        self.destination = destination
        self.showBuildMenu = True
        
        font = pygame.font.Font(pygame.font.get_default_font(), 12)
        dx = dy = 0
        "Name"
        name = str("Deep space at "+str(destination) )
        if destination in game.galaxy.planets:
            name = game.galaxy.planets[destination].name
            self.showBuildMenu = True

        
        widget = Text(pygame.Rect(dx,dy,0,0), font, COLORS["white"], name)
        self.options.append((widget,None,None))
        dy += 14
        
        
        
    def on_draw(self):
        "Calculate the size of the surface needed."
        width = 0
        height = 0
        for (widget,_,_) in self.options:
            if widget.width > width:
                width = widget.width
            height += widget.height
            
        self.surface = pygame.Surface((width,height))
        self.rect.width = self.surface.get_width()
        self.rect.height = self.surface.get_height() 
        self.surface.fill(COLORS["darkGray"])
        
        