import pygame
from os.path import join
from pytmx.util_pygame import load_pygame

from settings import HEIGHT, WIDTH, TILE_SIZE
from sprites import Player, Gun, Bullet, CollisionSprite, Sprite
from groups import AllSprites


class Game:
    def __init__(self):
        # general setup
        pygame.init()
        self.running = True
        self.width = WIDTH
        self.height = HEIGHT

        self.display_surf = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Vampire Survivor")

        self.clock = pygame.time.Clock()

        # sprites
        self.all_sprites = AllSprites()
        self.collsion_sprites = pygame.sprite.Group()
        self.bullet_sprites = pygame.sprite.Group()

        # gun related
        self.can_shoot = True
        self.shoot_time = 0
        self.gun_cooldown = 150

        # setup
        self.load_images()
        self.setup()

    def load_images(self):
        self.bullet_surf = pygame.image.load(
            join("images", "gun", "bullet.png")
        ).convert_alpha()

    def setup(self):
        map = load_pygame(join("data", "maps", "world.tmx"))

        for x, y, image in map.get_layer_by_name("Ground").tiles():
            Sprite((x * TILE_SIZE, y * TILE_SIZE), image, self.all_sprites)

        for object in map.get_layer_by_name("Objects"):
            CollisionSprite(
                (object.x, object.y),
                object.image,
                [self.all_sprites, self.collsion_sprites],
            )

        for object in map.get_layer_by_name("Collisions"):
            surf = pygame.Surface((object.width, object.height))
            CollisionSprite(
                (object.x, object.y),
                surf,
                [self.collsion_sprites],
            )

        for obj in map.get_layer_by_name("Entities"):
            if obj.name == "Player":
                self.player = Player(
                    (obj.x, obj.y),
                    self.all_sprites,
                    self.collsion_sprites,
                )
                self.gun = Gun(self.player, self.all_sprites)

    def gun_timer(self):
        if not self.can_shoot:
            current_time = pygame.time.get_ticks()
            if current_time - self.shoot_time >= self.gun_cooldown:
                self.can_shoot = True

    def input(self):
        if pygame.mouse.get_pressed()[0] and self.can_shoot:
            pos = self.gun.rect.center + self.gun.player_direction * 50
            Bullet(
                self.bullet_surf,
                pos,
                self.gun.player_direction,
                (self.all_sprites, self.bullet_sprites),
            )
            self.can_shoot = False
            self.shoot_time = pygame.time.get_ticks()

    def draw(self, surf):
        surf.fill((0, 0, 0))
        self.all_sprites.draw(self.player.rect.center)
        pygame.display.update()

    def run(self):
        while self.running:
            # delta time
            dt = self.clock.tick(60) / 1000
            # event loop
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            # shoot and gun timer
            self.gun_timer()
            self.input()

            # update and draw
            self.all_sprites.update(dt)
            self.draw(self.display_surf)

        pygame.quit()


if __name__ == "__main__":
    game = Game()
    game.run()
