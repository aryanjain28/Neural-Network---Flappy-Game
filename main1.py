import pygame
import os
import random
import math
import neat
import pandas as pd
import tensorflow as tf
from tensorflow import keras
import matplotlib.pyplot as plt
pygame.font.init()

w = 500
h = 800

birdImages = [
    pygame.transform.scale2x(pygame.image.load('/home/aryan/Desktop/Flappy bird/images/bird1.png')),
    pygame.transform.scale2x(pygame.image.load('/home/aryan/Desktop/Flappy bird/images/bird2.png')),
    pygame.transform.scale2x(pygame.image.load('/home/aryan/Desktop/Flappy bird/images/bird3.png'))
]
baseImage = pygame.transform.scale2x(pygame.image.load('/home/aryan/Desktop/Flappy bird/images/base.png'))
pipeImage = pygame.transform.scale2x(pygame.image.load('/home/aryan/Desktop/Flappy bird/images/pipe.png'))
bg = pygame.transform.scale2x(pygame.image.load('/home/aryan/Desktop/Flappy bird/images/bg.png'))

statFont = pygame.font.SysFont('comicsans', 50)

class Bird:

    animationTime = 5
    tickCount = 0

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.velocity = 0
        self.birdImages = birdImages
        self.imageCount = 0
        self.accelaration = 3
        self.image = birdImages[0]

    def drawBird(self, window):
        self.imageCount += 1

        if self.imageCount < self.animationTime:
            self.image = self.birdImages[0]
        elif self.imageCount < self.animationTime*2:
            self.image = self.birdImages[1]
        elif self.imageCount < self.animationTime*3:
            self.image = self.birdImages[2]
        elif self.imageCount < self.animationTime*4:
            self.image = self.birdImages[1]
        elif self.imageCount < self.animationTime*5:
            self.image = self.birdImages[0]
            self.imageCount = 0
        
        window.blit(self.image, (self.x,self.y))

    def jump(self):
        self.velocity = -8.0
        self.height = self.y
        self.tickCount = 0


    def moveBird(self):
        self.tickCount += 1
        d  = self.tickCount*self.velocity + (0.5*self.accelaration*self.tickCount**2)       #physics displacement formula => ut + (1/2)at^2
        
        if d >= 16:
            d = 16

        if d < 0:
            d -= 2
        
        self.y += d

class Pipe:

    pipeImage = pipeImage

    def __init__(self, x):
        self.height = 0
        self.topImage = pygame.transform.flip(self.pipeImage, False, True)
        self.bottomImage = self.pipeImage
        self.passed = 0
        self.xTop = x
        self.yTop = 0
        self.xBottom = x
        self.yBottom = 0
        self.gap = 150
        self.setHeight()
        self.velocity = 5

    def setHeight(self):
            self.height = random.randrange(50,450)
            self.yTop = -self.bottomImage.get_height() + self.height
            self.yBottom = self.gap + self.height
    
    def drawPipe(self, window):
        window.blit(self.topImage, (self.xTop, self.yTop))
        window.blit(self.bottomImage, (self.xBottom, self.yBottom))

    def movePipe(self):
        self.xTop-=self.velocity
        self.xBottom-=self.velocity

class Base:

    baseImage = baseImage
    width = baseImage.get_width()
    velocity = 5

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.width

    def move(self):
        self.x1-=self.velocity
        self.x2-=self.velocity

        if self.x1 + self.width < 0:
            self.x1 = self.x2 + self.width
        
        if self.x2 + self.width < 0:
            self.x2 = self.x1 + self.width
        
    def drawBase(self, window):
        window.blit(self.baseImage, (self.x1, self.y))
        window.blit(self.baseImage, (self.x2, self.y))
        

        
def drawBackground(window, bird, pipes, base, score):
    window.blit(bg, (0,0))
    bird.drawBird(window)
    for pipe in pipes:
        pipe.drawPipe(window)
    base.drawBase(window)
    text = statFont.render("Score : "+str(score), 1, (0,0,0))
    window.blit(text, (300, 10))
    pygame.display.update()

def collision(bird, pipe):

    birdMask = pygame.mask.from_surface(bird.image)
    topPipeMask = pygame.mask.from_surface(pipe.topImage)
    bottomPipeMask = pygame.mask.from_surface(pipe.bottomImage)

    topOffset = (pipe.xTop - bird.x, pipe.yTop - round(bird.y))
    bottomOffset = (pipe.xTop - bird.x, pipe.yBottom - round(bird.y))

    topPoint = birdMask.overlap(topPipeMask, topOffset)
    bottomPoint = birdMask.overlap(bottomPipeMask, bottomOffset)
    
    if topPoint or bottomPoint:
        return True
    
    return False

def main():
    model = keras.models.load_model('/home/aryan/Desktop/Flappy bird/trainedModel.h5')

    window = pygame.display.set_mode((w, h))
    bird = Bird(200, 200)
    pipes = [Pipe(350)]
    base = Base(730)
    clock = pygame.time.Clock()
    run = True
    jump = False
    score = 0
    dTop, dBottom = 0,0

    generateData = []

    while run:
        clock.tick(5)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                # print('\n\n')
                # df = pd.DataFrame(generateData, columns=['topDistance', 'bottomDistance', 'birdPosition', 'jump'])
                # df.to_csv('generatedData1.csv')
                # print(len(generateData))
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    bird.jump()
                    jump = True

        bird.moveBird()
        base.move()

        removedPipe = []
        addPipe = False

        yBird = bird.y
        xBird = bird.x + bird.image.get_width()
        dTop = math.sqrt((xBird-pipes[-1].xTop)**2+(yBird-(pipes[-1].yTop+640))**2)
        dBottom = math.sqrt((xBird-pipes[-1].xBottom)**2+(yBird-(pipes[-1].yBottom))**2)

        o = 1 if jump else 0
        print([dTop, dBottom, yBird, o])
        generateData.append([dTop, dBottom, yBird, o])

        if jump:
            jump = False

        for pipe in pipes:
            if collision(bird, pipe):
                pass
            if pipe.xTop + pipe.topImage.get_width() < 0:
                removedPipe.append(pipe)
            if not pipe.passed and pipe.xTop < bird.x:
                pipe.passed = True
                addPipe = True
            pipe.movePipe()

        if addPipe:
            score+=1
            pipes.append(Pipe(600))

        removedPipe.clear()

        if bird.y + bird.image.get_height() >= 730:
            pass

        drawBackground(window, bird, pipes, base, score)

        pygame.draw.line(window, (255, 0, 0), (xBird, yBird), (pipes[-1].xTop, pipes[-1].yTop+640), 5)
        pygame.draw.line(window, (255, 0, 0), (xBird, yBird), (pipes[-1].xBottom, pipes[-1].yBottom), 5)
        pygame.display.update()

    pygame.quit()

if __name__ == "__main__":
    main()