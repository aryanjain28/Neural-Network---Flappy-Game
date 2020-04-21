import pygame
import neat
import random
import os
import time
pygame.font.init()
pygame.init()

GEN = 0
WIDTH, HEIGHT = 600, 800
GAP = 200
CLOCK = 100
WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Flappy Bird using Neuro Evolution')
ANIMATION_TIME = 5



birdImages = [
    pygame.transform.scale2x(pygame.image.load(os.path.join(os.path.dirname(__file__), 'images/bird1.png'))),
    pygame.transform.scale2x(pygame.image.load(os.path.join(os.path.dirname(__file__), 'images/bird2.png'))),
    pygame.transform.scale2x(pygame.image.load(os.path.join(os.path.dirname(__file__), 'images/bird3.png'))),
]
baseImage = pygame.transform.scale2x(pygame.image.load(os.path.join(os.path.dirname(__file__), 'images/base.png')))
bg = pygame.transform.scale(pygame.image.load(os.path.join(os.path.dirname(__file__), 'images/bg.png')).convert_alpha(), (WIDTH, HEIGHT))

bPipeImage = pygame.transform.scale2x(pygame.image.load(os.path.join(os.path.dirname(__file__), 'images/pipe.png')))
tPipeImage = pygame.transform.flip(bPipeImage, True,  True)


class Bird:

    global birdImages

    def __init__(self, x, y):
        self.jumpVelocity = 0
        self.x = x
        self.y = y
        self.image = birdImages[0]
        self.animationTime = ANIMATION_TIME
        self.time = 0
        self.imageCount = 0
        self.accelaration = 3

    def jump(self):
        self.time = 0
        self.jumpVelocity = -10.5

    def move(self):
        self.time += 1
        d = (self.jumpVelocity*self.time) + (0.5)*(self.accelaration)*(self.time**2)  # d = ut + 1/2(a)(t)^2

        if d >= 16:
            d = (d/abs(d)) * 16

        if d < 0:
            d -= 2 

        self.y += d

    def draw(self, WINDOW):
        self.imageCount += 1

        if self.imageCount <= self.animationTime:
            self.image = birdImages[0]
        elif self.imageCount <= self.animationTime*2:
            self.image = birdImages[1]
        elif self.imageCount <= self.animationTime*3:
            self.image = birdImages[2]
        elif self.imageCount <= self.animationTime*4:
            self.image = birdImages[1]
        elif self.imageCount <= self.animationTime*5:
            self.image = birdImages[0]
            self.imageCount = 0

        WINDOW.blit(self.image, (self.x, self.y))

class Base:

    global baseImage

    def __init__(self, y):
        self.y = y
        self.image = baseImage
        self.x1 = 0
        self.x2 = baseImage.get_width()
        self.velocity = 5

    def draw(self, WINDOW):
        WINDOW.blit(self.image, (self.x1, self.y))
        WINDOW.blit(self.image, (self.x2, self.y))
        

    def move(self):
        self.x1-=self.velocity
        self.x2-=self.velocity

        if self.x1+self.image.get_width() <= 0:
            self.x1 = self.x2 + self.image.get_width()

        if self.x2+self.image.get_width() <= 0:
            self.x2 = self.x1 + self.image.get_width()

class Pipe:

    global tPipeImage, bPipeImage, GAP

    def __init__(self, x):
        self.height = 0
        self.velocity = 5
        self.x = x
        self.bottomY = 0
        self.topY = 0
        self.gap = GAP
        self.tImage = tPipeImage
        self.bPipeImage = bPipeImage
        self.height = random.randrange(50, 450)

    def draw(self, WINDOW):
        self.topY = self.height - self.tImage.get_height()
        self.bottomY = self.height + self.gap
        
        WINDOW.blit(tPipeImage, (self.x, self.topY))
        WINDOW.blit(bPipeImage, (self.x, self.bottomY))

    def move(self):
        self.x -= self.velocity
        

def collision(bird, pipe):
    birdMask = pygame.mask.from_surface(bird.image)
    tPipeMask = pygame.mask.from_surface(pipe.tImage)
    bPipeMask = pygame.mask.from_surface(pipe.bPipeImage)

    topOffset = (pipe.x - bird.x, pipe.topY - round(bird.y))
    bottomOffset = (pipe.x - bird.x, pipe.bottomY - round(bird.y))

    top = birdMask.overlap(tPipeMask, topOffset)
    bottom = birdMask.overlap(bPipeMask, bottomOffset)

    if top or bottom:# or bird.y >= HEIGHT-140 or bird.y <= 0:
        return True

    return False

def main(genomes, config):
    global GEN
    GEN += 1

    g = []
    birds = []
    nets = []

    for genomeID, genome in genomes:
        #initializing all genome with fitness of 0
        genome.fitness = 0
        #creating neural networks
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        #appending genomes
        g.append(genome)
        birds.append(Bird(230, 300))

    run = True
    clock = pygame.time.Clock()

    global baseImage

    score = 0
    base = Base(700)
    pipes = [Pipe(400)]

    while run:
        clock.tick(CLOCK)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()

        WINDOW.blit(bg, (0,0))      #draw background 

        pipeIndex = 0
        if len(birds) > 0:
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].bPipeImage.get_width():
                pipeIndex = 1
        else:
            run = False
            break
        
        for x, bird in enumerate(birds):
            g[x].fitness += 0.1
            bird.move()

            output = nets[x].activate((bird.y, abs(bird.y - pipes[pipeIndex].height), abs(bird.y - pipes[pipeIndex].bottomY)))
            if output[0] > 0.5:
                bird.jump()

        base.move()
        
        for pipe in pipes:
            passed = False
            pipe.draw(WINDOW)
            pipe.move()

            if bird.x + bird.image.get_width()  > pipe.x + pipe.tImage.get_width():
                passed = True

        for bird in birds:
            if collision(bird, pipes[-1]):
                # time.sleep(2)
                # run = False
                # score-=1
                g[birds.index(bird)].fitness -= 1
                nets.pop(birds.index(bird))
                g.pop(birds.index(bird))
                birds.pop(birds.index(bird))
                    
        if passed:
            score+=1
            pipes.append(Pipe(WIDTH))
            for genome in g:
                genome.fitness += 5
            
        if pipes[0].x+pipes[0].tImage.get_width() < 0:
            pipes.remove(pipes[0])

        for x, bird in enumerate(birds):
            if bird.y + bird.image.get_height() - 10 >= 730 or bird.y < -50:
                nets.pop(birds.index(bird))
                g.pop(birds.index(bird))
                birds.pop(birds.index(bird))

        for bird in birds:
            bird.draw(WINDOW)          
        base.draw(WINDOW)

        WINDOW.blit(pygame.font.Font('freesansbold.ttf', 32).render(f'Generation : {GEN}', True, (0,0,0)), (10, 10))    #display score      
        WINDOW.blit(pygame.font.Font('freesansbold.ttf', 32).render(f'Alive : {len(birds)}', True, (0,0,0)), (10, 50))
        WINDOW.blit(pygame.font.Font('freesansbold.ttf', 32).render(f'Score : {score}', True, (0,0,0)), (400, 10))

        pygame.display.update()

    # pygame.quit()

def run(configFile):
    config = neat.config.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        configFile
    )
    population = neat.Population(config)
    population.add_reporter(neat.StdOutReporter(True))

    stats = neat.StatisticsReporter()
    population.add_reporter(stats)
    
    winner = population.run(main, n=50)


if __name__ == '__main__':
    run(os.path.join(os.path.dirname(__file__), 'config.txt'))