import pygame


def load_map(path):
    pass

def save_map(name, game):
    pygame.image.save(game._bg, f'/maps/{name}.png')
    data = {
        'map_path': f'/maps/{name}.png',
        'checkpoints': game.checkpoints,
        'spawn_point': game.spawn,
    }


class MapConfig:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)
