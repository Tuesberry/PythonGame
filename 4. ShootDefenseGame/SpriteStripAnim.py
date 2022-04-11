import pygame

class spritesheet(object):
    def __init__(self, filename, scale_x, scale_y, IsFlip):
        self.sheet = pygame.image.load(filename)
        self.sheet = pygame.transform.scale(self.sheet, (int(self.sheet.get_width() * scale_x), int(self.sheet.get_height() * scale_y)))
        self.sheet = pygame.transform.flip(self.sheet, IsFlip, False)

    # Load a specific image from a specific rectangle
    def image_at(self, rectangle, colorkey = None):
        # "Loads image from x,y,x+offset,y+offset"
        rect = pygame.Rect(rectangle)
        image = pygame.Surface(rect.size, pygame.SRCALPHA)
        image.blit(self.sheet, (0, 0), rect)
        return image

    # Load a whole bunch of images and return them as a list
    def images_at(self, rects, colorkey = None):
        # "Loads multiple images, supply a list of coordinates" 
        return [self.image_at(rect, colorkey) for rect in rects]
        
    # Load a whole strip of images
    def load_strip(self, rect, image_count, colorkey = None):
        # "Loads a strip of images and returns them as a list"
        tups = [(rect[0]+rect[2]*x, rect[1], rect[2], rect[3])
                for x in range(image_count)]
        return self.images_at(tups, colorkey)

class SpriteStripAnim(object):
    def __init__(self, filename, rect, count, colorkey=None, loop=False, frames=1, scale_x = 1, scale_y = 1, IsFlip = False):
        self.filename = filename
        ss = spritesheet(filename, scale_x, scale_y, IsFlip)
        self.images = ss.load_strip(rect, count, colorkey)
        self.i = 0
        self.loop = loop
        self.frames = frames
        self.f = frames
        self.count = count
    def iter(self):
        self.i = 0
        self.f = self.frames
        return self
    def next(self):
        if self.i >= len(self.images):
            if not self.loop:
                raise StopIteration
            else:
                self.i = 0
        image = self.images[self.i]
        self.f -= 1
        if self.f == 0:
            self.i += 1
            self.f = self.frames
        return image
    def __add__(self, ss):
        self.images.extend(ss.images)
        return self
    def IsEnd(self):
        if self.i == self.count-1 :
            return True
        return False