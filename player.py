from pgzero.actor import Actor    
from pgzero.keyboard import keyboard
from pgzero.builtins import sounds   # Importa o objeto sounds
from entity import Entity, GRAVIDADE, PULO_FORCA, ANIMACAO_DELAY
from audio import play_sound  # Função auxiliar para áudio
from pygame import Rect

class Personagem(Entity):
    def __init__(self, plataformas,life_bar, x_inicial=100, y_inicial=750):
        super().__init__(x_inicial, y_inicial, 25, 35)
        self.actor = Actor('heroknight_idle_0')
        self.actor.x = x_inicial
        self.actor.y = y_inicial
        self.life_bar = life_bar

        # --- Animações padrão ---

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

        # Tomando dano (hurt)
        self.images_hurt_right = ['heroknight_hurt_0', 'heroknight_hurt_1', 'heroknight_hurt_2']
        self.images_hurt_left = ['heroknight_hurt_0_left', 'heroknight_hurt_1_left', 'heroknight_hurt_2_left']

        # --- Animações novas ---

        # Bloqueando (estado normal de bloqueio – o personagem levanta o escudo) 
        self.images_block_idle_right = [
            'heroknight_block_idle_0', 'heroknight_block_idle_1', 'heroknight_block_idle_2',
            'heroknight_block_idle_3', 'heroknight_block_idle_4', 'heroknight_block_idle_5',
            'heroknight_block_idle_6', 'heroknight_block_idle_7'
        ]
        self.images_block_idle_left = [
            'heroknight_block_idle_0_left', 'heroknight_block_idle_1_left', 'heroknight_block_idle_2_left',
            'heroknight_block_idle_3_left', 'heroknight_block_idle_4_left', 'heroknight_block_idle_5_left',
            'heroknight_block_idle_6_left', 'heroknight_block_idle_7_left'
        ]

        # Bloqueio de ataque (quando o personagem bloqueia o impacto do ataque inimigo)
        self.images_block_attack_right = [
            'heroknight_block_0', 'heroknight_block_1', 'heroknight_block_2',
            'heroknight_block_3', 'heroknight_block_4'
        ]
        self.images_block_attack_left = [
            'heroknight_block_0_left', 'heroknight_block_1_left', 'heroknight_block_2_left',
            'heroknight_block_3_left', 'heroknight_block_4_left'
        ]
        self.is_blocking_attack = False

        # Morte
        self.images_death_right = [
            'heroknight_death_0', 'heroknight_death_1', 'heroknight_death_2',
            'heroknight_death_3', 'heroknight_death_4', 'heroknight_death_5',
            'heroknight_death_6', 'heroknight_death_7', 'heroknight_death_8',
            'heroknight_death_9'
        ]
        self.images_death_left = [
            'heroknight_death_0_left', 'heroknight_death_1_left', 'heroknight_death_2_left',
            'heroknight_death_3_left', 'heroknight_death_4_left', 'heroknight_death_5_left',
            'heroknight_death_6_left', 'heroknight_death_7_left', 'heroknight_death_8_left',
            'heroknight_death_9_left'
]


        # Estado e controle de animação
        self.current_image = 0
        self.current_images_list = self.images_idle_right  # Inicia parado, olhando para a direita
        self.is_moving = False
        self.facing_right = True     # Direção que o personagem está virado
        self.is_attacking = False    # Estado de ataque
        self.is_blocking = False     # Estado de bloqueio (escudo levantado)
        self.is_dead = False         # Estado de morte

        # Lógica de vida/dano
        self.health = 100            # Vida
        self.is_hurt = False         # Indicador de dano
        self.invulnerable_timer = 0  # Timer de invulnerabilidade após dano

        # Física de pulo e gravidade
        self.vel_y = 0
        self.no_chao = True          # Indicador se está no chão

        # Controle da velocidade da animação
        self.frame_count = 0

        # Referência às plataformas
        self.plataformas = plataformas

        # Lógica de ataque
        self.attack_damage = 20      # Dano do ataque
        self.hit_enemies = []        # Inimigos já atingidos neste ataque
        self.enemies = []            # Lista de inimigos (será atribuída externamente)

        # Timer para passos
        self.footstep_timer = 0

    def update(self):
        # Se o personagem estiver morto, atualiza a animação de morte e não permite outras ações
        if self.is_dead:
            self.update_image_death()
            return

        # Atualiza o timer de invulnerabilidade
        if self.invulnerable_timer > 0:
            self.invulnerable_timer -= 1

        # Se estiver no estado de dano, atualiza apenas a animação de dano
        if self.is_hurt:
            self.update_image_hurt()
            return

        # Se estiver executando a animação de bloqueio de ataque, processa-a com prioridade
        if self.is_blocking_attack:
            self.update_image_block_attack()
            return

        # Se estiver bloqueando (apenas mantendo o escudo levantado), atualiza a animação de bloqueio
        if self.is_blocking:
            self.current_images_list = self.images_block_idle_right if self.facing_right else self.images_block_idle_left
            self.update_image_block()
            return

        # Se estiver atacando, atualiza a animação de ataque e checa colisões com inimigos
        if self.is_attacking:
            self.update_image()
            if self.attack_hit_active():
                self.check_attack_hit()
            return

        # --- Processamento de movimento normal ---
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

        # Toca som de passos a cada 20 frames (se estiver se movendo)
        if self.is_moving:
            self.footstep_timer -= 1
            if self.footstep_timer <= 0:
                play_sound(sounds.human_walk)
                self.footstep_timer = 20
        else:
            self.footstep_timer = 0

        # Pulo (se estiver no chão)
        if keyboard.W and self.no_chao:
            self.vel_y = PULO_FORCA
            self.no_chao = False
            play_sound(sounds.human_jump)

        # Processamento de movimento horizontal, pulo, etc.
        if keyboard.W and self.no_chao:
            self.vel_y = PULO_FORCA
            self.no_chao = False
            play_sound(sounds.human_jump)

        # Armazena a posição Y anterior (antes de aplicar gravidade)
        old_y = self.actor.y

        # Aplica a gravidade e atualiza a posição vertical
        self.vel_y += GRAVIDADE
        self.actor.y += self.vel_y

        # Atualiza a posição central
        self.x = self.actor.x
        self.y = self.actor.y

        # Verifica colisões passando também o old_y
        self.verificar_colisoes()

        # Define a animação de acordo com o estado (no ar ou parado)
        if not self.no_chao:
            if self.vel_y < 0:
                self.current_images_list = self.images_jump_right if self.facing_right else self.images_jump_left
            else:
                self.current_images_list = self.images_fall_right if self.facing_right else self.images_fall_left
        elif not self.is_moving:
            self.current_images_list = self.images_idle_right if self.facing_right else self.images_idle_left

    

        # Atualiza a posição central
        self.x = self.actor.x
        self.y = self.actor.y

        
        self.update_image()

    def update_image(self):
        """Atualiza a animação padrão (movimento, ataque, etc.)."""
        self.frame_count += 1
        if self.frame_count >= ANIMACAO_DELAY:
            self.current_image += 1

            # Se estiver atacando e a animação terminar, volta ao estado normal
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
        """Atualiza a animação de dano."""
        self.frame_count += 1
        if self.frame_count >= ANIMACAO_DELAY:
            self.current_image += 1
            if self.current_image >= len(self.current_images_list):
                self.is_hurt = False
                self.current_images_list = self.images_idle_right if self.facing_right else self.images_idle_left
                self.current_image = 0
            self.actor.image = self.current_images_list[self.current_image]
            self.frame_count = 0

    def update_image_block(self):
        """Atualiza a animação de bloqueio (mantém o escudo levantado, em loop)."""
        self.frame_count += 1
        if self.frame_count >= ANIMACAO_DELAY:
            self.current_image = (self.current_image + 1) % len(self.current_images_list)
            self.actor.image = self.current_images_list[self.current_image]
            self.frame_count = 0

    def update_image_block_attack(self):
        """
        Atualiza a animação de bloqueio de ataque.
        Essa é uma animação não em loop; quando terminar, retorna ao estado de bloqueio (se o botão ainda estiver pressionado)
        ou ao estado normal (caso contrário).
        """
        self.frame_count += 1
        if self.frame_count >= ANIMACAO_DELAY:
            self.current_image += 1
            if self.current_image >= len(self.current_images_list):
                # Finalizada a animação de bloqueio de ataque:
                self.is_blocking_attack = False
                self.current_image = 0
                # Se o botão de bloqueio ainda estiver pressionado, mantém a animação de bloqueio;
                # caso contrário, volta à animação idle.
                if self.is_blocking:
                    self.current_images_list = self.images_block_idle_right if self.facing_right else self.images_block_idle_left
                else:
                    self.current_images_list = self.images_idle_right if self.facing_right else self.images_idle_left
                self.actor.image = self.current_images_list[self.current_image]
            else:
                self.actor.image = self.current_images_list[self.current_image]
            self.frame_count = 0

    def update_image_death(self):
        """
        Atualiza a animação de morte. Quando terminar, o personagem permanece na última frame.
        """
        self.frame_count += 1
        if self.frame_count >= ANIMACAO_DELAY:
            if self.current_image < len(self.current_images_list) - 1:
                self.current_image += 1
                self.actor.image = self.current_images_list[self.current_image]
            self.frame_count = 0

    def take_damage(self, damage):
        """
        Aplica dano ao personagem, considerando invulnerabilidade e bloqueio.
        Se o personagem estiver bloqueando, em vez de receber dano, dispara a animação de bloqueio de ataque.
        Se a vida chegar a 0, inicia a animação de morte.
        """
        if self.is_dead:
            return

        # Se estiver bloqueando, ativa a animação de bloqueio de ataque (se ainda não estiver ocorrendo)
        if self.is_blocking:
            if not self.is_blocking_attack:
                self.is_blocking_attack = True
                self.current_image = 0
                self.current_images_list = self.images_block_attack_right if self.facing_right else self.images_block_attack_left
                play_sound(sounds.escudo_impact)  # Som de impacto no bloqueio
            return

        if self.invulnerable_timer > 0:
            return

        self.health -= damage
        if damage > 0:
            # Atualiza a barra de vida através da referência armazenada
            if self.life_bar is not None:
                self.life_bar.atualizar(self.health)

        if self.health <= 0:
            self.health = 0
            self.is_dead = True
            self.current_image = 0
            self.current_images_list = self.images_death_right if self.facing_right else self.images_death_left
            play_sound(sounds.death_sound)
            return

        play_sound(sounds.human_damage)
        self.is_hurt = True
        self.current_image = 0
        self.current_images_list = self.images_hurt_right if self.facing_right else self.images_hurt_left
        self.invulnerable_timer = 30  # Exemplo: 30 frames de invulnerabilidade

    def on_mouse_down(self, pos, button):
        # Se o personagem não estiver no chão, ignora o comando
        if not self.no_chao:
            return

        if button == "left" and not self.is_attacking and not self.is_blocking:
            play_sound(sounds.human_atk_sword)
            self.is_attacking = True
            self.current_image = 0
            self.current_images_list = self.images_attack_right if self.facing_right else self.images_attack_left
            self.hit_enemies = []
        elif button == "right":
            self.is_blocking = True
            self.current_image = 0
            self.current_images_list = self.images_block_idle_right if self.facing_right else self.images_block_idle_left
            play_sound(sounds.pega_chave)

    def on_mouse_up(self, pos, button):
        # Se o personagem não estiver no chão, pode ignorar o fim do bloqueio ou forçar seu cancelamento
        if not self.no_chao:
            return

        if button == "right":
            self.is_blocking = False
            self.current_image = 0
            self.current_images_list = self.images_idle_right if self.facing_right else self.images_idle_left
            

    def get_attack_hitbox(self):
        """
        Retorna um pygame.Rect representando a área de alcance do ataque,
        considerando que (x, y) é o centro do personagem.
        """
        hitbox_width = 30   # Largura da área de ataque
        hitbox_height = self.altura  # Usa a altura definida em Entity
        if self.facing_right:
            hitbox_x = self.x + self.largura / 2
        else:
            hitbox_x = self.x - self.largura / 2 - hitbox_width
        hitbox_y = self.y - self.altura / 2
        return Rect(hitbox_x, hitbox_y, hitbox_width, hitbox_height)

    def attack_hit_active(self):
        """
        Retorna True se o frame atual do ataque estiver ativo para aplicar dano.
        Exemplo: frames 2 a 4 da animação de ataque.
        """
        return 2 <= self.current_image <= 4

    def check_attack_hit(self):
        """
        Verifica se o hitbox do ataque colide com algum inimigo. Se sim,
        e o inimigo ainda não foi atingido neste ataque, aplica dano.
        """
        hitbox = self.get_attack_hitbox()
        for enemy in self.enemies:
            enemy_rect = Rect(
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
        """
        Verifica e resolve colisões entre o personagem e as plataformas.
        Em caso de colisão, calcula a interseção (overlap) nos eixos X e Y
        e reposiciona o personagem na direção de menor penetração.
        
        É importante que o método get_rect() do personagem retorne o retângulo
        considerando que self.actor.x e self.actor.y são as coordenadas centrais.
        """
        # Obtém o retângulo atual do personagem
        char_rect = self.get_rect()  # definido como: Rect(x - largura/2, y - altura/2, largura, altura)
        
        # Para cada plataforma, verifica colisão
        for plataforma in self.plataformas:
            # Recupera os offsets da plataforma, se existirem
            offset_x = getattr(plataforma, "offset_x", 0)
            offset_y = getattr(plataforma, "offset_y", 0)
            
            # Define o retângulo da plataforma (a plataforma foi desenhada usando a
            # posição x e y com esses offsets, portanto, eles também afetam a colisão)
            plat_rect = Rect(
                plataforma.x + offset_x,
                plataforma.y + offset_y,
                plataforma.largura,
                plataforma.altura
            )
            
            # Se houver colisão entre o retângulo do personagem e o da plataforma...
            if char_rect.colliderect(plat_rect):
                # Calcula os valores de interseção (overlap) em cada direção
                overlap_esquerda  = char_rect.right - plat_rect.left
                overlap_direita   = plat_rect.right - char_rect.left
                overlap_cima      = char_rect.bottom - plat_rect.top
                overlap_baixo     = plat_rect.bottom - char_rect.top
                
                # Escolhe o menor overlap – esse será o eixo de resolução (o menor empurrão necessário)
                min_overlap = min(overlap_esquerda, overlap_direita, overlap_cima, overlap_baixo)
                
                if min_overlap == overlap_cima:
                    # Colisão vindo de cima: o personagem está caindo sobre a plataforma
                    # Reposiciona-o para que sua base fique exatamente sobre a plataforma
                    self.actor.y -= overlap_cima
                    self.vel_y = 0
                    self.no_chao = True
                elif min_overlap == overlap_baixo:
                    # Colisão vindo de baixo: o personagem está pulando e bateu a cabeça na plataforma
                    self.actor.y += overlap_baixo
                    self.vel_y = 0
                elif min_overlap == overlap_esquerda:
                    # Colisão lateral: vindo da esquerda
                    self.actor.x -= overlap_esquerda
                elif min_overlap == overlap_direita:
                    # Colisão lateral: vindo da direita
                    self.actor.x += overlap_direita
                
                # Atualiza o retângulo do personagem após a correção
                char_rect = self.get_rect()


    def get_rect(self):
        return Rect(
            self.x - self.largura / 2,
            self.y - self.altura / 2,
            self.largura,
            self.altura)
