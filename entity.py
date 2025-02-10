from pygame import Rect


# Constantes do jogo
CHAO_Y = 700
GRAVIDADE = 0.5      # Ajuste conforme necessário
PULO_FORCA = -10     # Força do pulo
ANIMACAO_DELAY = 5   # Número de frames entre troca de imagem


class Entity:
    def __init__(self, x, y, largura, altura):
        self.x = x
        self.y = y
        self.largura = largura
        self.altura = altura

    def get_rect(self):
        # Considerando que x e y representam o canto superior esquerdo
        return Rect(self.x, self.y, self.largura, self.altura)

    def verificar_colisao_com(self, outra_entidade, vel_y=0):
        self_rect = Rect(self.x, self.y + vel_y, self.largura, self.altura)
        outra_rect = outra_entidade.get_rect()
        return self_rect.colliderect(outra_rect)
