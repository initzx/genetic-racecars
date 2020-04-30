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
        self.map = kwargs.get('map')
        self.map_path = kwargs.get('map_path')
        self.checkpoints = kwargs.get('checkpoints')
        self.spawn_point = kwargs.get('spawn_point')
        self.cars = kwargs.get('cars')
        self.max_loop_time = kwargs.get('max_loop_time')
