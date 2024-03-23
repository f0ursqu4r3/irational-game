import pygame
import sys
import random
import math
from scripts.entities import physicsEntity, Player, enemy
from scripts.utilities import load_image, load_images, Animation, Async_clock
from scripts.tilemap import Tilemap
from scripts.cloud import Clouds
from scripts.paticle import Particle
from scripts.spark import Spark
import scripts.menus

import asyncio
#screen shake, 5:12:00, could be a coll effect later but dont need it now
pygame.init()
posA = [2560, 1440]
screen = pygame.display.set_mode((posA[0], posA[1]), pygame.RESIZABLE) 
screen_rect = screen.get_rect()
posB = [1280, 720]
display = pygame.Surface((posB[0], posB[1]))
display_rect = display.get_rect()

# last worked at 4:30:00

class Game: #the game lol     
    def __init__(self):        
        pygame.init()

        pygame.display.set_caption('Irrational Game') #bname of the winodw
        
        self.game_pause = False
        
        self.display = pygame.Surface((posB[0], posB[1]))# at 47 min in video, he said hes doing this way for control but you can get more preformance with pygame stuffs
        
        self.clock = pygame.time.Clock()
         #used to reference frame rate limit near the bottom
        
        self.movement = [False, False]
        
        self.font = pygame.font.SysFont("Arial" , 18 , bold = True)

        
        self.assets = { #theres ways to load more assests at once, by writing a loaderthing, this is a starter method
            'decor' : load_images('tiles/decor'),
            'grass' : load_images('tiles/grass'),
            'stone' : load_images('tiles/stone'),
            'large_decor' : load_images('tiles/large_decor'), 
            'player' : load_image('entities/player.png'),
            'background' : load_image('background.png'),
            'clouds': load_images('clouds'),
            'player/idle' : Animation(load_images('entities/player/idle'), img_dur=6),
            'player/run' : Animation(load_images('entities/player/run'), img_dur=4),
            'player/jump' : Animation(load_images('entities/player/jump'), img_dur=5),
            'player/slide' : Animation(load_images('entities/player/slide'), img_dur=5),
            'player/wall_slide' : Animation(load_images('entities/player/wall_slide'), img_dur=5),
            'particle/leaf' : Animation(load_images('particles/leaf'), img_dur=20, loop=False),
            'particle/particle' : Animation(load_images('particles/particle'), img_dur=6, loop=False),
            'enemy/idle' : Animation(load_images('entities/enemy/idle'), img_dur=6),
            'enemy/run' : Animation(load_images('entities/enemy/run'), img_dur=4),
            'gun' : load_image('gun.png'),
            'projectile' : load_image('projectile.png'),
            'resume' : load_image('button/button_resume.png'),
        }# could for loop if tons of images  56:35, 
        
        self.clouds = Clouds(self.assets['clouds'], count=16)
        
        self.player = Player(self, (50, 50), (8, 15)) #also the player
        
        self.tilemap = Tilemap(self, 16) #could change
        self.level = 'map2'
        self.load_level(3)
        
    def fps_counter(self):
        fps = str(int(self.clock.get_fps()))
        fps_t = self.font.render(fps , 1, pygame.Color("RED"))
        display.blit(fps_t,(0,0))
        
    def get_font(size): # Returns Press-Start-2P in the desired size
        return pygame.font.Font("assets/font.ttf", size)   
        
    def load_level(self, map_id):
        self.tilemap.load('data/maps/' + str(map_id) + '.json')
        
        self.leaf_spawners = []
        for tree in self.tilemap.extract([("large_decor", 2)], keep=True):
            self.leaf_spawners.append(pygame.Rect(4 + tree['pos'][0], 4 + tree['pos'][1], 23, 13))
          
        self.enemies = []  
        for spawner in self.tilemap.extract([('spawners', 0), ('spawners', 1)]):
            if spawner['variant'] == 0:
                self.player.pos = spawner['pos'] #4:19:00
                self.player.air_time = 0
            else:
                self.enemies.append(enemy(self, spawner['pos'], (8, 15)))
            
        self.projectiles = []   
        self.particles = []
        self.sparks = []
        
        self.scroll = [0,0]
        self.dead = 0
            
            
        
    async def run(self): #game running funct
        while True:
            
            self.display.blit(pygame.transform.scale(self.assets['background'], self.display.get_size()), (0, 0)) #back ground color
            
            if self.game_pause == True:
                menu()         
                            
            else:
                
                if self.dead:
                    self.dead += 1
                    if self.dead > 200:
                        self.load_level(3)
                    
                
                self.scroll[0] += (self.player.rect().centerx - self.display.get_width() / 2 - self.scroll[0]) / 30 
                self.scroll[1] += (self.player.rect().centery - self.display.get_height() / 2 - self.scroll[1]) / 30
                render_scroll = (int(self.scroll[0]), int(self.scroll[1]))
                
                for rect in self.leaf_spawners:
                    if random.random() * 200000 < rect.width * rect.height:
                        pos = (rect.x + random.random() * rect.width, rect.y + random.random() * rect.height)
                        self.particles.append(Particle(self, 'leaf', pos, velocity=[0.15, 0.3], frame=random.randint(0, 20)))
                
                self.clouds.update()
                self.clouds.render(self.display, offset=render_scroll)
                
                
                self.tilemap.render(self.display, offset=render_scroll)
                
                for enemy in self.enemies.copy():
                    kill = enemy.update(self.tilemap, (0, 0))
                    enemy.render(self.display, offset=render_scroll)
                    if kill:
                        self.enemies.remove(enemy)
                    
                if not self.dead:
                    self.player.update(self.tilemap, (self.movement[1] - self.movement[0], 0))
                    self.player.render(self.display, offset=render_scroll)
                #[[x, y], direction, timer]
                for projectile in self.projectiles.copy():
                    projectile[0][0] += projectile[1] #could be a object, it will need to be i think for a skill editor
                    projectile[2] += 1
                    img = self.assets['projectile']
                    self.display.blit(img, (projectile[0][0] - img.get_width() / 2 - render_scroll[0], projectile[0][1] - img.get_height() / 2 - render_scroll[1]))
                    if self.tilemap.solid_check(projectile[0]):
                        self.projectiles.remove(projectile)
                        for i in range(4):
                            self.sparks.append(Spark(projectile[0], random.random() - 0.5 + (math.pi if projectile[1] > 0 else 0), 2 + random.random()))
                    elif projectile[2] > 360:
                        self.projectiles.remove(projectile)
                    elif abs(self.player.dashing) < 50:#invincability frames basically 4:36:00
                        if self.player.rect().collidepoint(projectile[0]):
                            self.projectiles.remove(projectile)
                            self.dead += 1
                            for i in range(30):
                                angle = random.random() * math.pi * 2
                                speed = random.random() * 5
                                self.sparks.append(Spark(self.player.rect().center, angle, 2 + random.random()))
                                self.particles.append(Particle(self, 'particle', self.player.rect().center, velocity=[math.cos(angle + math.pi) * speed * 0.5, math.sin(angle + math.pi) * speed * 0.5], frame=random.randint(0, 7)))
        
                for spark in self.sparks.copy():
                    kill = spark.update()
                    spark.render(self.display, offset=render_scroll)       
                    if kill:
                        self.sparks.remove(spark) 
                
                for particle in self.particles.copy():
                    kill = particle.update()
                    particle.render(self.display, offset=render_scroll)
                    if particle.type == 'leaf':
                        particle.pos[0] += math.sin(particle.animation.frame * 0.035 ) *.3
                    if kill:
                        self.particles.remove(particle)
                
                for event in pygame.event.get():
                    if event.type == pygame.QUIT: # ability to close
                        pygame.quit()
                        sys.exit()
                        
                    if event.type == pygame.KEYDOWN: #controls
                        if event.key == pygame.K_a:
                            self.movement[0] = True
                        if event.key == pygame.K_d:
                            self.movement[1] = True
                        if event.key == pygame.K_SPACE:
                            self.player.jump() #- equals up
                        if event.key == pygame.K_LSHIFT:
                            self.player.dash()
                        if event.key == pygame.K_ESCAPE:
                            self.game_pause = True
                    if event.type == pygame.KEYUP:
                        if event.key == pygame.K_a:
                            self.movement[0] = False
                        if event.key == pygame.K_d:
                            self.movement[1] = False
                            
                
                screen.blit(pygame.transform.scale(self.display, screen.get_size()), (0 , 0)) #scaling the base image larger for p[ixel art effect]
                pygame.display.update()
                self.clock.tick(60)
                self.fps_counter()
                
                
