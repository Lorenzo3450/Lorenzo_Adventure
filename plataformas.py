from pgzero.actor import Actor  
from entity import Entity

class Plataforma(Entity):
    def __init__(self, x, y, largura):
        super().__init__(x, y, largura * 28, 38)  # A plataforma agora é uma entidade com largura e altura
        self.actor = Actor("plataforma1")  # Imagem da plataforma

    def draw(self):
        # Desenha a imagem repetidamente até cobrir a largura da plataforma
        for i in range(0, self.largura, self.actor.width):  # Usa a largura da imagem para repetir
            self.actor.x = self.x + i - 84  # Ajuste correto para garantir que as imagens se alinhem corretamente
            self.actor.y = self.y + 38  # Ajusta para garantir o alinhamento correto
            self.actor.draw()
