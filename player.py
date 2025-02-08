import pygame
from pgzero.actor import Actor  
from pgzero.keyboard import keyboard
from pgzero.builtins import sounds   # Importa o objeto sounds
from entity import Entity, GRAVIDADE, PULO_FORCA, ANIMACAO_DELAY
from audio import play_sound  # Importa a função auxiliar para áudio

class Personagem(Entity):
    def __init__(self, plataformas, x_inicial=100, y_inicial=750):
        super().__init__(x_inicial, y_inicial, 25, 35)
        self.actor = Actor('heroknight_idle_0')
        self.actor.x = x_inicial
        self.actor.y = y_inicial

        # Listas de imagens para as animações

        # Parado
        self.images_idle_right = [
            'heroknight_idle_0', 'heroknight_idle_1', 'heroknight_idle_2', 'heroknight_idle_3',
            'heroknight_idle_4', 'heroknight_idle_5', 'heroknight_idle_6', 'heroknight_idle_7'
        ]
        self.images_idle_left = [
            'heroknight_idle_0_left', 'heroknight_idle_1_left', 'heroknight_idle_2_left', 'heroknight_idle_3_left',
            'heroknight_idle_4_left', 'heroknight_idle_5_left', 'heroknight_idle_6_left', 'heroknight_idle_7_left'
        ]
        
        # Correndo
        self.images_run_right = [
            'heroknight_run_0', 'heroknight_run_2', 'heroknight_run_3', 'heroknight_run_4',
            'heroknight_run_5', 'heroknight_run_6', 'heroknight_run_7', 'heroknight_run_8', 'heroknight_run_9'
        ]
        self.images_run_left = [
            'heroknight_run_0_left', 'heroknight_run_2_left', 'heroknight_run_3_left', 'heroknight_run_4_left',
            'heroknight_run_5_left', 'heroknight_run_6_left', 'heroknight_run_7_left', 'heroknight_run_8_left', 'heroknight_run_9_left'
        ]
        
        # Pulando 
        self.images_jump_right = ['heroknight_jump_0', 'heroknight_jump_1', 'heroknight_jump_2']
        self.images_jump_left = ['heroknight_jump_0_left', 'heroknight_jump_1_left', 'heroknight_jump_2_left']
        
        # Caindo
        self.images_fall_right = ['heroknight_fall_0', 'heroknight_fall_1', 'heroknight_fall_2', 'heroknight_fall_3']
        self.images_fall_left = ['heroknight_fall_0_left', 'heroknight_fall_1_left', 'heroknight_fall_2_left', 'heroknight_fall_3_left']
        
        # Atacando
        self.images_attack_right = [
            'heroknight_attack1_0', 'heroknight_attack1_1', 'heroknight_attack1_2', 
            'heroknight_attack1_3', 'heroknight_attack1_4', 'heroknight_attack1_5'
        ]
        self.images_attack_left = [
            'heroknight_attack1_0_left', 'heroknight_attack1_1_left', 'heroknight_attack1_2_left', 
            'heroknight_attack1_3_left', 'heroknight_attack1_4_left', 'heroknight_attack1_5_left'
        ]

        # Animação de tomar dano (hurt)
        self.images_hurt_right = ['heroknight_hurt_0', 'heroknight_hurt_1', 'heroknight_hurt_2']
        self.images_hurt_left = ['heroknight_hurt_0_left', 'heroknight_hurt_1_left', 'heroknight_hurt_2_left']

        self.current_image = 0
        self.current_images_list = self.images_idle_right  # Estado inicial: parado olhando para a direita
        self.is_moving = False
        self.facing_right = True  # Indica para onde o personagem está virado
        self.is_attacking = False  # Controle do ataque

        # Lógica de vida e dano
        self.health = 100              # Quantidade de vida
        self.is_hurt = False           # Flag para indicar dano
        self.invulnerable_timer = 0    # Timer de invulnerabilidade após dano

        # Física do pulo e gravidade
        self.vel_y = 0
        self.no_chao = True  # Flag indicando se o personagem está no chão

        # Controle da velocidade da animação
        self.frame_count = 0

        # Referência às plataformas
        self.plataformas = plataformas

        # Atributos para lógica de ataque
        self.attack_damage = 20       # Dano do ataque
        self.hit_enemies = []         # Inimigos já atingidos no ataque atual
        self.enemies = []             # Lista de inimigos (a ser atribuída externamente)

        # Atributo para controlar o tempo entre passos
        self.footstep_timer = 0

    def update(self):
        # Atualiza o timer de invulnerabilidade
        if self.invulnerable_timer > 0:
            self.invulnerable_timer -= 1

        # Se estiver no estado de dano, atualiza somente a animação de dano
        if self.is_hurt:
            self.update_image_hurt()
            return

        # Se estiver atacando, atualiza a animação e verifica se o ataque acerta inimigos
        if self.is_attacking:
            self.update_image()
            if self.attack_hit_active():
                self.check_attack_hit()
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

        # Limita o personagem dentro da tela
        self.actor.x = max(0, min(self.actor.x, 1200))

        # Toca o som de caminhada (a cada 20 frames, por exemplo)
        if self.is_moving:
            self.footstep_timer -= 1
            if self.footstep_timer <= 0:
                play_sound(sounds.human_walk)  # Toca o som de passos
                self.footstep_timer = 20
        else:
            self.footstep_timer = 0

        # Pulo: verifica se está no chão para poder pular
        if keyboard.W and self.no_chao:
            self.vel_y = PULO_FORCA
            self.no_chao = False
            play_sound(sounds.human_jump)  # Toca o som de pulo

        # Aplica a gravidade
        self.vel_y += GRAVIDADE
        self.actor.y += self.vel_y

        # Atualiza a posição central (x, y) do personagem
        self.x = self.actor.x
        self.y = self.actor.y

        # Verifica colisões com as plataformas
        self.verificar_colisoes()

        # Atualiza a animação conforme o estado do personagem
        if not self.no_chao:  # Se estiver no ar
            if self.vel_y < 0:
                self.current_images_list = self.images_jump_right if self.facing_right else self.images_jump_left
            else:
                self.current_images_list = self.images_fall_right if self.facing_right else self.images_fall_left
        elif not self.is_moving:  # Parado no chão
            self.current_images_list = self.images_idle_right if self.facing_right else self.images_idle_left

        self.update_image()

    def update_image(self):
        """Atualiza a animação padrão (movimentos, ataque, etc.)."""
        self.frame_count += 1
        if self.frame_count >= ANIMACAO_DELAY:
            self.current_image += 1

            # Se estiver atacando e a animação acabar, volta ao estado normal
            if self.is_attacking:
                if self.current_image >= len(self.current_images_list):
                    self.is_attacking = False
                    self.current_images_list = self.images_idle_right if self.facing_right else self.images_idle_left
                    self.current_image = 0
            else:
                self.current_image %= len(self.current_images_list)

            self.actor.image = self.current_images_list[self.current_image]
            self.frame_count = 0

    def update_image_hurt(self):
        """Atualiza a animação de dano (quando o personagem toma dano)."""
        self.frame_count += 1
        if self.frame_count >= ANIMACAO_DELAY:
            self.current_image += 1
            if self.current_image >= len(self.current_images_list):
                # Ao terminar a animação de dano, volta ao estado normal
                self.is_hurt = False
                self.current_images_list = self.images_idle_right if self.facing_right else self.images_idle_left
                self.current_image = 0
            self.actor.image = self.current_images_list[self.current_image]
            self.frame_count = 0

    def take_damage(self, damage):
        """
        Aplica dano ao personagem, respeitando o período de invulnerabilidade.
        """
        if self.invulnerable_timer > 0:
            return

        self.health -= damage
        if self.health < 0:
            self.health = 0
            # Aqui pode ser implementada a lógica de morte
        play_sound(sounds.human_damage)  # Toca o som de dano
        self.is_hurt = True
        self.current_image = 0
        self.current_images_list = self.images_hurt_right if self.facing_right else self.images_hurt_left
        self.invulnerable_timer = 30  # Exemplo: 60 frames de invulnerabilidade

    def on_mouse_down(self):
        """Inicia o ataque ao clicar o botão do mouse."""
        if not self.is_attacking:
            play_sound(sounds.human_atk_sword)  # Toca o som de ataque
            self.is_attacking = True
            self.current_image = 0
            self.current_images_list = self.images_attack_right if self.facing_right else self.images_attack_left
            self.hit_enemies = []  # Reinicia a lista de inimigos atingidos no ataque

    def get_attack_hitbox(self):
        """
        Retorna um objeto pygame.Rect representando a área de alcance do ataque.
        O cálculo considera que x e y são o centro do personagem.
        """
        hitbox_width = 30   # Largura da área de ataque
        hitbox_height = self.altura  # Usa a altura definida em Entity
        if self.facing_right:
            hitbox_x = self.x + self.largura / 2
        else:
            hitbox_x = self.x - self.largura / 2 - hitbox_width
        hitbox_y = self.y - self.altura / 2
        return pygame.Rect(hitbox_x, hitbox_y, hitbox_width, hitbox_height)

    def attack_hit_active(self):
        """
        Retorna True se o frame atual do ataque estiver ativo para aplicar dano.
        Exemplo: frames 2 a 4 da animação de ataque.
        """
        return 2 <= self.current_image <= 4

    def check_attack_hit(self):
        """
        Verifica se o hitbox do ataque colide com algum inimigo.
        Caso positivo e o inimigo ainda não tenha sido atingido neste ataque,
        aplica o dano a ele.
        """
        hitbox = self.get_attack_hitbox()
        for enemy in self.enemies:
            enemy_rect = pygame.Rect(
                enemy.x - enemy.largura / 2,
                enemy.y - enemy.altura / 2,
                enemy.largura, enemy.altura
            )
            if hitbox.colliderect(enemy_rect) and enemy not in self.hit_enemies:
                enemy.take_damage(self.attack_damage)
                self.hit_enemies.append(enemy)

    def draw(self):
        self.actor.draw()

    def verificar_colisoes(self):
        """Verifica a colisão do personagem com as plataformas."""
        for plataforma in self.plataformas:
            if self.verificar_colisao_com(plataforma, self.vel_y):
                self.actor.y = plataforma.y
                self.vel_y = 0
                self.no_chao = True
                return
        self.no_chao = False
