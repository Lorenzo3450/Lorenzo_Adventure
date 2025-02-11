from pgzero.actor import Actor    
from pgzero.keyboard import keyboard
from pgzero.builtins import sounds
from entity import Entity, GRAVIDADE, PULO_FORCA, ANIMACAO_DELAY
from audio import play_sound
from pygame import Rect

class Personagem(Entity):
    def __init__(self, plataformas, life_bar, x_inicial=100, y_inicial=750):
        super().__init__(x_inicial, y_inicial, 25, 35)
        self.actor = Actor('heroknight_idle_0')
        self.actor.pos = (x_inicial, y_inicial)
        self.life_bar = life_bar

        # --- Animações ---
        # Idle
        self.images_idle_right = [f'heroknight_idle_{i}' for i in range(8)]
        self.images_idle_left  = [f'heroknight_idle_{i}_left' for i in range(8)]
        # Correndo
        self.images_run_right = [f'heroknight_run_{i}' for i in [0, 2, 3, 4, 5, 6, 7, 8, 9]]
        self.images_run_left  = [f'heroknight_run_{i}_left' for i in [0, 2, 3, 4, 5, 6, 7, 8, 9]]
        # Pulando
        self.images_jump_right = [f'heroknight_jump_{i}' for i in range(3)]
        self.images_jump_left  = [f'heroknight_jump_{i}_left' for i in range(3)]
        # Caindo
        self.images_fall_right = [f'heroknight_fall_{i}' for i in range(4)]
        self.images_fall_left  = [f'heroknight_fall_{i}_left' for i in range(4)]
        # Atacando
        self.images_attack_right = [f'heroknight_attack1_{i}' for i in range(6)]
        self.images_attack_left  = [f'heroknight_attack1_{i}_left' for i in range(6)]
        # Tomando dano (hurt)
        self.images_hurt_right = [f'heroknight_hurt_{i}' for i in range(3)]
        self.images_hurt_left  = [f'heroknight_hurt_{i}_left' for i in range(3)]
        # Bloqueando (escudo levantado)
        self.images_block_idle_right = [f'heroknight_block_idle_{i}' for i in range(8)]
        self.images_block_idle_left  = [f'heroknight_block_idle_{i}_left' for i in range(8)]
        # Bloqueio de ataque (ao absorver um impacto)
        self.images_block_attack_right = [f'heroknight_block_{i}' for i in range(5)]
        self.images_block_attack_left  = [f'heroknight_block_{i}_left' for i in range(5)]
        # Morte
        self.images_death_right = [f'heroknight_death_{i}' for i in range(10)]
        self.images_death_left  = [f'heroknight_death_{i}_left' for i in range(10)]

        # --- Estado e controle de animação ---
        self.current_image = 0
        self.current_images_list = self.images_idle_right  # Estado inicial
        self.is_moving = False
        self.facing_right = True
        self.is_attacking = False
        self.is_blocking = False
        self.is_dead = False
        self.is_hurt = False
        self.is_blocking_attack = False

        # Vida e invulnerabilidade
        self.health = 100
        self.invulnerable_timer = 0

        # Física (pulo e gravidade)
        self.vel_y = 0
        self.no_chao = True  # Indica se está no chão

        # Controle da animação
        self.frame_count = 0

        # Plataformas
        self.plataformas = plataformas

        # Lógica de ataque
        self.attack_damage = 20
        self.hit_enemies = []
        self.enemies = []  # Será definida externamente

        # Timer para passos
        self.footstep_timer = 0

    def update(self):
        """Atualiza o estado e a animação do personagem a cada frame."""
        # Estado de Morte
        if self.is_dead:
            self.update_image_death()
            return

        # Atualiza timer de invulnerabilidade
        if self.invulnerable_timer > 0:
            self.invulnerable_timer -= 1

        # Estado de Dano (hurt)
        if self.is_hurt:
            self.update_image_hurt()
            return

        # Bloqueio de ataque tem prioridade
        if self.is_blocking_attack:
            self.update_image_block_attack()
            return

        # Bloqueio (escudo levantado)
        if self.is_blocking:
            self.current_images_list = self.images_block_idle_right if self.facing_right else self.images_block_idle_left
            self.update_image_block()
            return

        # Ataque
        if self.is_attacking:
            self.update_image()
            if self.attack_hit_active():
                self.check_attack_hit()
            return

        # --- Processamento de Movimento ---
        dx = 0
        if keyboard.A:
            dx = -5
            self.facing_right = False
            self.current_images_list = self.images_run_left
            self.is_moving = True
        elif keyboard.D:
            dx = 5
            self.facing_right = True
            self.current_images_list = self.images_run_right
            self.is_moving = True
        else:
            self.is_moving = False

        self.actor.x += dx
        self.actor.x = max(0, min(self.actor.x, 1200))  # Limita na tela

        # Sons de passos
        if self.is_moving:
            self.footstep_timer -= 1
            if self.footstep_timer <= 0:
                play_sound(sounds.human_walk)
                self.footstep_timer = 20
        else:
            self.footstep_timer = 0

        # Pulo (apenas se estiver no chão)
        if keyboard.W and self.no_chao:
            self.vel_y = PULO_FORCA
            self.no_chao = False
            play_sound(sounds.human_jump)

        # Aplicação da gravidade
        self.vel_y += GRAVIDADE
        self.actor.y += self.vel_y

        # Sincroniza as coordenadas da entidade com o ator
        self.x = self.actor.x
        self.y = self.actor.y

        # Verifica colisões com plataformas
        self.verificar_colisoes()

        # Define a animação conforme o estado vertical
        if not self.no_chao:
            if self.vel_y < 0:
                self.current_images_list = self.images_jump_right if self.facing_right else self.images_jump_left
            else:
                self.current_images_list = self.images_fall_right if self.facing_right else self.images_fall_left
        elif not self.is_moving:
            self.current_images_list = self.images_idle_right if self.facing_right else self.images_idle_left

        self.update_image()

    def update_image(self):
        """Atualiza a animação padrão (movimento e ataque)."""
        self.frame_count += 1
        if self.frame_count >= ANIMACAO_DELAY:
            self.current_image += 1
            if self.is_attacking:
                # Finaliza o ataque quando a animação acaba
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
        """Atualiza a animação de bloqueio (em loop)."""
        self.frame_count += 1
        if self.frame_count >= ANIMACAO_DELAY:
            self.current_image = (self.current_image + 1) % len(self.current_images_list)
            self.actor.image = self.current_images_list[self.current_image]
            self.frame_count = 0

    def update_image_block_attack(self):
        """
        Atualiza a animação de bloqueio de ataque (não em loop). 
        Ao final, retorna ao estado de bloqueio ou ao idle.
        """
        self.frame_count += 1
        if self.frame_count >= ANIMACAO_DELAY:
            self.current_image += 1
            if self.current_image >= len(self.current_images_list):
                self.is_blocking_attack = False
                self.current_image = 0
                # Se o bloqueio ainda estiver ativo, mantém-o; senão, volta ao idle.
                self.current_images_list = (self.images_block_idle_right if self.facing_right else self.images_block_idle_left) \
                    if self.is_blocking else (self.images_idle_right if self.facing_right else self.images_idle_left)
                self.actor.image = self.current_images_list[self.current_image]
            else:
                self.actor.image = self.current_images_list[self.current_image]
            self.frame_count = 0

    def update_image_death(self):
        """
        Atualiza a animação de morte. Ao final, mantém a última frame.
        """
        self.frame_count += 1
        if self.frame_count >= ANIMACAO_DELAY:
            if self.current_image < len(self.current_images_list) - 1:
                self.current_image += 1
                self.actor.image = self.current_images_list[self.current_image]
            self.frame_count = 0

    def take_damage(self, damage):
        """
        Aplica dano ao personagem, considerando bloqueio e invulnerabilidade.
        Se a vida chegar a 0, inicia a animação de morte.
        """
        if self.is_dead:
            return

        # Se estiver bloqueando, ativa a animação de bloqueio de ataque e não recebe dano
        if self.is_blocking:
            if not self.is_blocking_attack:
                self.is_blocking_attack = True
                self.current_image = 0
                self.current_images_list = self.images_block_attack_right if self.facing_right else self.images_block_attack_left
                play_sound(sounds.escudo_impact)
            return

        if self.invulnerable_timer > 0:
            return

        self.health -= damage
        if damage > 0 and self.life_bar is not None:
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
        """Processa os comandos de ataque e bloqueio ao pressionar o mouse."""
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
        """Encerra o bloqueio ao soltar o botão direito."""
        if not self.no_chao:
            return

        if button == "right":
            self.is_blocking = False
            self.current_image = 0
            self.current_images_list = self.images_idle_right if self.facing_right else self.images_idle_left

    def get_attack_hitbox(self):
        """
        Retorna um Rect representando a área do ataque, 
        considerando (self.x, self.y) como centro do personagem.
        """
        hitbox_width = 30
        hitbox_height = self.altura
        if self.facing_right:
            hitbox_x = self.x + self.largura / 2
        else:
            hitbox_x = self.x - self.largura / 2 - hitbox_width
        hitbox_y = self.y - self.altura / 2
        return Rect(hitbox_x, hitbox_y, hitbox_width, hitbox_height)

    def attack_hit_active(self):
        """Retorna True se o frame atual do ataque estiver ativo para causar dano."""
        return 2 <= self.current_image <= 4

    def check_attack_hit(self):
        """
        Verifica se o hitbox do ataque colide com algum inimigo.
        Se colidir e o inimigo ainda não tiver sido atingido neste ataque, aplica dano.
        """
        hitbox = self.get_attack_hitbox()
        for enemy in self.enemies:
            enemy_rect = Rect(
                enemy.x - enemy.largura / 2,
                enemy.y - enemy.altura / 2,
                enemy.largura,
                enemy.altura
            )
            if hitbox.colliderect(enemy_rect) and enemy not in self.hit_enemies:
                enemy.take_damage(self.attack_damage)
                self.hit_enemies.append(enemy)

    def draw(self):
        self.actor.draw()

    def verificar_colisoes(self):
        """
        Verifica e resolve colisões entre o personagem e as plataformas.
        Calcula o overlap em cada eixo e reposiciona o personagem na direção de menor penetração.
        """
        char_rect = self.get_rect()
        for plataforma in self.plataformas:
            offset_x = getattr(plataforma, "offset_x", 0)
            offset_y = getattr(plataforma, "offset_y", 0)
            plat_rect = Rect(
                plataforma.x + offset_x,
                plataforma.y + offset_y,
                plataforma.largura,
                plataforma.altura
            )
            if char_rect.colliderect(plat_rect):
                overlap_left   = char_rect.right - plat_rect.left
                overlap_right  = plat_rect.right - char_rect.left
                overlap_top    = char_rect.bottom - plat_rect.top
                overlap_bottom = plat_rect.bottom - char_rect.top

                min_overlap = min(overlap_left, overlap_right, overlap_top, overlap_bottom)
                if min_overlap == overlap_top:
                    # Colisão por baixo da plataforma (personagem caindo)
                    self.actor.y -= overlap_top
                    self.vel_y = 0
                    self.no_chao = True
                elif min_overlap == overlap_bottom:
                    # Colisão por cima (bater a cabeça)
                    self.actor.y += overlap_bottom
                    self.vel_y = 0
                elif min_overlap == overlap_left:
                    self.actor.x -= overlap_left
                elif min_overlap == overlap_right:
                    self.actor.x += overlap_right

                # Atualiza o retângulo após a correção
                char_rect = self.get_rect()

    def get_rect(self):
        """Retorna o Rect representando a área do personagem."""
        return Rect(
            self.x - self.largura / 2,
            self.y - self.altura / 2,
            self.largura,
            self.altura
        )
