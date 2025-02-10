import pygame  
from pgzero.actor import Actor
from entity import Entity

class Espinho(Entity):
    def __init__(self, x, y, largura=1):
        """
        :param x: posição x do espinho
        :param y: posição y do espinho
        :param largura: número de segmentos de espinhos (cada um tem 28px de largura)
        """
        altura = 28  # Altura do espinho
        largura_total = largura * 28  # Cada segmento do espinho tem 28px

        super().__init__(x, y+10, largura_total, altura)
        self.largura_segmentos = largura  # Quantidade de segmentos de espinhos
        self.actor = Actor("spikes")  # Certifique-se de ter a imagem "spikes" na pasta images
        self.damage = 20  # Valor do dano causado pelo espinho

        self.offset_x = -14  # Ajusta o deslocamento para trás (ajuste conforme necessário)

    def draw(self):
        # Desenha cada segmento de espinho com o deslocamento ajustado
        for i in range(self.largura_segmentos):
            self.actor.x = self.x + i * 28   # Aplica o deslocamento para trás
            self.actor.y = self.y
            self.actor.draw()

    def get_rect(self):
        """
        Retorna um pygame.Rect representando a área do espinho.
        """
        return pygame.Rect(
            self.x + self.offset_x,  # Usa o mesmo deslocamento do desenho
            self.y,
            self.largura,  # Usa a largura real do espinho
            self.altura
        )
