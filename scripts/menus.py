class Button():
    def __init__(self, image, pos, text_input, font, base_color, hovering_color):
        self.image = image
        self.pos = list(pos)
        self.font = font
        self.base_color, self.hover_color = base_color, hovering_color
        self.text_input = text_input
        self.text = self.font.render(self.text_input, True, self.base_color)
        if self.image is None:
            self.image = self.text
        self.rect = self.image.get_rect(center=(self.pos[0], self.pos[1]))
        self.text_rect = self.text.get_rect(center=(self.pos[0], self.pos[1]))
        
    def update(self, display):
        if self.image is not None:
            display.blit(self.image, self.rect)
        display.blit(self.text, self.text_rect)
        
    def clicked(self, pos):
        if pos[0] in range(self.rect.left, self.rect.right) and pos[1] in range (self.rect.top, self.rect.bottom):
            return True
        return False
    
    def change_color(self, pos):
        if pos[0] in range(self.rect.left, self.rect.right) and pos[1] in range (self.rect.top, self.rect.bottom):
            self.text = self.font.render(self.text_input, True, self.hover_color)
        else:
            self.text = self.font.render(self.text_input, True, self.base_color)