#!/usr/bin/env python3

import pygame
import random
import math


background_colour = (0, 0, 0)
n_planets = 100
n_stars = 1
p_new = None
c_down = None
(width, height) = (800, 600)
clock = None
fps = 60
G = 0.5


class Particle(object):
    def __init__(self, x, y, m):
        self.x = x
        self.y = y
        self.m = m
        self.r = int(math.ceil(math.sqrt(abs(m))))
        self.color = pygame.Color(255, 255, 255)

    def draw(self, screen):
        pygame.draw.circle(screen, self.color,
                           (int(self.x), int(self.y)), self.r, 0)


class Star(Particle):
    def __init__(self, x, y, M):
        super(Star, self).__init__(x, y, M)
        self.color = (255, 0, 0) if M > 0 else (0, 0, 255)


class Planet(Particle):
    def __init__(self, x, y, m, stars):
        super(Planet, self).__init__(x, y, m)
        self.vx = random.random() * 4 - 2
        self.vy = random.random() * 4 - 2
        self.stars = stars
        self.dead = False
        self.prev_pos = []
        self.trail = 5

    def draw(self, screen):
        super(Planet, self).draw(screen)

        # draw the trail
        for i, p in enumerate(self.prev_pos):
            c_decrease = int(255 - 255 / self.trail * i)
            c = self.color - pygame.Color(*[c_decrease] * 3)
            pygame.draw.circle(screen, c,
                               (int(p[0]), int(p[1])), self.r, 0)

    def update(self):
        if self.dead:
            return

        # compute total acceleration to all stars
        ax = ay = 0
        for star in self.stars:
            # compute distance to star
            dx = self.x - star.x
            dy = self.y - star.y
            d = math.sqrt(dx * dx + dy * dy)

            # check for collisions
            if d < self.r + star.r:
                self.dead = True

            # update acceleration
            a = math.atan2(dy, dx)
            ax += - G * self.m * star.m * math.cos(a) / (d * d)
            ay += - G * self.m * star.m * math.sin(a) / (d * d)

        # update velocity
        self.vx += ax
        self.vy += ay

        # store position history for trail
        self.prev_pos.append((self.x, self.y))
        if len(self.prev_pos) > self.trail:
            self.prev_pos = self.prev_pos[-self.trail:]

        # update position
        self.x += self.vx
        self.y += self.vy

        # die if too far away
        if abs(self.x - width / 2) > 1000 or abs(self.y - height / 2) > 1000:
            self.dead = True


stars = []
for i in range(n_stars):
    x = random.random() * width / 2 + width / 4
    y = random.random() * height / 2 + height / 4
    M = random.random() * 100 + 50
    if random.random() < 0.5:
        M = -M
    stars.append(Star(x, y, M))

planets = []
for i in range(n_planets):
    x = random.random() * width
    y = random.random() * height
    m = random.random() * 10
    planets.append(Planet(x, y, m, stars))


def draw_main(screen):
    clock.tick(fps)
    for star in stars:
        star.draw(screen)

    for p in planets:
        p.draw(screen)
        p.update()
        if p.dead:
            planets.remove(p)

    if p_new:
        p_new.x, p_new.y = pygame.mouse.get_pos()
        p_new.draw(screen)
        pygame.draw.line(screen, (0, 255, 255), c_down, pygame.mouse.get_pos())


def main():
    global p_new, c_down, clock
    # initialize pygame
    pygame.init()
    screen = pygame.display.set_mode((width, height), pygame.DOUBLEBUF)
    pygame.display.set_caption('Planets')
    clock = pygame.time.Clock()

    # main loop
    running = True
    while running:
        # event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                keys = pygame.key.get_pressed()
                mods = pygame.key.get_mods()
                if keys[pygame.K_ESCAPE] or \
                   (keys[pygame.K_w] and mods & pygame.KMOD_META):
                    running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                c_down = pygame.mouse.get_pos()
                m = random.random() * 30
                p_new = Planet(c_down[0], c_down[1], m, stars)
            elif event.type == pygame.MOUSEBUTTONUP:
                c_up = pygame.mouse.get_pos()
                p_new.vx = (c_up[0] - c_down[0]) / 20
                p_new.vy = (c_up[1] - c_down[1]) / 20
                planets.append(p_new)
                p_new = None

        # drawing routines
        screen.fill(background_colour)
        draw_main(screen)
        pygame.display.flip()
    pygame.quit()


if __name__ == '__main__':
    main()
