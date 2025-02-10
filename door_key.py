from pgzero.actor import Actor
from audio import play_sound  # Importa a função auxiliar para áudio
from pgzero.builtins import sounds   # Importa o objeto sounds
# Adicione estas classes no início do arquivo, após as outras importações


class Key:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.actor = Actor('chave')  # Certifique-se de ter a imagem 'key.png'
        self.actor.pos = (x, y)
        self.is_collected = False

    def draw(self):
        if not self.is_collected:
            self.actor.draw()

    def check_collision(self, player_rect):
        if self.is_collected:
            return False
        return self.actor.colliderect(player_rect)


class Door:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.locked = True
        self.is_opening = False
        self.is_open = False
        self.animation_frames = ['opening_0', 'opening_1',
                                 'opening_2', 'opening_3', 'opening_4']  # Nomes das imagens
        self.current_frame = 0
        self.animation_timer = 0
        self.animation_speed = 0.2  # Segundos por frame
        self.actor = Actor(self.animation_frames[0], (x, y))

    def unlock(self):
        if self.locked:
            self.locked = False
            self.is_opening = True
            play_sound(sounds.pega_chave)  # Adicione um som de abertura

    def update(self, dt):
        if self.is_opening and not self.is_open:
            self.animation_timer += dt
            if self.animation_timer >= self.animation_speed:
                self.animation_timer = 0
                if self.current_frame < len(self.animation_frames) - 1:
                    self.current_frame += 1
                    self.actor.image = self.animation_frames[self.current_frame]
                else:
                    self.is_open = True
                    self.is_opening = False

    def draw(self):
        self.actor.draw()
