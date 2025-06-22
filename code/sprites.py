import pygame
from settings import WIDTH, HEIGHT
from os import walk
from os.path import join
from math import atan2, degrees


class Sprite(pygame.sprite.Sprite):
    def __init__(self, pos, surf, *groups):
        super().__init__(*groups)
        self.image = surf
        self.rect = self.image.get_frect(topleft=pos)
        self.ground = True


# class for collsion objects
# these objects are used to check for collisions with the player
class CollisionSprite(pygame.sprite.Sprite):
    def __init__(self, pos, surf, *groups):
        super().__init__(*groups)
        self.image = surf
        self.rect = self.image.get_frect(topleft=pos)


# player class
class Player(pygame.sprite.Sprite):
    def __init__(self, pos, groups, collsion_sprites):
        super().__init__(groups)
        self.load_images()
        self.image = pygame.image.load(join("images", "player", "down", "0.png"))
        self.rect = self.image.get_frect(center=pos)
        self.hitbox_rect = self.rect.inflate(-60, -90)

        self.state, self.frame_index = "down", 0

        self.speed = 400
        self.direction = pygame.Vector2()

        self.collsion_sprites = collsion_sprites

    def load_images(self):
        self.frames = {"up": [], "down": [], "left": [], "right": []}

        for state in self.frames.keys():
            for file_path, sub_folder, files in walk(join("images", "player", state)):
                for file in sorted(files, key=lambda x: int(x.split(".")[0])):
                    image = pygame.image.load(join(file_path, file))
                    self.frames[state].append(image)

    def collsion(self, direction):
        for sprite in self.collsion_sprites:
            if sprite.rect.colliderect(self.hitbox_rect):
                if direction == "horizontal":
                    if self.direction.x > 0:
                        self.hitbox_rect.right = sprite.rect.left
                    if self.direction.x < 0:
                        self.hitbox_rect.left = sprite.rect.right
                if direction == "vertical":
                    if self.direction.y < 0:
                        self.hitbox_rect.top = sprite.rect.bottom
                    if self.direction.y > 0:
                        self.hitbox_rect.bottom = sprite.rect.top

    def input(self):
        keys = pygame.key.get_pressed()

        self.direction.x = keys[pygame.K_d] - keys[pygame.K_a]
        self.direction.y = keys[pygame.K_s] - keys[pygame.K_w]

        if self.direction.length() > 0:
            self.direction.normalize()

    def move(self, dt):
        self.hitbox_rect.x += self.direction.x * self.speed * dt
        self.collsion("horizontal")

        self.hitbox_rect.y += self.direction.y * self.speed * dt
        self.collsion("vertical")

        self.rect.center = self.hitbox_rect.center

    def animate(self, dt):
        # getting the current state
        if self.direction.x != 0:
            self.state = "right" if self.direction.x > 0 else "left"
        if self.direction.y != 0:
            self.state = "down" if self.direction.y > 0 else "up"

        # animatation logic
        self.frame_index = self.frame_index + 10 * dt if self.direction else 0
        self.image = self.frames[self.state][
            int(self.frame_index) % len(self.frames[self.state])
        ]

    def update(self, dt):
        self.input()
        self.move(dt)
        self.animate(dt)


# Bullet class
class Bullet(pygame.sprite.Sprite):
    def __init__(self, surf, pos, direction, *groups):
        super().__init__(*groups)
        self.image = surf
        self.rect = self.image.get_frect(center=pos)

        self.direction = direction.normalize()
        self.speed = 1200

        self.spawn_time = pygame.time.get_ticks()
        self.lifetime = 1000

    def update(self, dt):
        self.rect.center += self.direction * self.speed * dt

        if pygame.time.get_ticks() - self.spawn_time > self.lifetime:
            self.kill()


# Gun class
class Gun(pygame.sprite.Sprite):
    def __init__(self, player, *groups):
        super().__init__(*groups)
        self.player = player
        self.distance = 140
        self.player_direction = pygame.Vector2(1, 0)

        # sprite setup
        self.gun_surf = pygame.image.load(
            join("images", "gun", "gun.png")
        ).convert_alpha()
        self.image = self.gun_surf
        self.rect = self.image.get_frect(
            center=self.player.rect.center + self.player_direction * self.distance
        )

    def get_direction(self):
        mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
        player_pos = pygame.Vector2(WIDTH / 2, HEIGHT / 2)

        self.player_direction = (mouse_pos - player_pos).normalize()

    def rotate_gun(self):
        angle = degrees(atan2(self.player_direction.x, self.player_direction.y)) - 90

        if self.player_direction.x > 0:
            self.image = pygame.transform.rotozoom(self.gun_surf, angle, 1)
        else:
            self.image = pygame.transform.rotozoom(self.gun_surf, abs(angle), 1)
            self.image = pygame.transform.flip(self.image, False, True)

    def update(self, _):
        self.get_direction()
        self.rotate_gun()
        self.rect.center = (
            self.player.rect.center + self.player_direction * self.distance
        )


class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos, groups, player, collsion_sprites):
        super().__init__(*groups)
        self.image = pygame.image.load(join("images", "enemy", "enemy.png"))

        self.player = player
        self.collsion_sprites = collsion_sprites

        self.rect = self.image.get_frect(center=pos)
        self.speed = 200
        self.direction = pygame.Vector2(0, 0)
