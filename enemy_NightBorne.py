import pygame 
from enemy import Inimigo
from pgzero.builtins import sounds
from audio import play_sound
from enemy import VELOCIDADE_CORRIDA, GRAVIDADE, VELOCIDADE_QUEDA_MAX

class Enemy_NightBorne(Inimigo):
    def __init__(self, posicao_inicial_x, posicao_inicial_y, plataformas, x_inicial, x_final):
        super().__init__(
            # Idle
            imagens_idle_right=[f'enemy1_idle_{i}' for i in range(9)],
            imagens_idle_left=[f'enemy1_idle_{i}_left' for i in range(9)],
            # Ataque
            imagens_attack_right=[f'enemy1_attack_{i}' for i in [0, 1, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]],
            imagens_attack_left=[f'enemy1_attack_{i}_left' for i in [0, 1, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]],
            # Dano
            imagens_dano_right=[f'enemy1_hurt_{i}' for i in range(5)],
            imagens_dano_left=[f'enemy1_hurt_{i}_left' for i in range(5)],
            # Corrida
            imagens_run_right=[f'enemy1_run_{i}' for i in range(6)],
            imagens_run_left=[f'enemy1_run_{i}_left' for i in range(6)],
            # Morte
            imagens_death_right=[f'enemy1_death_{i}' for i in range(23)],
            imagens_death_left=[f'enemy1_death_{i}_left' if i < 9 else f'enemy1_death_{i}' for i in range(23)],
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
        self.sound_death  = sounds.enemy_death

        self.attack_range   = 50   # Distância máxima para ataque (eixo x)
        self.attack_range_y = 50   # Distância máxima para ataque (eixo y)
        
        # Flag para garantir que o som de ataque seja tocado apenas uma vez por ciclo de ataque
        self.attack_sound_played = False
        
        # Timer para o som de corrida (evita repetição a cada frame)
        self.run_sound_timer = 0

    def update_image(self, images_list=None, finish_on_end=False):
        """
        Atualiza a animação do NightBorne com um delay menor, tornando a troca de frames mais rápida.
        """
        # Defina um delay customizado menor para o NightBorne (por exemplo, 3 frames em vez de ANIMACAO_DELAY)
        custom_anim_delay = 3

        if images_list is None:
            images_list = self.current_images_list
        self.frame_count += 1
        if self.frame_count >= custom_anim_delay:
            self.current_image += 1
            if finish_on_end and self.current_image >= len(images_list):
                self.current_image = len(images_list) - 1
            else:
                self.current_image %= len(images_list)
            self.actor.image = images_list[self.current_image]
            self.frame_count = 0


    def attack_hit_active(self):
        """
        Retorna True somente se o frame atual estiver entre 10 e 12,
        definindo assim o momento “ativo” para causar dano.
        """
        return 10 <= self.current_image <= 12

    def update(self):
        """
        Atualiza o estado do inimigo, tratando as animações, movimento, ataques e colisões.
        """
        # Se estiver morrendo, apenas atualiza a animação de morte.
        if self.is_dying:
            death_images = self.images_death_right if self.facing_right else self.images_death_left
            self.update_image(death_images, finish_on_end=True)
            return

        # Se estiver tomando dano, atualiza a animação de dano.
        if self.is_taking_damage:
            dano_images = self.images_dano_right if self.facing_right else self.images_dano_left
            self.update_image(dano_images, finish_on_end=True)
            if self.current_image == len(dano_images) - 1:
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

            # Toca o som de ataque no frame específico (ex.: frame 10)
            if self.current_image == 10 and not self.attack_sound_played:
                if self.sound_attack:
                    play_sound(self.sound_attack)
                self.attack_sound_played = True

            # Verifica se é o momento de aplicar o dano.
            if self.attack_hit_active():
                self.check_attack_hit()

            # Ao fim da animação de ataque, volta para o estado idle.
            if self.current_image == len(self.current_images_list) - 1:
                self.is_attacking = False
                self.current_image = 0
                self.current_images_list = self.images_idle_right if self.facing_right else self.images_idle_left

            return  # Interrompe o restante do update enquanto estiver atacando

        # Se não estiver atacando, trata o movimento (patrulha) e aplica gravidade.
        if self.is_moving:
            # Toca o som de corrida periodicamente
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

            # Inverte a direção ao bater nos limites definidos.
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

        # Sincroniza a posição com a do actor.
        self.x = self.actor.x
        self.y = self.actor.y

        # Verifica colisões com as plataformas.
        self.verificar_colisoes()

        # Atualiza a animação do estado normal (idle ou patrulha).
        self.update_image()
