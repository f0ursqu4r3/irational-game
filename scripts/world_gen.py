
class chunk_generation:
    def __init__(self, x, y, smooth, extreme):
        self.x = x
        self.y = y
        self.smooth = smooth
        self.extreme = extreme
        
    def basic_generation(tilemap, x, y, smooth, extreme):
        import noise
        import random
        chunk_size = 32
        chunks_data = []
        for y_pos in range(chunk_size):
            for x_pos in range(chunk_size):
                tile_pos = (x * chunk_size + x_pos, y * chunk_size + y_pos)
                height = int(noise.pnoise1(tile_pos[0] * smooth, repeat=99999999) * extreme)
                tile_type = 0 #nothing
                if tile_pos[1] > 50 - height: 
                        tile_type = 'grass' # dirt
                        variant = 8
                elif tile_pos[1] == 50 - height:
                    tile_type = 'grass' # grass
                    variant = 1
                elif tile_pos[1] == 49 - height - 1:
                    if random.randint(1, 5) == 1:
                        tile_type = 'large_decor' #plant
                        variant = 2
                elif tile_pos[1] == 49 - height:
                    if random.randint(1, 5) == 2:
                        tile_type = 'large_decor'
                        variant = 1
                
                if tile_type != 0:
                    tilemap[str(tile_pos[0]) + ';' + str(tile_pos[1])] = {'type': tile_type, 'variant': variant, 'pos': tile_pos}
                
        if chunks_data != []:        
            return chunks_data
        
#class mountains(forest):
    #def __init__(self, x, y):
        #super().__init__(self, x ,y)
        