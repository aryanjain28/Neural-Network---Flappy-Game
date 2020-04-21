import pygame
import os
import random
import math
import neat
import pandas as pd
import matplotlib.pyplot as plt
pygame.font.init()

w = 600
h = 800
GEN = 0

WIN = pygame.display.set_mode((w, h))
pygame.display.set_caption("Flappy Bird")

birdImages = [
    pygame.transform.scale2x(pygame.image.load('/home/aryan/Desktop/Flappy bird/images/bird1.png')),
    pygame.transform.scale2x(pygame.image.load('/home/aryan/Desktop/Flappy bird/images/bird2.png')),
    pygame.transform.scale2x(pygame.image.load('/home/aryan/Desktop/Flappy bird/images/bird3.png'))
]
baseImage = pygame.transform.scale2x(pygame.image.load('/home/aryan/Desktop/Flappy bird/images/base.png'))
pipeImage = pygame.transform.scale2x(pygame.image.load('/home/aryan/Desktop/Flappy bird/images/pipe.png'))
# bg = pygame.transform.scale2x(pygame.image.load('/home/aryan/Desktop/Flappy bird/images/bg.png'))
bg = pygame.transform.scale(pygame.image.load('/home/aryan/Desktop/Flappy bird/images/bg.png').convert_alpha(), (600, 900))

statFont = pygame.font.SysFont('comicsans', 50)

class Bird:

    animationTime = 5

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.velocity = 0
        self.birdImages = birdImages
        self.imageCount = 0
        self.accelaration = 3
        self.image = birdImages[0]
        self.height = self.y
        self.tickCount = 0

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
        self.velocity = -10.5 
        self.tickCount = 0
        self.height = self.y


    def moveBird(self):
        self.tickCount += 1
        d  = (self.tickCount)*(self.velocity) + 0.5*(self.accelaration)*(self.tickCount)**2       #physics displacement formula => ut + (1/2)at^2
        
        if d >= 16:
            d = (d/abs(d)) * 16

        if d < 0:
            d -= 2
        
        self.y += d

class Pipe:

    pipeImage = pipeImage

    def __init__(self, x):
        self.height = 0
        self.topImage = pygame.transform.flip(self.pipeImage, False, True)
        self.bottomImage = self.pipeImage
        self.passed = False
        self.xTop = x
        self.yTop = 0
        self.xBottom = x
        self.yBottom = 0
        self.gap = 200
        self.setHeight()
        self.velocity = 5

    def setHeight(self):
            self.height = random.randrange(50,450)
            self.yTop = -self.topImage.get_height() + self.height
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
        

        
def drawBackground(window, birds, pipes, base, score):
    global GEN 
    window.blit(bg, (0,0))
    for bird in birds:
        bird.drawBird(window)
    for pipe in pipes:
        pipe.drawPipe(window)
    base.drawBase(window)
    text = statFont.render("Generation : " + str(GEN) +  "      Score : "+str(score), 1, (0,0,0))
    window.blit(text, (10, 10))
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

def main(genomes, config):

    global GEN
    GEN += 1

    nets = []
    birds = []
    ge = []

    for _, g in genomes:
        g.fitness = 0
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        birds.append(Bird(230, 350))
        ge.append(g)

    global WIN
    window = WIN
    pipes = [Pipe(700)]
    base = Base(730)
    clock = pygame.time.Clock()
    run = True
    # jump = False
    score = 0

    while run:      
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()

        pipeIndex = 0
        if len(birds) > 0:
            if len(pipes) > 1 and birds[0].x > pipes[0].xTop + pipes[0].topImage.get_width():
                pipeIndex = 1
        else:
            run = False
            break

        for x, bird in enumerate(birds):
            ge[x].fitness+=0.1
            bird.moveBird()

            # print((bird.y, abs(bird.y - pipes[pipeIndex].height), abs(bird.y - pipes[pipeIndex].yBottom)))
            output = nets[x].activate((bird.y, abs(bird.y - pipes[pipeIndex].height), abs(bird.y - pipes[pipeIndex].yBottom)))
            if (output[0] > 0.5):
                bird.jump()

        base.move()

        removedPipe = []
        addPipe = False

        # yBird = bird.y
        # xBird = bird.x + bird.image.get_width()
        # dTop = math.sqrt((xBird-pipes[-1].xTop)**2+(yBird-(pipes[-1].yTop+640))**2)
        # dBottom = math.sqrt((xBird-pipes[-1].xBottom)**2+(yBird-(pipes[-1].yBottom))**2)
        # heightTop = pipes[-1].height
        # heightbottom = h-(pipes[-1].gap+pipes[-1].height)
        # theta = math.degrees(math.acos((dTop**2+dBottom**2-150**2)/(2*dTop*dBottom)))

        for pipe in pipes:
            pipe.movePipe()

            for x, bird in enumerate(birds):
                if collision(bird, pipe):
                    ge[birds.index(bird)].fitness -= 1
                    nets.pop(birds.index(bird))
                    ge.pop(birds.index(bird))
                    birds.pop(birds.index(bird))

            if not pipe.passed and pipe.xTop < bird.x:
                pipe.passed = True
                addPipe = True
            
            if pipe.xTop + pipe.topImage.get_width() < 0:
                removedPipe.append(pipe)

        if addPipe:
            score+=1
            for g in ge:
                g.fitness += 5
            pipes.append(Pipe(600))

        for r in removedPipe:
            pipes.remove(r)

        for x, bird in enumerate(birds):
            if bird.y + bird.image.get_height() - 10 >= 730 or bird.y < -50:
                nets.pop(birds.index(bird))
                ge.pop(birds.index(bird))
                birds.pop(birds.index(bird))

        drawBackground(window, birds, pipes, base, score)

        # pygame.draw.line(window, (255, 0, 0), (bird.x, bird.y), (pipes[-1].xTop, pipes[-1].yTop+640), 5)
        # pygame.draw.line(window, (255, 0, 0), (bird.x, bird.y), (pipes[-1].xBottom, pipes[-1].yBottom), 5) 
        # pygame.draw.line(window, (255, 0, 0), (0, pipes[-1].height+pipes[-1].gap/2), (w, pipes[-1].height+pipes[-1].gap/2), 5)
        # pygame.draw.line(window, (255, 0, 0), (pipes[-1].xTop+pipes[-1].topImage.get_width(), pipes[-1].height), (pipes[-1].xBottom+pipes[-1].topImage.get_width(), pipes[-1].height+pipes[-1].gap), 5)
        # pygame.draw.line(window, (255, 0, 0), (bird.x, bird.y), (bird.x, h), 5)
        
        pygame.display.update()


def run(configPath):
    config = neat.config.Config(
        neat.DefaultGenome, 
        neat.DefaultReproduction, 
        neat.DefaultSpeciesSet, 
        neat.DefaultStagnation, 
        configPath
    )
    population = neat.Population(config)
    #optional
    population.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    population.add_reporter(stats)

    winner = population.run(main,50)


if __name__ == "__main__":
    # main()
    localDir = os.path.dirname(__file__)
    configPath = os.path.join(localDir, 'config.txt')
    run(configPath)