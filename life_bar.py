# life_bar.py

class LifeBar:
    def __init__(self, x, y):
        """
        x, y: posição onde a barra de vida será desenhada na tela.
        """
        self.x = x
        self.y = y
        # Dicionário mapeando os níveis de vida às imagens correspondentes
        self.imagens = {
            100: "life1",
            80: "life2",
            60: "life3",
            40: "life4",
            20: "life5",
            0:  "life6"
        }
        # Inicialmente, a vida é 100%
        self.vida_atual = 100

    def update(self, nova_vida):
        """
        Atualiza o valor atual da vida.
        """
        self.vida_atual = nova_vida

    def draw(self, screen):
        """
        Desenha a barra de vida na tela, escolhendo a imagem de acordo com o valor atual de vida.
        """
        if self.vida_atual > 80:
            imagem = self.imagens[100]
        elif self.vida_atual > 60:
            imagem = self.imagens[80]
        elif self.vida_atual > 40:
            imagem = self.imagens[60]
        elif self.vida_atual > 20:
            imagem = self.imagens[40]
        elif self.vida_atual > 0:
            imagem = self.imagens[20]
        else:
            imagem = self.imagens[0]

        # Desenha a imagem da barra de vida na posição (x, y)
        screen.blit(imagem, (self.x, self.y))
