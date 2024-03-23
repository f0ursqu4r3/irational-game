import pygame
import os
import asyncio

BASE_IMG_PATH = 'data/images/'

def load_image(path):
    img  = pygame.image.load(BASE_IMG_PATH + path).convert()
    img.set_colorkey((0, 0, 0))
    return img

def load_images(path): # you can create a function to load everything ona bigger project, the following is simplified 54:30
    images = []
    for img_name in sorted(os.listdir(BASE_IMG_PATH + path)):
        images.append(load_image(path + '/' + img_name))
    return images

class Animation: #1:59:00 this gets more complicated, but this is a basic starter animation code
    def __init__(self, images, img_dur=5, loop=True):
        self.images = images
        self.loop = loop
        self.img_duration = img_dur
        self.done = False
        self.frame = 0
        
    def copy(self):
        return Animation(self.images, self.img_duration, self.loop)
    
    def update(self):
        if self.loop:
            self.frame = (self.frame + 1) % (self.img_duration * len(self.images)) # the % took care of the list starts at zero thing here 2:05:00
        else:
            self.frame = min(self.frame + 1, self.img_duration * len(self.images) - 1) #minus one cause lists start at 0
            if self.frame >= self.img_duration * len(self.images) - 1:
                self.done = True
    
    def img(self):
        return self.images[int(self.frame / self.img_duration)]
    

class Async_clock:
    def __init__(self, time_func=pygame.time.get_ticks):
        self.time_func = time_func
        self.last_tick = time_func() or 0
        
    async def tick(self, fps=0):
        if 0 >= fps:
            return
        
        end_time = (1/fps) * 1000
        current = self.time_func()
        time_diff = current - self.last_tick
        delay = (end_time - time_diff) / 1000
        
        self.last_tick = current
        if delay < 0:
            delay = 0
        
        asyncio.sleep(delay)
        

            