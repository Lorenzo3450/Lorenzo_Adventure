from pgzero.actor import Actor
from pgzero.keyboard import keyboard
from entity import Entity
from entity import GRAVIDADE, PULO_FORCA, ANIMACAO_DELAY

class Personagem(Entity):
    def __init__(self, plataformas, x_inicial=100, y_inicial=750):
        # Considera-se que o personagem possui 50x50 (ajuste se necessário)
        super().__init__(x_inicial, y_inicial, 50, 50)
        self.actor = Actor('heroknight_idle_0')
        self.actor.x = x_inicial
        self.actor.y = y_inicial

        # Listas de imagens

        # Parado
        self.images_idle_right = ['heroknight_idle_0', 'heroknight_idle_1', 'heroknight_idle_2', 'heroknight_idle_3',
                                  'heroknight_idle_4', 'heroknight_idle_5', 'heroknight_idle_6', 'heroknight_idle_7']
        self.images_idle_left = ['heroknight_idle_0_left', 'heroknight_idle_1_left', 'heroknight_idle_2_left', 'heroknight_idle_3_left',
                                 'heroknight_idle_4_left', 'heroknight_idle_5_left', 'heroknight_idle_6_left', 'heroknight_idle_7_left']
        
        # Correndo
        self.images_run_right = ['heroknight_run_0', 'heroknight_run_2', 'heroknight_run_3', 'heroknight_run_4',
                                 'heroknight_run_5', 'heroknight_run_6', 'heroknight_run_7', 'heroknight_run_8', 'heroknight_run_9']
        self.images_run_left = ['heroknight_run_0_left', 'heroknight_run_2_left', 'heroknight_run_3_left', 'heroknight_run_4_left',
                                'heroknight_run_5_left', 'heroknight_run_6_left', 'heroknight_run_7_left', 'heroknight_run_8_left', 'heroknight_run_9_left']
        
        # Pulando 
        self.images_jump_right = ['heroknight_jump_0', 'heroknight_jump_1', 'heroknight_jump_2']
        self.images_jump_left = ['heroknight_jump_0_left', 'heroknight_jump_1_left', 'heroknight_jump_2_left']
        
        # Caindo
        self.images_fall_right = ['heroknight_fall_0', 'heroknight_fall_1', 'heroknight_fall_2', 'heroknight_fall_3']
        self.images_fall_left = ['heroknight_fall_0_left', 'heroknight_fall_1_left', 'heroknight_fall_2_left', 'heroknight_fall_3_left']
        
        # Atacando
        self.images_attack_right = ['heroknight_attack1_0', 'heroknight_attack1_1', 'heroknight_attack1_2', 
                                    'heroknight_attack1_3', 'heroknight_attack1_4', 'heroknight_attack1_5']
        self.images_attack_left = ['heroknight_attack1_0_left', 'heroknight_attack1_1_left', 'heroknight_attack1_2_left', 
                                    'heroknight_attack1_3_left', 'heroknight_attack1_4_left', 'heroknight_attack1_5_left']

        self.current_image = 0
        self.current_images_list = self.images_idle_right  # Começa parado
        self.is_moving = False
        self.facing_right = True  # Indica para onde o personagem está virado
        self.is_attacking = False  # Controle do ataque

        # Física do pulo e gravidade
        self.vel_y = 0
        self.no_chao = True  # Indica se o personagem está no chão

        # Controle da velocidade da animação
        self.frame_count = 0

        # Referência às plataformas
        self.plataformas = plataformas

    def update(self):
        # Se estiver atacando, não pode se mover até terminar a animação de ataque
        if self.is_attacking:
            self.update_image()
            return

        # Movimento horizontal
        if keyboard.A:
            self.current_images_list = self.images_run_left
            self.is_moving = True
            self.facing_right = False
            self.actor.x -= 5
        elif keyboard.D:
            self.current_images_list = self.images_run_right
            self.is_moving = True
            self.facing_right = True
            self.actor.x += 5
        else:
            self.is_moving = False

        # Impede que o personagem saia da tela
        self.actor.x = max(0, min(self.actor.x, 1200))  # Mantém dentro da largura da tela

        # Pulo
        if keyboard.W and self.no_chao:  # Só pode pular se estiver no chão
            self.vel_y = PULO_FORCA
            self.no_chao = False  # No ar

        # Aplicando gravidade
        self.vel_y += GRAVIDADE
        self.actor.y += self.vel_y

        # Atualiza a posição da entidade com a do actor
        self.x = self.actor.x
        self.y = self.actor.y

        # Verifica colisão com plataformas utilizando o método da classe Entity
        self.verificar_colisoes()

        # Atualiza animação baseada no estado do personagem
        if not self.no_chao:  # No ar
            if self.vel_y < 0:  # Subindo (pulando)
                self.current_images_list = self.images_jump_right if self.facing_right else self.images_jump_left
            else:  # Descendo (caindo)
                self.current_images_list = self.images_fall_right if self.facing_right else self.images_fall_left
        elif not self.is_moving:  # Parado no chão
            self.current_images_list = self.images_idle_right if self.facing_right else self.images_idle_left

        # Atualiza imagem
        self.update_image()

    def update_image(self):
        self.frame_count += 1
        if self.frame_count >= ANIMACAO_DELAY:
            self.current_image += 1

            # Se estiver atacando e chegou ao final da animação de ataque, volta ao estado normal
            if self.is_attacking:
                if self.current_image >= len(self.current_images_list):
                    self.is_attacking = False
                    self.current_images_list = self.images_idle_right if self.facing_right else self.images_idle_left
                    self.current_image = 0
            else:
                self.current_image %= len(self.current_images_list)

            self.actor.image = self.current_images_list[self.current_image]
            self.frame_count = 0  # Reinicia o contador

    def on_mouse_down(self):
        """Ativa o ataque quando o botão do mouse for pressionado."""
        if not self.is_attacking:
            self.is_attacking = True
            self.current_image = 0
            self.current_images_list = self.images_attack_right if self.facing_right else self.images_attack_left

    def draw(self):
        self.actor.draw()

    def verificar_colisoes(self):
        """Verifica colisão do personagem com as plataformas utilizando o método da Entity."""
        for plataforma in self.plataformas:
            if self.verificar_colisao_com(plataforma, self.vel_y):
                self.actor.y = plataforma.y
                self.vel_y = 0
                self.no_chao = True
                return
        # Caso não esteja colidindo com nenhuma plataforma, mantém o personagem no ar
        self.no_chao = False
