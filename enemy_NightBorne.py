import pygame
from enemy import Inimigo
from pgzero.builtins import sounds
from audio import play_sound
from enemy import VELOCIDADE_CORRIDA, GRAVIDADE, VELOCIDADE_QUEDA_MAX


class Enemy_NightBorne(Inimigo):
    def __init__(self, posicao_inicial_x, posicao_inicial_y, plataformas, x_inicial, x_final):
        super().__init__(
            imagens_idle_right=[
                'enemy1_idle_0', 'enemy1_idle_1', 'enemy1_idle_2', 'enemy1_idle_3',
                'enemy1_idle_4', 'enemy1_idle_5', 'enemy1_idle_6', 'enemy1_idle_7', 'enemy1_idle_8'
            ],
            imagens_idle_left=[
                'enemy1_idle_0_left', 'enemy1_idle_1_left', 'enemy1_idle_2_left', 'enemy1_idle_3_left',
                'enemy1_idle_4_left', 'enemy1_idle_5_left', 'enemy1_idle_6_left', 'enemy1_idle_7_left', 'enemy1_idle_8_left'
            ],
            imagens_attack_right=[
                'enemy1_attack_0', 'enemy1_attack_1', 'enemy1_attack_3', 'enemy1_attack_4',
                'enemy1_attack_5', 'enemy1_attack_6', 'enemy1_attack_7', 'enemy1_attack_8',
                'enemy1_attack_9', 'enemy1_attack_10', 'enemy1_attack_11', 'enemy1_attack_12'
            ],
            imagens_attack_left=[
                'enemy1_attack_0_left', 'enemy1_attack_1_left', 'enemy1_attack_3_left', 'enemy1_attack_4_left',
                'enemy1_attack_5_left', 'enemy1_attack_6_left', 'enemy1_attack_7_left', 'enemy1_attack_8_left',
                'enemy1_attack_9_left', 'enemy1_attack_10_left', 'enemy1_attack_11_left', 'enemy1_attack_12_left'
            ],
            imagens_dano_right=[
                'enemy1_hurt_0', 'enemy1_hurt_1', 'enemy1_hurt_2', 'enemy1_hurt_3', 'enemy1_hurt_4'
            ],
            imagens_dano_left=[
                'enemy1_hurt_0_left', 'enemy1_hurt_1_left', 'enemy1_hurt_2_left', 'enemy1_hurt_3_left', 'enemy1_hurt_4_left'
            ],
            imagens_run_right=[
                'enemy1_run_0', 'enemy1_run_1', 'enemy1_run_2', 'enemy1_run_3', 'enemy1_run_4', 'enemy1_run_5'
            ],
            imagens_run_left=[
                'enemy1_run_0_left', 'enemy1_run_1_left', 'enemy1_run_2_left', 'enemy1_run_3_left', 'enemy1_run_4_left', 'enemy1_run_5_left'
            ],
            imagens_death_left=[
                'enemy1_death_0_left', 'enemy1_death_1_left', 'enemy1_death_2_left',
                'enemy1_death_3_left', 'enemy1_death_4_left', 'enemy1_death_5_left',
                'enemy1_death_6_left', 'enemy1_death_7_left', 'enemy1_death_8_left',
                'enemy1_death_9', 'enemy1_death_10', 'enemy1_death_11', 'enemy1_death_12',
                'enemy1_death_13', 'enemy1_death_14', 'enemy1_death_15', 'enemy1_death_16',
                'enemy1_death_17', 'enemy1_death_18', 'enemy1_death_19', 'enemy1_death_20',
                'enemy1_death_21', 'enemy1_death_22'
            ],
            imagens_death_right=[
                'enemy1_death_0', 'enemy1_death_1', 'enemy1_death_2', 'enemy1_death_3',
                'enemy1_death_4', 'enemy1_death_5', 'enemy1_death_6', 'enemy1_death_7',
                'enemy1_death_8', 'enemy1_death_9', 'enemy1_death_10', 'enemy1_death_11',
                'enemy1_death_12', 'enemy1_death_13', 'enemy1_death_14', 'enemy1_death_15',
                'enemy1_death_16', 'enemy1_death_17', 'enemy1_death_18', 'enemy1_death_19',
                'enemy1_death_20', 'enemy1_death_21', 'enemy1_death_22'
            ],
            vida=100,
            dano=40,
            posicao_inicial_x=posicao_inicial_x,
            posicao_inicial_y=posicao_inicial_y,
            plataformas=plataformas,
            x_inicial=x_inicial,
            x_final=x_final
        )
        # Sons específicos para o NightBorne:
        self.sound_attack = sounds.enemy_attack
        self.sound_run = sounds.enemy_walk
        self.sound_damage = sounds.enemy_damage
        self.sound_death = sounds.enemy_death
        self.attack_range = 50  # Distância máxima para ataque

        # Flag para garantir que o som de ataque seja tocado apenas uma vez por ciclo de ataque
        self.attack_sound_played = False

        
        self.attack_range_y = 50  # Ajuste esse valor conforme necessário


    def attack_hit_active(self):
        """
        Retorna True somente se o frame atual estiver entre 10 e 12,
        definindo assim o momento “ativo” para causar dano.
        """
        return 10 <= self.current_image <= 12

    def update(self):
        """
        Sobrescrevemos o update para ajustar o momento do som e do golpe.
        A maior parte da lógica é igual à classe base, com alterações na parte de ataque.
        """
        # Se estiver morrendo, apenas atualiza a animação de morte.
        if self.is_dying:
            self.update_image(
                self.images_death_right if self.facing_right else self.images_death_left, finish_on_end=True)
            return

        # Se estiver tomando dano, atualiza a animação de dano.
        if self.is_taking_damage:
            dano_list = self.images_dano_right if self.facing_right else self.images_dano_left
            self.update_image(dano_list, finish_on_end=True)
            if self.current_image == len(dano_list) - 1:
                self.is_taking_damage = False
                self.current_image = 0
                self.current_images_list = self.images_idle_right if self.facing_right else self.images_idle_left
            return

        # Verifica se há um alvo para iniciar o ataque.
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
            self.update_image()  # Atualiza o frame da animação de ataque

            # Se chegarmos ao frame 10 (por exemplo) e o som ainda não foi tocado, toca-o.
            if self.current_image == 10 and not self.attack_sound_played:
                if self.sound_attack:
                    play_sound(self.sound_attack)
                self.attack_sound_played = True

            # Verifica se é o momento de aplicar o dano.
            if self.attack_hit_active():
                self.check_attack_hit()

            # Opcional: quando a animação de ataque chegar ao final, reseta para o estado idle.
            if self.current_image == len(self.current_images_list) - 1:
                self.is_attacking = False
                self.current_image = 0
                self.current_images_list = self.images_idle_right if self.facing_right else self.images_idle_left

            return  # Interrompe o restante do update enquanto estiver atacando

        # Se não estiver atacando, segue com o patrulhamento (movimentação) e gravidade:
        if self.is_moving:
            # Toca o som de corrida periodicamente (para não repetir a cada frame)
            if self.run_sound_timer <= 0:
                if self.sound_run:
                    play_sound(self.sound_run)
                self.run_sound_timer = 30  # tempo em frames para repetir o som
            else:
                self.run_sound_timer -= 1

            if self.facing_right:
                self.actor.x += VELOCIDADE_CORRIDA
                self.current_images_list = self.images_run_right
            else:
                self.actor.x -= VELOCIDADE_CORRIDA
                self.current_images_list = self.images_run_left

            # Inverte a direção ao bater nos limites da tela.
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

        # Sincroniza a posição da entidade com a do actor.
        self.x = self.actor.x
        self.y = self.actor.y

        # Verifica colisões com as plataformas.
        self.verificar_colisoes()

        # Atualiza a animação do estado normal (idle ou patrulhamento).
        self.update_image()
