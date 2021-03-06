import pygame
import logging

from ui_abstract.widget import Widget

import texture_cache

from color import COLORS
import model
from model import game
import assets
from assets.png import PNG

log = logging.getLogger(__name__)

class ViewportWidget(Widget):
    def __init__(self,rect,galaxy,window):
        super(ViewportWidget,self).__init__(rect)
        self.galaxy = galaxy
        self.window = window
        
        model.ship.sensor_map_dirty = True # Set sensor map for redraw.
        
        # model.ship.init_sensor_map() # Empty sensor map.
        
        # Jump to the player's homeworld on creation.
        event = pygame.event.Event(pygame.USEREVENT,action="go to homeworld")
        pygame.event.post(event)
        
        self.font = pygame.font.Font(pygame.font.get_default_font(),10)
        
        self.position = (0,0) # position in px
        self.velocity = (0,0) # position in px/ms
        self.scale = 32 # Px width of 1 pc
        
        self.selected = None # What is the user currently selecting?
        
        # Register key handlers.
        self.add_keyboard_handler(self.change_scroll_speed, pygame.KEYDOWN, pygame.K_w, 0, 0, -1) # Up.
        self.add_keyboard_handler(self.change_scroll_speed, pygame.KEYUP, pygame.K_w, 0, 0, 1) # Release.
        self.add_keyboard_handler(self.change_scroll_speed, pygame.KEYDOWN, pygame.K_s, 0, 0, 1) # Down.
        self.add_keyboard_handler(self.change_scroll_speed, pygame.KEYUP, pygame.K_s, 0, 0, -1) # Release.
        self.add_keyboard_handler(self.change_scroll_speed, pygame.KEYDOWN, pygame.K_a, 0, -1, 0) # Left.
        self.add_keyboard_handler(self.change_scroll_speed, pygame.KEYUP, pygame.K_a, 0, 1, 0) # Release.
        self.add_keyboard_handler(self.change_scroll_speed, pygame.KEYDOWN, pygame.K_d, 0, 1, 0) # Right.
        self.add_keyboard_handler(self.change_scroll_speed, pygame.KEYUP, pygame.K_d, 0, -1, 0) # Release.
        self.add_keyboard_handler(self.zoom, pygame.KEYDOWN, pygame.K_PAGEUP, 0, "in")
        self.add_keyboard_handler(self.zoom, pygame.KEYDOWN, pygame.K_PAGEDOWN, 0, "out")
        self.add_keyboard_handler(self.open_build_menu, pygame.KEYDOWN, pygame.K_b, 0)
        
        # Accelerators for openning ledgers
        self.add_keyboard_handler(self.open_event_list, pygame.KEYDOWN, pygame.K_e, pygame.KMOD_LALT)
        self.add_keyboard_handler(self.open_ship_list, pygame.KEYDOWN, pygame.K_s, pygame.KMOD_LALT)
        self.add_keyboard_handler(self.open_world_list, pygame.KEYDOWN, pygame.K_w, pygame.KMOD_LALT)
    
        
        # Mouse button handlers
        self.add_mouse_handler(self.click_left_mouse_button, pygame.MOUSEBUTTONDOWN, 1)
        self.add_mouse_handler(self.click_right_mouse_button, pygame.MOUSEBUTTONDOWN, 3)
        self.add_mouse_handler(self.zoom, pygame.MOUSEBUTTONDOWN, 4, "in") # Zoom in
        self.add_mouse_handler(self.zoom, pygame.MOUSEBUTTONDOWN, 5, "out") # Zoom out
        return
    
    def open_event_list(self):
        event = pygame.event.Event(pygame.USEREVENT, action="open event list")
        pygame.event.post(event)
    def open_world_list(self):
        event = pygame.event.Event(pygame.USEREVENT, action="open world list")
        pygame.event.post(event)
    def open_ship_list(self):
        event= pygame.event.Event(pygame.USEREVENT, action="open ship list")
        pygame.event.post(event)
            
    def on_draw(self):
        self.surface.fill((0,0,0))
        
        (x0,y0) = self.position
        
        width = self.width/self.scale
        height = self.height/self.scale
        
        # Draw coordinate grid
        white = (255,255,255)
        for y in range (self.scale, self.galaxy.height*self.scale, 3*self.scale):
            pygame.draw.line(self.surface, white, (0, y-y0), (self.width, y-y0) )
            label = self.font.render("("+str(y//self.scale)+")", True, white)
            self.surface.blit(label, (0,y-y0) )
        for x in range (self.scale, self.galaxy.width*self.scale, 3*self.scale):
            pygame.draw.line(self.surface, white, (x-x0, 0), (x-x0, self.height) )
            label = self.font.render("("+str(x//self.scale)+")", True, white)
            self.surface.blit(label, (x-x0,0) )
            
        # Draw movement lines.
        for ship in sum(game.ships.values(),[]):
            if ship.faction != game.factions[0]:
                continue
            (last_point_x, last_point_y) = (None, None)

            try:            
                for (_,target) in ship.orders:
                    if last_point_x == None:
                        (last_point_x,last_point_y) = ship.position
                    
                    path = model.ship.get_path((last_point_x, last_point_y), target)
                    # print path
                    
                    for (grid_x,grid_y) in path:
                        # Is ship 'selected'?
                        line_width = 1
                        if self.window.ship_list != None:
                            if ship in self.window.ship_list.selected:
                                line_width = 4
                        # Draw a line segment
                        line_start_x = last_point_x * self.scale - x0
                        line_start_y = last_point_y * self.scale - y0
                        line_end_x = grid_x * self.scale - x0
                        line_end_y = grid_y * self.scale - y0
                        #gradient = float(line_end_y - line_start_y)/(line_end_x - line_start_x)
                        pygame.draw.line(self.surface, COLORS["green"],
                                         (line_start_x,line_start_y),
                                         (line_end_x,line_end_y),
                                         line_width)
                            
                        last_point_x = grid_x
                        last_point_y = grid_y
            except ValueError:
                pass
            
                            
        # Draw ships in deep space.
        def draw_ships(x0, y0):
            for y in xrange( (y0/self.scale)*self.scale, self.height+y0+self.scale, self.scale):
                for x in xrange( (x0/self.scale)*self.scale, self.width+x0+self.scale, self.scale):
                    if x < 0 or y < 0 or x/self.scale >= game.galaxy.width or y/self.scale >= game.galaxy.height:
                        continue # Do nothing if value out of bounds.
                    tile = game.ships[(x/self.scale,y/self.scale)]
                    if tile == []:
                        continue # Do nothing if there are no ships.
                    friends = foes = 0
                    marine = colony = missile = service = False
                    enemy_marine = enemy_colony = enemy_missile = enemy_service = False
                    for ship in tile:
                        if ship.faction == game.factions[0]:
                            friends += 1
                            
                            flag = ship.faction.flag
                        
                            if ship.marines:
                                marine = True
                            if ship.colony:
                                colony = True
                            if ship.missile:
                                missile = True
                            if ship.service:
                                service = True
                        else:
                            # Skip if outside sensor range.
                            friendly_in_space = False
                            if friends > 0:
                                friendly_in_space = True
                            if (x,y) in game.galaxy.planets:
                                if game.galaxy.at(x,y).owner == game.factions[0]:
                                    friendly_in_space = True
                            if ship.invisible(game.factions[0]) and not friendly_in_space:
                                continue # This ship cannot be seen.
                            foes += 1
                            enemy_flag = ship.faction.flag
                            if ship.marines:
                                enemy_marine = True
                            if ship.colony:
                                enemy_colony = True
                            if ship.missile:
                                enemy_missile = True
                            if ship.service:
                                enemy_service = True
                        
                    if foes > 0: # FIXME: Rewrite this.
                        texture = texture_cache.ship_token(self.scale,
                                                           enemy_flag,
                                                           False, 
                                                           enemy_colony, 
                                                           enemy_marine, 
                                                           enemy_missile, 
                                                           enemy_service)
                        texture.set_colorkey((0x0,0x0,0x0))
                        count = texture_cache.text(None, 12, COLORS["red"],
                                                   str(foes))
                        if friends > 0 or game.galaxy.at(x/self.scale, y/self.scale) is not None:
                            # Draw off-center
                            self.surface.blit(texture, (x-x0-self.scale, y-y0-self.scale))
                            self.surface.blit(count, (x-x0-self.scale*2/3, y-y0-self.scale*2/3))
                        else:
                            # Draw centered
                            self.surface.blit(texture, (x-x0-self.scale/2,y-y0-self.scale/2))
                            self.surface.blit(count, (x-x0+self.scale/3, y-y0+self.scale/3))
                        

                    if friends > 0: # Draw friend tile
                        texture = texture_cache.ship_token(self.scale, flag, 
                                                           True, colony, marine, missile, service)
                        texture.set_colorkey((0x0,0x0,0x0))
                        count = texture_cache.text(None,12,COLORS["green"],str(friends))
                        
                        if foes > 0 or game.galaxy.at(x/self.scale, y/self.scale) is not None:
                            self.surface.blit(texture, (x-x0, y-y0)) # Blit off centre.
                            self.surface.blit(count, (x-x0+self.scale*2/3, y-y0+self.scale*2/3))
                        else: # Draw centered    
                            self.surface.blit(texture, (x-x0-self.scale/2,y-y0-self.scale/2))
                            self.surface.blit(count, (x-x0+self.scale/3, y-y0+self.scale/3))
                        
                        
                        
                        
        draw_ships(x0,y0)
        
        # Draw planets
        for y in range ( (y0/self.scale)*self.scale, self.height+y0+self.scale, self.scale):
            for x in range ( (x0/self.scale)*self.scale, self.width+x0+self.scale, self.scale):
                planet = self.galaxy.at(x/self.scale, y/self.scale)
                if planet is not None:
                    #(drawX, drawY) = (x - x0 - 0.25, y - y0 - 0.25)
                    #(drawX, drawY) = (drawX*self.scale, drawY*self.scale)
                    #rect = pygame.Rect(drawX, drawY, self.scale/2, self.scale/2)
                    (drawX, drawY) = (x-x0, y-y0)
                    rect = pygame.Rect(drawX-self.scale/4, drawY-self.scale/4, self.scale/2, self.scale/2)
                    
                    #Choose colour based on value
                    color = (255,255,0)
                    textColor = (0,0,0)
                    if planet.baseValue < 75:
                        color = (255,69,0)
                    if planet.baseValue > 125:
                        color = (64,64,255)
                        
                    # self.surface.fill(color,rect)
                    
                    "Draw the owner's flair"
                    if planet.owner is not None and model.ship.get_sensor_value(game.factions[0],planet.position) > -1:
                        (forgroundColor,backgroundColor) = planet.owner.flag
                        
                        texture = texture_cache.flag((self.scale,self.scale),forgroundColor,backgroundColor)
                        self.surface.blit(texture, (drawX-self.scale/2, drawY-self.scale/2))
                    
                    "Draw circle for the world"
                    texture = texture_cache.circle(self.scale/4,color)
                    self.surface.blit(texture, (drawX-self.scale/4, drawY-self.scale/4))
                    
                    font = pygame.font.Font(pygame.font.get_default_font(), self.scale/2-2)
                    label = font.render(planet.type_, True, textColor)
                    (labelWidth,labelHeight) = font.size(planet.type_)
                    self.surface.blit(label, (drawX-labelWidth/2, drawY-labelHeight/2))
                    
        "Blit fog of war"
        for y in range ( (y0/self.scale)*self.scale, self.height+y0+self.scale, self.scale):
            for x in range ( (x0/self.scale)*self.scale, self.width+x0+self.scale, self.scale):
                (drawX, drawY) = (x-x0, y-y0) # x,y in SDL space.
                (tileX,tileY) = (x/self.scale, y/self.scale) # x,y in game space. 
                if tileX < 0 or tileY < 0 or tileX > game.galaxy.width-1 or tileY > game.galaxy.height-1:
                    continue # Bounds checking.    
                if model.ship.get_sensor_value(game.factions[0], (tileX,tileY)) < 0:
                    texture = assets.get(PNG, "fog_"+str(self.scale))
                    texture.set_alpha(128)
                    self.surface.blit(texture, (drawX - self.scale/2, drawY - self.scale/2))
                    
        "Draw selection box"
        if self.selected is not None:
            texture = texture_cache.rect((self.scale, self.scale), COLORS["white"], 3)
            (translateX, translateY) = self.position
            (drawX, drawY) = self.selected
            (drawX, drawY) = (drawX*self.scale, drawY*self.scale)
            (drawX, drawY) = (drawX - translateX - self.scale/2, drawY - translateY - self.scale/2) 
            self.surface.blit(texture, (drawX, drawY) )


        return
    
    def on_tick(self, deltaTime):
        # Check that movement keys are depressed, else reset speed.
        keys = pygame.key.get_pressed()
        if not keys[pygame.K_w] and not keys[pygame.K_s]:
            (dx,dy) = self.velocity
            dy = 0
            self.velocity = (dx,dy)
            
        if not keys[pygame.K_a] and not keys[pygame.K_d]:
            (dx,dy) = self.velocity
            dx = 0
            self.velocity = (dx,dy)
        
        # Calculate new position.
        if deltaTime > 10:
            deltaTime = 10
        (x,y) = self.position
        (dx,dy) = self.velocity
        (x,y) = (x + dx * deltaTime, y + dy * deltaTime)


        # Generate event (and thus bypass niceness) if velocity != 0
        if dx != 0 or dy != 0:
            event = pygame.event.Event(pygame.USEREVENT+1, action="Viewport moving")
            pygame.event.post(event)
                
        # Snap to edge if outside bottom right boundary
        if (x + self.width) > self.galaxy.width*self.scale:
            x = self.galaxy.width*self.scale - self.width
        if (y + self.height) > self.galaxy.height*self.scale:
            y = self.galaxy.height*self.scale - self.height
        # Snap to edge if outside topleft boundary
        if x < 0:
            x = 0
        if y < 0:
            y = 0
        
        self.position = (x,y)
        self.update()
    
    def on_mouse(self,event):
        if event.type == pygame.MOUSEMOTION and event.buttons == (1,0,0):
            (x,y) = self.position
            (dx,dy) = event.rel
            self.position = (x-dx,y-dy)
            return True
            
    def click_left_mouse_button(self):
        (mouseX, mouseY) = pygame.mouse.get_pos()
        (viewX, viewY) = self.position
        (mouseX, mouseY) = (mouseX - self.x0 + viewX, mouseY - self.y0 + viewY)
        def rounddiv(a,b):
            return a // b + (1 if a%b >= b // 2 else 0)
        (x, y) = (rounddiv(mouseX,self.scale), rounddiv(mouseY,self.scale) ) # Where in the map the click occured.
        
        self.selected = (x, y)
        
        """planet = None
        if (x,y) in self.galaxy.planets:
            planet = self.galaxy.planets[(x,y)]
        if planet is not None:
            event = pygame.event.Event(pygame.USEREVENT, action="Open planet", planet=planet)
            pygame.event.post(event)
        else:
            log.debug("No planet to open at "+str((x,y) ) )"""
        event = pygame.event.Event(pygame.USEREVENT, action="selection", selection=self.selected)
        pygame.event.post(event)
        
    def click_right_mouse_button(self):
        (mouseX, mouseY) = pygame.mouse.get_pos()
        (viewX, viewY) = self.position
        (mouseX, mouseY) = (mouseX - self.x0 + viewX, mouseY - self.y0 + viewY)
        x = mouseX / self.scale + (1 if mouseX % self.scale >= self.scale/2 else 0)
        y = mouseY / self.scale + (1 if mouseY % self.scale >= self.scale/2 else 0)
        
        event = pygame.event.Event(pygame.USEREVENT, action="open menu", selection=(x,y))
        pygame.event.post(event) 
            
    def change_scroll_speed(self, d2X, d2Y):
        (dx,dy) = self.velocity
        (dx,dy) = (dx+d2X, dy+d2Y)
            
        self.velocity = (dx,dy)
         
    def zoom(self, string):
        (mouseX, mouseY) = pygame.mouse.get_pos()
        (x,y) = self.position
        (mouseX, mouseY) = (mouseX + x - self.x0, mouseY + y - self.y0)
        (mouseX, mouseY) = (mouseX/self.scale, mouseY/self.scale)
        
        if string == "in":
            self.scale = self.scale * 2
            if self.scale > 64:
                self.scale = 64
                
        if string == "out":
            self.scale = self.scale /2
            if self.scale < 8:
                self.scale = 8
                
        (mouseX, mouseY) = (mouseX * self.scale, mouseY * self.scale)
        self.position = (mouseX - self.width/2, mouseY - self.height/2)
        
        self.update()    
    
    def open_build_menu(self):
        try:
            if game.galaxy.at(*self.selected).owner != game.factions[0]:
                return True
            
            event = pygame.event.Event(pygame.USEREVENT, 
                                       destination=self.selected, 
                                       action="open build menu" 
                                       )
            pygame.event.post(event)
            return True
        except:
            return True
                
            
        
