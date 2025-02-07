from pgzero.actor import Actor
from entity import Entity  # Certifique-se de que entity.py esteja disponível

# Constantes do jogo
CHAO_Y = 700
ANIMACAO_DELAY = 5
GRAVIDADE = 1
VELOCIDADE_QUEDA_MAX = 10
VELOCIDADE_CORRIDA = 2  # Velocidade ajustada para patrulhamento

class Inimigo(Entity):
    def __init__(self, imagens_idle_right, imagens_idle_left, 
                 imagens_attack_right, imagens_attack_left, 
                 imagens_dano_right, imagens_dano_left, 
                 imagens_run_right, imagens_run_left, 
                 imagens_death_right, imagens_death_left,
                 vida, dano, posicao_inicial_x, posicao_inicial_y,
                 plataformas):
        # Definindo um tamanho padrão para o inimigo (ajuste conforme necessário)
        largura_padrao = 50
        altura_padrao = 50
        super().__init__(posicao_inicial_x, posicao_inicial_y, largura_padrao, altura_padrao)
        
        self.actor = Actor(imagens_idle_right[0])
        self.actor.x = posicao_inicial_x
        self.actor.y = posicao_inicial_y
        
        # Animações
        self.images_idle_right   = imagens_idle_right
        self.images_idle_left    = imagens_idle_left
        self.images_attack_right = imagens_attack_right
        self.images_attack_left  = imagens_attack_left
        self.images_dano_right   = imagens_dano_right
        self.images_dano_left    = imagens_dano_left
        self.images_run_right    = imagens_run_right
        self.images_run_left     = imagens_run_left
        self.images_death_right  = imagens_death_right
        self.images_death_left   = imagens_death_left

        # Estado inicial
        self.current_image = 0
        # Definindo uma lista de imagens padrão para quando o inimigo não está realizando outra ação.
        self.current_images_list = self.images_idle_right  
        self.is_attacking     = False  
        self.is_running       = False    
        self.is_taking_damage = False  
        self.is_dying         = False
        self.facing_right     = True  
        self.is_moving        = True  # Adicionado para garantir o patrulhamento
        
        # Vida e dano
        self.vida  = vida
        self.dano  = dano
        
        # Controle da velocidade da animação
        self.frame_count = 0
        
        # Físicas
        self.velocidade_y = 0
        self.no_chao = False
        self.plataformas = plataformas  # Lista de plataformas

    def update(self):
        if self.is_dying:
            # Atualiza a animação de morte; se finish_on_end for True, a animação para na última imagem
            self.update_image(self.images_death_right if self.facing_right else self.images_death_left, finish_on_end=True)
            return

        # Movimento do inimigo (patrulhamento automático)
        if self.is_moving:
            if self.facing_right:
                self.actor.x += VELOCIDADE_CORRIDA
                self.current_images_list = self.images_run_right
            else:
                self.actor.x -= VELOCIDADE_CORRIDA
                self.current_images_list = self.images_run_left

            # Alternar direção caso bata em um limite
            if self.actor.x >= 1200:
                self.facing_right = False
            elif self.actor.x <= 0:
                self.facing_right = True

        # Aplicando gravidade
        self.velocidade_y += GRAVIDADE
        if self.velocidade_y > VELOCIDADE_QUEDA_MAX:
            self.velocidade_y = VELOCIDADE_QUEDA_MAX
        self.actor.y += self.velocidade_y

        # Sincroniza a posição da Entity com a do actor (útil para as colisões)
        self.x = self.actor.x
        self.y = self.actor.y

        # Verificar colisão com as plataformas utilizando o método da Entity
        self.verificar_colisoes()

        # Atualizar animação
        self.update_image()

    def update_image(self, images_list=None, finish_on_end=False):
        """
        Atualiza a imagem atual da animação.
        Se images_list for fornecida, usa-a; caso contrário, utiliza self.current_images_list.
        Se finish_on_end for True, a animação para na última imagem.
        """
        if images_list is None:
            images_list = self.current_images_list
        self.frame_count += 1
        if self.frame_count >= ANIMACAO_DELAY:
            self.current_image += 1
            if finish_on_end and self.current_image >= len(images_list):
                self.current_image = len(images_list) - 1  # Fica na última imagem
            else:
                self.current_image %= len(images_list)
            self.actor.image = images_list[self.current_image]
            self.frame_count = 0

    def verificar_colisoes(self):
        """Verifica colisão do inimigo com as plataformas utilizando o método da Entity."""
        self.no_chao = False  # Reinicia o status de estar no chão antes de verificar
        for plataforma in self.plataformas:
            if self.verificar_colisao_com(plataforma, self.velocidade_y):
                self.actor.y = plataforma.y
                self.velocidade_y = 0
                self.no_chao = True
                break  # Para de procurar após encontrar uma colisão
        
        if not self.no_chao:
            self.velocidade_y = min(self.velocidade_y, VELOCIDADE_QUEDA_MAX)

    def draw(self):
        # Ajuste de deslocamento para mover a imagem para cima
        deslocamento_y = 10  # Ajuste conforme necessário
        self.actor.y -= deslocamento_y  # Ajusta a posição Y do ator
        self.actor.draw()  # Chama o método de desenho sem passar parâmetros extras
        self.actor.y += deslocamento_y  # Restaura a posição Y após o desenho