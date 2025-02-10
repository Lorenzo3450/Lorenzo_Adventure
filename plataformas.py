from pgzero.actor import Actor     
from entity import Entity
from pygame import Rect


class Plataforma(Entity):
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



class PlataformaVertical(Entity):
    def __init__(self, x, y, segmentos):
        """
        :param x: posição x da plataforma (ponto de referência definido pelo designer)
        :param y: posição y da plataforma, representando a base (parte inferior) da plataforma
        :param segmentos: número de blocos que compõem a plataforma
        """
        self.segmentos = segmentos
        self.largura = 28            # Largura de cada bloco
        self.altura_bloco = 38       # Altura de cada bloco (certifique-se de que esse valor corresponde à imagem)
        altura_total = segmentos * self.altura_bloco

        # Se y representa a base, calculamos o topo da plataforma
        y_top = y - altura_total

        super().__init__(x, y_top, self.largura, altura_total)
        self.actor = Actor("plataforma1")
        self.actor.anchor = (0, 0)

    def draw(self):
        # Desenha cada bloco, de forma que fiquem encostados
        for i in range(self.segmentos):
            self.actor.x = self.x
            self.actor.y = self.y + i * (self.altura_bloco -10)
            self.actor.draw()
            
        # Desenha um retângulo ao redor da plataforma para visualização (por exemplo, em vermelho)
        rect = self.get_rect()
        

    def get_rect(self):
        """
        Retorna um pygame.Rect representando a área da plataforma.
        """
        return Rect(self.x, self.y, self.largura, self.segmentos * self.altura_bloco)