def menu():
        def get_font(size): # Returns Press-Start-2P in the desired size
            return pygame.font.Font("data/font.ttf", size)
           
        while True:
            
            assets = {'background' : load_image('background.png'),
            }
              
            display.blit(pygame.transform.scale(assets['background'], display.get_size()), (0, 0))
            
            pos = list(pygame.mouse.get_pos())
            ratio_x = (screen_rect.width / display_rect.width)
            ratio_y = (screen_rect.height / display_rect.height)
            Menu_mouse = (pos[0] / ratio_x, pos[1] / ratio_y)
                
            
            MENU_TEXT = get_font(100).render("MAIN MENU", True, "#b68f40")
            MENU_RECT = MENU_TEXT.get_rect(center=(posB[0] * .5, posB[1] * .139))

            PLAY_BUTTON = scripts.menus.Button(None, pos=(posB[0] * .5, posB[1] * .347),
                                text_input="PLAY", font=get_font(75), base_color="#d7fcd4", hovering_color="White")
            OPTIONS_BUTTON = scripts.menus.Button(None, pos=(posB[0] * .5, posB[1] * .555), 
                                text_input="OPTIONS", font=get_font(75), base_color="#d7fcd4", hovering_color="White")
            QUIT_BUTTON = scripts.menus.Button(None, pos=(posB[0] * .5, posB[1] * .764), 
                                text_input="QUIT", font=get_font(75), base_color="#d7fcd4", hovering_color="White")

            display.blit(MENU_TEXT, MENU_RECT)

            for button in [PLAY_BUTTON, OPTIONS_BUTTON, QUIT_BUTTON]:
                button.change_color(Menu_mouse)
                button.update(display)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if PLAY_BUTTON.clicked(Menu_mouse):
                        asyncio.run(Game().run())
                    if OPTIONS_BUTTON.clicked(Menu_mouse):
                        options()
                    if QUIT_BUTTON.clicked(Menu_mouse):
                        pygame.quit()
                        sys.exit()

            screen.blit(pygame.transform.scale(display, screen.get_size()), (0 , 0)) #scaling the base image larger for p[ixel art effect]
            pygame.display.update()

