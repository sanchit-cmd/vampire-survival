import pygame


class AllSprites(pygame.sprite.Group):
    def __init__(self):
        super().__init__()
        self.display_surf = pygame.display.get_surface()
        self.offset = pygame.Vector2(0, 0)

    def draw(self, target_pos):
        self.offset.x = self.display_surf.get_width() // 2 - target_pos[0]
        self.offset.y = self.display_surf.get_height() // 2 - target_pos[1]

        ground_sprite = [sprite for sprite in self if hasattr(sprite, "ground")]
        object_sprite = [sprite for sprite in self if not hasattr(sprite, "ground")]

        for layer in [ground_sprite, object_sprite]:
            for sprite in sorted(layer, key=lambda sprite: sprite.rect.centery):
                self.display_surf.blit(sprite.image, sprite.rect.topleft + self.offset)
