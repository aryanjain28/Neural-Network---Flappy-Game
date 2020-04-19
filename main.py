import pygame
import neat
import time
import random
import os

w = 500
h = 800

birdImages = [
    pygame.transform.scale2x(pygame.image.load('/home/aryan/Desktop/Flappy bird/images/bird1.png')),
    pygame.transform.scale2x(pygame.image.load('/home/aryan/Desktop/Flappy bird/images/bird2.png')),
    pygame.transform.scale2x(pygame.image.load('/home/aryan/Desktop/Flappy bird/images/bird3.png')),
]

pipeImage = pygame.transform.scale2x(pygame.image.load('/home/aryan/Desktop/Flappy bird/images/pipe.png'))
baseImage = pygame.transform.scale2x(pygame.image.load('/home/aryan/Desktop/Flappy bird/images/base.png'))
bg = pygame.transform.scale2x(pygame.image.load('/home/aryan/Desktop/Flappy bird/images/bg.png'))

class Bird:
    images = birdImages
    maxRotation = 25
    rotationVelocity = 20
    animationTime = 2

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.tilt = 0
        self.tickCount = 0
        self.velocity = 0
        self.height = self.y
        self.imageCount = 0
        self.image = self.images[0]

    def jump(self):
        self.velocity = -10.5
        self.height = self.y
        self.tickCount = 0

    def move(self, win):
        self.tickCount += 1
        d = self.velocity*self.tickCount+1.5*self.tickCount**2     # displacement equation = vt + (1/2)a(t^2)

        if d >= 16:
            d = 16

        if d < 0:
            d -= 2

        self.y += d

    def draw(self, win):
        self.imageCount += 1

        if self.imageCount < self.animationTime:
            self.image = self.images[0]
        elif self.imageCount < self.animationTime*2:
            self.image = self.images[1]
        elif self.imageCount < self.animationTime*3:
            self.image = self.images[2]
        elif self.imageCount < self.animationTime*4:
            self.image = self.images[1]
        elif self.imageCount < self.animationTime*5:
            self.image = self.images[0]
            self.imageCount = 0

        win.blit(self.image, (self.x , self.y))

    def getMask(self):
        return pygame.mask.from_surface(self.image)

def drawWindow(win, bird, pipe):
    win.blit(bg, (0,0))
    bird.draw(win)
    pipe.draw(win)
    pygame.display.update()


class Pipe:
    gap = 200
    pipeVelocity = 5

    def __init__(self, x):
        self.x = x
        self.height = 0
        self.gap = 100

        self.top = 0
        self.bottom = 0
        self.pipeTop = pygame.transform.flip(pipeImage, False, True)
        self.pipeBottom = pipeImage

        self.passed = False
        self.setHeight()

    def setHeight(self):
        self.height = random.randrange(50, 450)
        self.top = -self.pipeTop.get_height() + self.height
        self.bottom = self.height + self.gap
        # self.bottom = self.gap + self.top + self.pipeTop.get_height()

    def move(self):
        self.x-=self.pipeVelocity

    def draw(self, window):
        window.blit(self.pipeTop, (self.x, self.top))
        window.blit(self.pipeBottom, (self.x, self.bottom))

    def collide(self, bird, window):
        birdMask = bird.getMask()
        topPipeMask = pygame.mask.from_surface(self.pipeTop)
        bottomPipeMask = pygame.mask.from_surface(self.pipeBottom)

        topOffset = (self.x - bird.x, self.top - round(bird.y))
        bottomOffset = (self.x - bird.x, self.bottom - round(bird.y))

        topPoint = birdMask.overlap(topPipeMask, topOffset)
        bottomPoint = birdMask.overlap(bottomPipeMask, bottomOffset)
        
        if topPoint or bottomPoint:
            return True
        
        return False

class Base:
    velocity = 5
    width = baseImage.get_width()
    height = baseImage.get_height()

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.width
        self.baseImage = baseImage

    def move(self):
        self.x1-=self.velocity
        self.x2-=self.velocity

        if self.x1 + self.width < 0:
            self.x1 = self.x2 + self.width
        
        if self.x2 + self.width < 0:
            self.x2 = self.x1 + self.width
        
    def draw(self, window):
        window.blit(self.baseImage, (self.x1, self.y))
        window.blit(self.baseImage, (self.x2, self.y))
        

def main():
    bird = Bird(200, 200) 
    pipe = Pipe(400)
    base = Base(730)

    win = pygame.display.set_mode((w, h))
    clock = pygame.time.Clock()

    run = True
    while run:
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    bird.jump()
        drawWindow(win, bird, pipe)
    pygame.quit()

if __name__ == '__main__':
    main()
