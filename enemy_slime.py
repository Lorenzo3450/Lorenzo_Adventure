from enemy import Inimigo, VELOCIDADE_CORRIDA, GRAVIDADE, VELOCIDADE_QUEDA_MAX
from pgzero.builtins import sounds
from audio import play_sound


class Enemy_Slime(Inimigo):
    def __init__(self, posicao_inicial_x, posicao_inicial_y, plataformas, x_inicial, x_final):
        """
        Inicializa um inimigo do tipo Slime.

        Parâmetros:
          - posicao_inicial_x, posicao_inicial_y: posição inicial do slime.
          - plataformas: lista de plataformas para verificação de colisões.
          - x_inicial, x_final: limites horizontais da patrulha.
        """
        super().__init__(
            # Imagens de idle (frames 0 a 3)
            imagens_idle_left=[
                'slime-idle-0', 'slime-idle-1', 'slime-idle-2', 'slime-idle-3'
            ],
            imagens_idle_right=[
                'slime-idle-0_right', 'slime-idle-1_right', 'slime-idle-2_right', 'slime-idle-3_right'
            ],
            # Imagens de ataque (frames 0 a 4)
            imagens_attack_left=[
                'slime-attack-0', 'slime-attack-1', 'slime-attack-2', 'slime-attack-3', 'slime-attack-4'
            ],
            imagens_attack_right=[
                'slime-attack-0_right', 'slime-attack-1_right', 'slime-attack-2_right', 'slime-attack-3_right', 'slime-attack-4_right'
            ],
            # Imagens de dano/hurt (frames 0 a 3)
            imagens_dano_left=[
                'slime-hurt-0', 'slime-hurt-1', 'slime-hurt-2', 'slime-hurt-3'
            ],
            imagens_dano_right=[
                'slime-hurt-0_right', 'slime-hurt-1_right', 'slime-hurt-2_right', 'slime-hurt-3_right'
            ],
            # Imagens de movimento (move) – para patrulha (frames 0 a 3)
            imagens_run_left=[
                'slime-move-0', 'slime-move-1', 'slime-move-2', 'slime-move-3'
            ],
            imagens_run_right=[
                'slime-move-0_right', 'slime-move-1_right', 'slime-move-2_right', 'slime-move-3_right'
            ],
            # Imagens de morte (die) (frames 0 a 3)
            imagens_death_left=[
                'slime-die-0', 'slime-die-1', 'slime-die-2', 'slime-die-3'
            ],
            imagens_death_right=[
                'slime-die-0_right', 'slime-die-1_right', 'slime-die-2_right', 'slime-die-3_right'
            ],
            # Outros parâmetros
            vida=60,
            dano=20,
            posicao_inicial_x=posicao_inicial_x,
            posicao_inicial_y=posicao_inicial_y,
            plataformas=plataformas,
            x_inicial=x_inicial,
            x_final=x_final
        )

        # Configura os sons específicos para o Slime (se estiverem definidos no objeto sounds)
        self.sound_attack = sounds.slime_attack
        self.sound_run = sounds.enemy_walk
        self.sound_damage = sounds.slime_hurt
        self.sound_death = sounds.slime_die

        # Ajusta o alcance de ataque (em pixels)
        self.attack_range = 40

        # Flag para garantir que o som de ataque seja tocado apenas uma vez por ciclo de ataque
        self.attack_sound_played = False

        # Delay específico para a animação de ataque (quanto maior, mais lento o avanço dos frames)
        self.attack_anim_delay = 10

    def attack_hit_active(self):
        """
        Retorna True se o frame atual do ataque for o momento ativo para causar dano.
        Para o Slime, usamos o frame 2 (dos 5 da animação) como instante ativo.
        """
        return self.current_image == 2

    def update_attack_image(self, finish_on_end=False):
        """
        Atualiza a imagem do ataque utilizando um delay customizado para
        deixar a animação de ataque mais lenta.
        """
        images_list = self.current_images_list
        self.frame_count += 1
        if self.frame_count >= self.attack_anim_delay:
            self.current_image += 1
            if finish_on_end and self.current_image >= len(images_list):
                self.current_image = len(images_list) - 1
            else:
                self.current_image %= len(images_list)
            self.actor.image = images_list[self.current_image]
            self.frame_count = 0

    def update(self):
        # Se o inimigo está morrendo, atualiza a animação de morte e interrompe outras ações.
        if self.is_dying:
            self.update_image(
                self.images_death_right if self.facing_right else self.images_death_left,
                finish_on_end=True
            )
            return

        # Se o inimigo está tomando dano, atualiza a animação de dano.
        if self.is_taking_damage:
            dano_list = self.images_dano_right if self.facing_right else self.images_dano_left
            self.update_image(dano_list, finish_on_end=True)
            if self.current_image == len(dano_list) - 1:
                self.is_taking_damage = False
                self.current_image = 0
                self.current_images_list = (
                    self.images_idle_right if self.facing_right else self.images_idle_left
                )
            return

        # Verifica se há um alvo (por exemplo, o jogador) para iniciar o ataque.
        if self.alvo is not None:
            distancia_x = abs(self.alvo.x - self.x)
            distancia_y = abs(self.alvo.y - self.y)
            if distancia_x < self.attack_range and distancia_y < self.attack_range_y:
                # Ajusta a direção para encarar o alvo.
                self.facing_right = self.alvo.x > self.x
                if not self.is_attacking:
                    self.is_attacking = True
                    self.current_image = 0
                    self.current_images_list = self.images_attack_right if self.facing_right else self.images_attack_left
                    self.hit_player = False
                    self.attack_sound_played = False  # Reseta a flag no início do ataque
                self.is_moving = False
            else:
                if self.is_attacking:
                    self.is_attacking = False
                    self.current_image = 0
                    self.current_images_list = self.images_idle_right if self.facing_right else self.images_idle_left
                self.is_moving = True


        # Se estiver no estado de ataque:
        if self.is_attacking:
            # Usa o método customizado para atualizar a animação de ataque com delay aumentado.
            self.update_attack_image()

            # Toca o som de ataque no momento adequado (frame 2, por exemplo)
            if self.current_image == 2 and not self.attack_sound_played:
                if self.sound_attack:
                    play_sound(self.sound_attack)
                self.attack_sound_played = True

            # Aplica dano se estiver no momento ativo do ataque.
            if self.attack_hit_active():
                self.check_attack_hit()

            # Ao final da animação de ataque, retorna ao estado idle.
            if self.current_image == len(self.current_images_list) - 1:
                self.is_attacking = False
                self.current_image = 0
                self.current_images_list = (
                    self.images_idle_right if self.facing_right else self.images_idle_left
                )
            return  # Interrompe o restante do update enquanto o ataque está em andamento

        # Se estiver patrulhando/movendo:
        if self.is_moving:
            # Toca o som de movimento periodicamente.
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

            # Inverte a direção ao atingir os limites da patrulha.
            if self.actor.x >= self.x_final:
                self.actor.x = self.x_final
                self.facing_right = False
            elif self.actor.x <= self.x_inicial:
                self.actor.x = self.x_inicial
                self.facing_right = True

        # Aplica a gravidade.
        self.velocidade_y += GRAVIDADE
        if self.velocidade_y > VELOCIDADE_QUEDA_MAX:
            self.velocidade_y = VELOCIDADE_QUEDA_MAX
        self.actor.y += self.velocidade_y

        # Sincroniza a posição interna com a do actor.
        self.x = self.actor.x
        self.y = self.actor.y

        # Verifica colisões com as plataformas.
        self.verificar_colisoes()

        # Atualiza a animação do estado normal (idle ou movimento).
        self.update_image()

    def draw(self):
        """
        Desenha o slime aplicando um offset vertical para que ele seja
        renderizado mais próximo do chão.
        """
        offset_y = 5  # Ajuste este valor conforme necessário
        self.actor.y += offset_y
        self.actor.draw()
        self.actor.y -= offset_y
