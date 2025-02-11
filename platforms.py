from pgzero.actor import Actor
from entity import Entity
from pygame import Rect


class Platforms(Entity):
    def __init__(self, x, y, segmentos):
        """
        :param x: posição x da plataforma (ponto de referência definido pelo designer)
        :param y: posição y da plataforma
        :param segmentos: número de blocos que compõem a plataforma
        """
        self.segmentos = segmentos
        largura_total = segmentos * 28   # Cada bloco tem 28 pixels de largura
        altura = 38                      # Altura da imagem da plataforma

        # Define os offsets que serão usados para desenho e colisão
        self.offset_x = -20  # Ex.: deslocamento para ajustar horizontalmente
        self.offset_y = 20   # Ex.: deslocamento para ajustar verticalmente

        super().__init__(x, y, largura_total, altura)
        self.actor = Actor("plataforma1")
        # Usa o canto superior esquerdo como âncora para facilitar o posicionamento
        self.actor.anchor = (0, 0)

    def draw(self):
        # Desenha cada bloco da plataforma aplicando os offsets definidos
        for i in range(self.segmentos):
            self.actor.x = self.x + i * 28 + self.offset_x
            self.actor.y = self.y + self.offset_y
            self.actor.draw()

    def get_rect(self):
        """
        Retorna um pygame.Rect representando a área da plataforma,
        considerando os offsets de desenho.
        """
        return Rect(self.x + self.offset_x,
                    self.y + self.offset_y,
                    self.largura,
                    self.altura)


