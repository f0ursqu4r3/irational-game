import pygame
import json
import scripts.world_gen as world_gen
import asyncio

#if the player is bigge rmight need look up more tiles 1:07:00

AUTOTILE_MAP = {
    tuple(sorted([(1, 0), (0,1)])): 0,
    tuple(sorted([(1, 0), (0,1), (-1, 0)])): 1,
    tuple(sorted([(-1, 0), (0,1)])): 2,
    tuple(sorted([(1, 0), (0,-1), (0, 1)])): 3,
    tuple(sorted([(-1, 0), (0,-1)])): 4,
    tuple(sorted([(-1, 0), (0,-1), (1, 0)])): 5,
    tuple(sorted([(1, 0), (0,-1)])): 6,
    tuple(sorted([(1, 0), (0,-1), (0, 1)])): 7,
    tuple(sorted([(1, 0), (-1,0), (0,1), (0, -1)])): 8,
}

NEIGHBOR_OFFSETS = [(-1, 0), (-1, -1), (0, -1), (1, -1), (1, 0), (0,0), (-1, 1), (0,1), (1,1)]
PHYSICS_TILES = {'grass', 'stone'}
AUTOTILE_TYPES = {'grass', 'stone'}
chunk_size = 32
import random

class Tilemap:
    def __init__(self, game, tile_size):
        self.game = game
        self.tile_size= tile_size
        self.tilemap = {}
        self.offgrid_tiles = []
        #could use a object here 52:30
            
    def tiles_around(self, pos):
        tiles = []
        tile_loc = (int(pos[0] // self.tile_size), int(pos[1] // self.tile_size)) # double slash matters for some -1, decimal issues 1:09:00
        for offset in NEIGHBOR_OFFSETS:
            check_loc = str(tile_loc[0] + offset[0]) + ';' + str(tile_loc[1] + offset[1]) #most of these [0] [1], are x and y postions respectively
            if check_loc in self.tilemap:
                tiles.append(self.tilemap[check_loc])
        return tiles
    
    def physics_rects_around(self, pos):
        rects = []
        for tile in self.tiles_around(pos):
            try:
                if tile['type'] in PHYSICS_TILES:
                    rects.append(pygame.Rect(tile['pos'][0] * self.tile_size, tile['pos'][1] * self.tile_size, self.tile_size, self.tile_size))
            except:
                pass
        return rects
    
    def autotile(self):
        for loc in self.tilemap:
            tile = self.tilemap[loc]
            neighbors = set()
            for shift in [(1, 0), (-1, 0), (0, -1), (0, 1)]:
                check_loc = str(tile['pos'][0] + shift[0]) + ';' + str(tile['pos'][1] + shift[1])
                if check_loc in self.tilemap:
                    if self.tilemap[check_loc]['type'] == tile['type']:
                        neighbors.add(shift)
            neighbors = tuple(sorted(neighbors))
            if (tile['type'] in AUTOTILE_TYPES) and (neighbors in AUTOTILE_MAP):
                tile['variant'] = AUTOTILE_MAP[neighbors]
                
    def extract(self, idpairs, keep=False): #3:15
        matches = []
        for tile in self.offgrid_tiles.copy():
            if (tile['type'], tile['variant']) in idpairs:
                matches.append(tile.copy())
                if not keep:
                    self.offgrid_tiles.remove(tile)
                    
        for loc in self.tilemap:
            tile = self.tilemap[loc]
        try:
            if (tile['type'], tile['variant']) in idpairs:
                matches.append(tile.copy())
                matches[-1]['pos'] = matches[-1]['pos'].copy()
                matches[-1]['pos'][0] *= self.tile_size
                matches[-1]['pos'][1] *= self.tile_size
                if not keep:
                    del self.tilemap[loc]
        except:
            pass            
        return matches
            
        
    def render(self, surf, offset=(0, 0)):
        for tile in self.offgrid_tiles:
            surf.blit(self.game.assets[tile['type']][tile['variant']], (tile['pos'][0] - offset[0], tile['pos'][1] - offset[1])) #1:53:00 talks about larger scale games
            
        for x in range(offset[0] // self.tile_size, (offset[0] + surf.get_width())  // self.tile_size + 1): #this for loop only load whats on screen 1:45:00 ish
            for y in range(offset[1] // self.tile_size, (offset[1] + surf.get_height()) // self.tile_size + 1): 
                loc = str(x) + ';' + str(y)
                target_x = x + int(self.game.scroll[0]/ (chunk_size * 16))
                target_y = y + int(self.game.scroll[1]/ (chunk_size * 16))
                if loc in self.tilemap and self.tilemap[loc] != None:
                    tile = self.tilemap[loc]
                    surf.blit(self.game.assets[tile['type']][tile['variant']], (tile['pos'][0] * self.tile_size - offset[0], tile['pos'][1] * self.tile_size - offset[1]))
                if loc not in self.tilemap:
                    asyncio.create_task(self.generation(loc, target_x, target_y))
    
        
    def save(self, path):
        f = open(path, 'w')
        json.dump({'tilemap': self.tilemap, 'tile_size': self.tile_size, 'offgrid': self.offgrid_tiles}, f)
        f.close()
        
    def load(self, path):
        f = open(path, 'r')
        map_data = json.load(f)
        f.close()
        
        self.tilemap = map_data['tilemap']
        self.tile_size = map_data['tile_size']
        self.offgrid_tiles = map_data['offgrid']
        
    def solid_check(self, pos):
        tile_loc = str(int(pos[0] // self.tile_size)) + ';' + str(int(pos[1] // self.tile_size))
        if tile_loc in self.tilemap:
            if self.tilemap[tile_loc]['type'] in PHYSICS_TILES:
                return True
    
    async def generation(self, loc, target_x, target_y):
        rand = random.randint(1,3)
        if rand == 1:
            
            self.tilemap[loc] = self.forest(self.tilemap, target_x, target_y)
        if rand == 2:
            
            self.tilemap[loc] = self.ditches(self.tilemap, target_x, target_y)
        else:
            
            self.tilemap[loc] = self.mountain(self.tilemap, target_x, target_y)
         

    def forest(self, tilemap, x, y):
        world_gen.chunk_generation.basic_generation(tilemap, x, y, .05, 10)
        
    
    def mountain(self, tilemap, x, y):
        world_gen.chunk_generation.basic_generation(tilemap, x, y, .01, 20)
        
    def ditches(self, tilemap, x, y):
        world_gen.chunk_generation.basic_generation(tilemap, x, y, .05, 15)
                        