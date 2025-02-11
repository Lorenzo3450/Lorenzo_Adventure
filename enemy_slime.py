from enemy import Inimigo, VELOCIDADE_CORRIDA, GRAVIDADE, VELOCIDADE_QUEDA_MAX 
from pgzero.builtins import sounds
from audio import play_sound

class Enemy_Slime(Inimigo):
    def __init__(self, posicao_inicial_x, posicao_inicial_y, plataformas, x_inicial, x_final):
        """
        Inicializa um inimigo do tipo Slime.
        """
        super().__init__(
            # Imagens de idle
            imagens_idle_left=[f'slime-idle-{i}' for i in range(4)],
            imagens_idle_right=[f'slime-idle-{i}_right' for i in range(4)],
            # Imagens de ataque
            imagens_attack_left=[f'slime-attack-{i}' for i in range(5)],
            imagens_attack_right=[f'slime-attack-{i}_right' for i in range(5)],
            # Imagens de dano (hurt)
            imagens_dano_left=[f'slime-hurt-{i}' for i in range(4)],
            imagens_dano_right=[f'slime-hurt-{i}_right' for i in range(4)],
            # Imagens de movimentação (run)
            imagens_run_left=[f'slime-move-{i}' for i in range(4)],
            imagens_run_right=[f'slime-move-{i}_right' for i in range(4)],
            # Imagens de morte (die)
            imagens_death_left=[f'slime-die-{i}' for i in range(4)],
            imagens_death_right=[f'slime-die-{i}_right' for i in range(4)],
            vida=60,
            dano=20,
            posicao_inicial_x=posicao_inicial_x,
            posicao_inicial_y=posicao_inicial_y,
            plataformas=plataformas,
            x_inicial=x_inicial,
            x_final=x_final
        )

        # Configuração dos sons
        self.sound_attack = sounds.slime_attack
        self.sound_run    = sounds.enemy_walk
        self.sound_damage = sounds.slime_hurt
        self.sound_death  = sounds.slime_die

        # Alcance para detectar o alvo
        self.attack_range   = 40  # alcance horizontal para ataque
        self.attack_range_y = 40  # alcance vertical para ataque

        # Flags para controlar os sons e estados de ataque
        self.attack_sound_played = False
        self.run_sound_timer     = 0

        # --- Novas variáveis para controle do ataque ---
        # Cooldown para que o slime espere antes de iniciar um novo ataque
        self.attack_cooldown_timer = 0  # contador de frames de cooldown
        self.attack_cooldown_interval = 60  # intervalo entre ataques (ex.: 60 frames = 1 segundo)

        # Delay entre os frames da animação de ataque para desacelerá-la
        self.attack_frame_delay = 5  # quantidade de frames a esperar antes de trocar para o próximo frame
        self.attack_frame_counter = 0

    def attack_hit_active(self):
        """
        Retorna True se o frame atual da animação de ataque for o instante ativo para causar dano.
        Para o Slime, consideramos o frame 2 como o instante de impacto.
        """
        return self.current_image == 2

    def update(self):
        """
        Atualiza o estado e a animação do Slime a cada frame.
        """
        # Reduz o cooldown de ataque, se ativo
        if self.attack_cooldown_timer > 0:
            self.attack_cooldown_timer -= 1

        # 1. Estado de Morte
        if self.is_dying:
            death_images = self.images_death_right if self.facing_right else self.images_death_left
            self.update_image(death_images, finish_on_end=True)
            return

        # 2. Estado de Tomando Dano
        if self.is_taking_damage:
            dano_list = self.images_dano_right if self.facing_right else self.images_dano_left
            self.update_image(dano_list, finish_on_end=True)
            if self.current_image == len(dano_list) - 1:
                self.is_taking_damage = False
                self.current_image = 0
                self.current_images_list = self.images_idle_right if self.facing_right else self.images_idle_left
            return

        # 3. Verifica se há um alvo para iniciar o ataque
        if self.alvo is not None:
            dx = abs(self.alvo.x - self.x)
            dy = abs(self.alvo.y - self.y)
            if dx < self.attack_range and dy < self.attack_range_y:
                # Ajusta a direção para encarar o alvo
                self.facing_right = self.alvo.x > self.x
                # Só inicia ataque se o cooldown estiver zerado
                if self.attack_cooldown_timer == 0:
                    if not self.is_attacking:
                        self.is_attacking = True
                        self.current_image = 0
                        self.current_images_list = self.images_attack_right if self.facing_right else self.images_attack_left
                        self.hit_player = False
                        self.attack_sound_played = False  # Reseta a flag de som de ataque
                        self.attack_frame_counter = 0  # Reseta o contador de delay na animação de ataque
                    self.is_moving = False
                else:
                    # Se ainda estiver no intervalo entre ataques, não ataca e continua patrulhando
                    self.is_attacking = False
                    self.current_image = 0
                    self.current_images_list = self.images_idle_right if self.facing_right else self.images_idle_left
                    self.is_moving = True
            else:
                if self.is_attacking:
                    # Se o alvo se afastar durante o ataque, encerra o ataque
                    self.is_attacking = False
                    self.current_image = 0
                    self.current_images_list = self.images_idle_right if self.facing_right else self.images_idle_left
                self.is_moving = True

        # 4. Estado de Ataque
        if self.is_attacking:
            # Aplica o delay para que cada frame da animação de ataque demore mais
            self.attack_frame_counter += 1
            if self.attack_frame_counter >= self.attack_frame_delay:
                self.attack_frame_counter = 0
                self.update_image()  # Atualiza para o próximo frame da animação de ataque

                # Toca o som de ataque no frame de impacto (frame 2)
                if self.current_image == 2 and not self.attack_sound_played:
                    if self.sound_attack:
                        play_sound(self.sound_attack)
                    self.attack_sound_played = True

                # Verifica se é o momento de aplicar dano
                if self.attack_hit_active():
                    self.check_attack_hit()

                # Ao terminar a animação de ataque, retorna ao estado idle e inicia o cooldown
                if self.current_image == len(self.current_images_list) - 1:
                    self.is_attacking = False
                    self.current_image = 0
                    self.current_images_list = self.images_idle_right if self.facing_right else self.images_idle_left
                    self.attack_cooldown_timer = self.attack_cooldown_interval
            return

        # 5. Estado de Patrulhamento/Movimentação
        if self.is_moving:
            if self.run_sound_timer <= 0:
                if self.sound_run:
                    play_sound(self.sound_run)
                self.run_sound_timer = 30
            else:
                self.run_sound_timer -= 1

            if self.facing_right:
                self.actor.x += VELOCIDADE_CORRIDA
                self.current_images_list = self.images_run_right
            else:
                self.actor.x -= VELOCIDADE_CORRIDA
                self.current_images_list = self.images_run_left

            # Inverte a direção ao bater nos limites da patrulha
            if self.actor.x >= self.x_final:
                self.actor.x = self.x_final
                self.facing_right = False
            elif self.actor.x <= self.x_inicial:
                self.actor.x = self.x_inicial
                self.facing_right = True

        # 6. Aplica a gravidade
        self.velocidade_y += GRAVIDADE
        if self.velocidade_y > VELOCIDADE_QUEDA_MAX:
            self.velocidade_y = VELOCIDADE_QUEDA_MAX
        self.actor.y += self.velocidade_y

        # Sincroniza a posição interna com a do actor
        self.x = self.actor.x
        self.y = self.actor.y

        # Verifica colisões com as plataformas
        self.verificar_colisoes()

        # Atualiza a animação no estado normal (idle ou run)
        self.update_image()

    def draw(self):
        """
        Desenha o Slime aplicando um offset vertical para que ele seja renderizado
        mais próximo do chão.
        """
        offset_y = 5  # Ajuste conforme necessário
        self.actor.y += offset_y
        self.actor.draw()
        self.actor.y -= offset_y
