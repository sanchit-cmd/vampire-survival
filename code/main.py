import pygame
import random
from os.path import join
from os import walk
from pytmx.util_pygame import load_pygame

from settings import HEIGHT, WIDTH, TILE_SIZE
from sprites import Player, Gun, Bullet, Enemy, CollisionSprite, Sprite
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

        # enemies related
        self.enemies_frames = {"bat": [], "blob": [], "skeleton": []}
        self.enemy_sprites = pygame.sprite.Group()
        self.enemy_spawn_cooldown = 500
        self.spawn_position = []

        # custom events
        self.enemy_spawn_event = pygame.event.custom_type()
        pygame.time.set_timer(self.enemy_spawn_event, self.enemy_spawn_cooldown)

        # sounds
        self.music = pygame.mixer.Sound(join("audio", "music.wav"))
        self.shoot_sound = pygame.mixer.Sound(join("audio", "shoot.wav"))
        self.impact_sound = pygame.mixer.Sound(join("audio", "impact.ogg"))

        self.music.set_volume(0.1)
        self.music.play(1)

        self.shoot_sound.set_volume(0.1)
        self.impact_sound.set_volume(0.1)

        # setupaw
        self.load_images()
        self.setup()

    def load_images(self):
        self.bullet_surf = pygame.image.load(
            join("images", "gun", "bullet.png")
        ).convert_alpha()

        for state in self.enemies_frames.keys():
            for file_path, sub_folder, files in walk(join("images", "enemies", state)):
                for file in sorted(files, key=lambda x: int(x.split(".")[0])):
                    image = pygame.image.load(join(file_path, file))
                    self.enemies_frames[state].append(image)

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
            else:
                self.spawn_position.append((obj.x, obj.y))

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
            self.shoot_sound.play()
            self.can_shoot = False
            self.shoot_time = pygame.time.get_ticks()

    def draw(self, surf):
        surf.fill((0, 0, 0))
        self.all_sprites.draw(self.player.rect.center)
        pygame.display.update()

    def spawn_enemies(self):
        enemy_type = ["bat", "blob", "skeleton"][pygame.time.get_ticks() % 3]
        pos = random.choice(self.spawn_position)
        Enemy(
            pos,
            self.enemies_frames[enemy_type],
            (self.all_sprites, self.enemy_sprites),
            self.player,
            self.collsion_sprites,
        )

    def check_collsions(self):
        for bullet in self.bullet_sprites:
            hit_enemies = pygame.sprite.spritecollide(bullet, self.enemy_sprites, False)
            if hit_enemies:
                bullet.kill()
                self.impact_sound.play()
                for enemy in hit_enemies:
                    enemy.destroy()

        player_hit = pygame.sprite.spritecollide(
            self.player, self.enemy_sprites, True, pygame.sprite.collide_mask
        )
        if player_hit:
            self.impact_sound.play()
            self.player.kill()
            self.running = False
            print("Game Over! You were hit by an enemy.")

    def run(self):
        while self.running:
            # delta time
            dt = self.clock.tick(60) / 1000
            # event loop
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

                if event.type == self.enemy_spawn_event:  # spawn enemies
                    self.spawn_enemies()

            # shoot and gun timer
            self.gun_timer()
            self.input()

            # update and draw
            self.check_collsions()
            self.all_sprites.update(dt)
            self.draw(self.display_surf)

        pygame.quit()


if __name__ == "__main__":
    game = Game()
    game.run()