def options():
    while True:
        def get_font(size): # Returns Press-Start-2P in the desired size
            return pygame.font.Font("data/font.ttf", size)
        
        assets = {'background' : load_image('background.png'),
            }
              
        display.blit(pygame.transform.scale(assets['background'], display.get_size()), (0, 0))
        pos = list(pygame.mouse.get_pos())
        ratio_x = (screen_rect.width / display_rect.width)
        ratio_y = (screen_rect.height / display_rect.height)
        OPTIONS_MOUSE_POS = (pos[0] / ratio_x, pos[1] / ratio_y)

        OPTIONS_TEXT = get_font(45).render("This is the OPTIONS screen.", True, "Black")
        OPTIONS_RECT = OPTIONS_TEXT.get_rect(center=(posB[0] * .5, posB[1] * .347))
        display.blit(OPTIONS_TEXT, OPTIONS_RECT)

        OPTIONS_BACK = scripts.menus.Button(image=None, pos=(posB[0] * .5, posB[1] * .555), 
                            text_input="BACK", font=get_font(75), base_color="Black", hovering_color="Green")

        OPTIONS_BACK.change_color(OPTIONS_MOUSE_POS)
        OPTIONS_BACK.update(display)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if OPTIONS_BACK.clicked(OPTIONS_MOUSE_POS):
                    menu()
        
        screen.blit(pygame.transform.scale(display, screen.get_size()), (0 , 0)) #scaling the base image larger for p[ixel art effect]
        pygame.display.update()


        
if __name__ == "__main__":
    menu()
