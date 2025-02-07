from pgzero.actor import Actor
from pgzero.keyboard import keyboard

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

    def verificar_colisao_com(self, outra_entidade, vel_y=0):
        """
        Verifica se esta entidade colide com outra_entidade.
        A condição de colisão foi definida de forma semelhante à utilizada
        na classe Personagem original para as plataformas.
        """
        if (
            self.x > outra_entidade.x - outra_entidade.largura // 2 and
            self.x < outra_entidade.x + outra_entidade.largura // 2 and
            self.y + vel_y >= outra_entidade.y
        ):
            return True
        return False
