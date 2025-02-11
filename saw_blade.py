from pygame import Rect
from pgzero.actor import Actor
from entity import Entity

class Saw_Blade(Entity):
    def __init__(self, x_inicial, y, x_final):
        """
        Inicializa a serra animada que se move entre x_inicial e x_final.
        
        Características:
          - Dimensões: 39 x 38 pixels.
          - Animação: As imagens de "serra_0" até "serra_7" representam a rotação para a esquerda.
            Para a rotação para a direita, a sequência é invertida (de "serra_7" a "serra_0").
          - Movimento horizontal entre x_inicial e x_final.
          - Causa dano (valor configurável).
        """
        # Inicializa a entidade com as dimensões especificadas
        super().__init__(x_inicial, y, 39, 38)
        self.x_inicial = x_inicial
        self.x_final = x_final
        self.damage = 20  # Ajuste o valor do dano conforme necessário

        # Configura o ator com a imagem inicial
        self.actor = Actor("serra_0")
        
        # Define as sequências de animação:
        # Para a rotação à esquerda, usamos a sequência natural.
        self.anim_left = [f"serra_{i}" for i in range(8)]
        # Para a rotação à direita, invertemos a sequência.
        self.anim_right = self.anim_left[::-1]
        
        # Estado inicial: movimento para a direita
        self.facing_right = True
        self.current_frame = 0
        self.frame_delay = 5   # Número de atualizações antes de trocar o frame (pode ser ajustado)
        self.frame_counter = 0
        
        # Velocidade horizontal da serra (em pixels por update)
        self.speed = 2

    def update(self):
        # Atualiza a animação: incrementa o contador de frames e, se ultrapassar o delay, troca o frame.
        self.frame_counter += 1
        if self.frame_counter >= self.frame_delay:
            self.current_frame = (self.current_frame + 1) % len(self.anim_left)
            self.frame_counter = 0

        # Atualiza a imagem do ator de acordo com a direção:
        if self.facing_right:
            self.actor.image = self.anim_right[self.current_frame]
        else:
            self.actor.image = self.anim_left[self.current_frame]

        # Atualiza o movimento horizontal:
        if self.facing_right:
            self.x += self.speed
            if self.x >= self.x_final:
                self.x = self.x_final
                self.facing_right = False  # Inverte a direção ao atingir o limite
                self.current_frame = 0    # Reinicia a animação, se desejado
        else:
            self.x -= self.speed
            if self.x <= self.x_inicial:
                self.x = self.x_inicial
                self.facing_right = True
                self.current_frame = 0

        # Sincroniza a posição do ator com a posição atual da serra
        self.actor.x = self.x
        self.actor.y = self.y

    def draw(self):
        self.actor.draw()

    def get_rect(self):
        """
        Retorna um pygame.Rect representando a área da serra para detecção de colisões.
        """
        return Rect(self.x, self.y, self.largura, self.altura)
