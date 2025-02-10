from pgzero.actor import Actor 
from pgzero.builtins import sounds  # Importa o objeto sounds do Pygame Zero
from entity import Entity        # Certifique-se de que entity.py esteja disponível
from audio import play_sound     # Função auxiliar para tocar sons (respeita o mute global)
from pygame import Rect
import math

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
                 plataformas, x_inicial, x_final):
        # Define um tamanho padrão para o inimigo (ajuste conforme necessário)
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
        self.current_images_list = self.images_idle_right  
        self.is_attacking     = False  
        self.is_running       = False    
        self.is_taking_damage = False  
        self.is_dying         = False
        self.facing_right     = True  
        self.is_moving        = True  # Patrulhamento automático
        
        # Vida e dano
        self.vida  = vida
        self.dano  = dano
        
        # Controle da velocidade da animação
        self.frame_count = 0

        # Limites da patrulha (definidos na criação do inimigo)
        self.x_inicial = x_inicial
        self.x_final = x_final
        
        # Físicas
        self.velocidade_y = 0
        self.no_chao = False
        self.plataformas = plataformas  # Lista de plataformas
        
        # Lista opcional de obstáculos (por exemplo, espinhos) – pode ser definida externamente
        self.obstaculos = []  

        # Atributos para lógica de ataque
        self.alvo = None          # Referência para o personagem (deve ser atribuída externamente)
        self.attack_range = 100   # Distância para iniciar o ataque
        self.hit_player = False   # Indica se o personagem já foi atingido no ataque atual
        self.attack_range_y = 50  # Valor ajustável conforme a necessidade


        # Atributo para controle do som ao correr (run)
        self.run_sound_timer = 0
        
        # Atributos de som – podem ser sobrescritos pelas subclasses
        self.sound_attack = None    # Som ao iniciar um ataque
        self.sound_run    = None    # Som durante o patrulhamento/corrida
        self.sound_damage = None    # Som quando o inimigo leva dano
        self.sound_death  = None    # Som quando o inimigo morre

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

        # Se houver um alvo (personagem), verifica a distância para atacar.
        if self.alvo is not None:
            distancia_x = abs(self.alvo.x - self.x)
            distancia_y = abs(self.alvo.y - self.y)
            if distancia_x < self.attack_range and distancia_y < self.attack_range_y:
                # Ajusta a direção para "encarar" o personagem.
                self.facing_right = (self.alvo.x > self.x)
                if not self.is_attacking:
                    self.is_attacking = True
                    self.current_image = 0
                    self.current_images_list = (
                        self.images_attack_right if self.facing_right else self.images_attack_left
                    )
                    self.hit_player = False
                    if self.sound_attack:
                        play_sound(self.sound_attack)
                self.is_moving = False
            else:
                if self.is_attacking:
                    self.is_attacking = False
                    self.current_image = 0
                    self.current_images_list = (
                        self.images_idle_right if self.facing_right else self.images_idle_left
                    )
                self.is_moving = True

        # Se estiver atacando, atualiza a animação de ataque e aplica dano se for o momento.
        if self.is_attacking:
            self.update_image()
            if self.attack_hit_active():
                self.check_attack_hit()
            return

        # --- Lógica de patrulhamento (movimentação automática) ---
        if self.is_moving:
            check_offset_y = 5  # Deslocamento vertical para a verificação (ajuste conforme necessário)

            # Verifica se atingiu os limites da patrulha e inverte a direção se necessário
            if self.actor.x <= self.x_inicial:
                self.actor.x = self.x_inicial
                self.facing_right = True
            elif self.actor.x >= self.x_final:
                self.actor.x = self.x_final
                self.facing_right = False

            # Verifica se há um obstáculo à frente
            check_point = (
                (self.actor.x + VELOCIDADE_CORRIDA, self.actor.y + self.altura / 2 + check_offset_y)
                if self.facing_right 
                else (self.actor.x - VELOCIDADE_CORRIDA, self.actor.y + self.altura / 2 + check_offset_y)
            )
            obstaculo_encontrado = any(
                obst.get_rect().collidepoint(check_point) for obst in self.obstaculos
            )
            if obstaculo_encontrado:
                self.facing_right = not self.facing_right

            # Movimento horizontal
            self.actor.x += VELOCIDADE_CORRIDA if self.facing_right else -VELOCIDADE_CORRIDA
            self.current_images_list = self.images_run_right if self.facing_right else self.images_run_left

            # Toca o som de corrida periodicamente
            if self.run_sound_timer <= 0:
                if self.sound_run:
                    play_sound(self.sound_run)
                self.run_sound_timer = 30
            else:
                self.run_sound_timer -= 1
        # --- Fim da lógica de patrulhamento ---

        # Aplica gravidade.
        self.velocidade_y += GRAVIDADE
        if self.velocidade_y > VELOCIDADE_QUEDA_MAX:
            self.velocidade_y = VELOCIDADE_QUEDA_MAX
        self.actor.y += self.velocidade_y

        # Atualiza a posição interna com a do actor.
        self.x = self.actor.x
        self.y = self.actor.y

        # Verifica colisões com as plataformas (ajustando para os offsets)
        self.verificar_colisoes()

        # Atualiza a animação para o estado normal (idle ou patrulhamento).
        self.update_image()

    def update_image(self, images_list=None, finish_on_end=False):
        """
        Atualiza a imagem atual da animação.
        Se images_list for fornecida, utiliza-a; caso contrário, usa self.current_images_list.
        Se finish_on_end for True, a animação para na última imagem.
        """
        if images_list is None:
            images_list = self.current_images_list
        self.frame_count += 1
        if self.frame_count >= ANIMACAO_DELAY:
            self.current_image += 1
            if finish_on_end and self.current_image >= len(images_list):
                self.current_image = len(images_list) - 1
            else:
                self.current_image %= len(images_list)
            self.actor.image = images_list[self.current_image]
            self.frame_count = 0

    def take_damage(self, damage):
        """
        Aplica dano ao inimigo e inicia a animação de dano ou de morte.
        """
        self.is_attacking = False  # Interrompe o ataque se estiver em progresso
        if self.is_dying or self.is_taking_damage:
            return
        self.vida -= damage
        if self.vida <= 0:
            self.vida = 0
            if not self.is_dying:
                if self.sound_death:
                    play_sound(self.sound_death)
                self.is_dying = True
                self.current_image = 0
                self.current_images_list = (
                    self.images_death_right if self.facing_right else self.images_death_left
                )
        else:
            self.is_taking_damage = True
            self.current_image = 0
            self.current_images_list = (
                self.images_dano_right if self.facing_right else self.images_dano_left
            )
            if self.sound_damage:
                play_sound(self.sound_damage)

    def verificar_colisoes(self):
        """Verifica a colisão do inimigo com as plataformas, ajustando os offsets."""
        self.no_chao = False
        for plataforma in self.plataformas:
            offset_x = getattr(plataforma, "offset_x", 0)
            offset_y = getattr(plataforma, "offset_y", 0)
        
            # Retângulo da plataforma
            plat_rect = Rect(plataforma.x + offset_x, plataforma.y + offset_y,
                         plataforma.largura, plataforma.altura)
        
            # Retângulo do inimigo (considerando o actor centralizado)
            enemy_rect = Rect(self.actor.x - self.largura / 2,
                          self.actor.y - self.altura / 2,
                          self.largura, self.altura)
        
            if enemy_rect.colliderect(plat_rect):
                # Posiciona o inimigo para que sua base fique no topo da plataforma
                self.actor.y = plataforma.y + offset_y - self.altura / 2
                self.velocidade_y = 0
                self.no_chao = True
                break
        if not self.no_chao:
            self.velocidade_y = min(self.velocidade_y, VELOCIDADE_QUEDA_MAX)

    def get_attack_hitbox(self):
        """
        Retorna um pygame.Rect representando a área de alcance do ataque, à frente do inimigo.
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
        """
        Retorna True se o frame atual do ataque for o momento ativo para causar dano.
        """
        total_frames = len(self.current_images_list)
        meio = total_frames // 2
        return self.current_image == meio

    def check_attack_hit(self):
        """
        Verifica se o hitbox do ataque colide com o alvo e, se sim, aplica dano.
        """
        if self.alvo is None:
            return
        hitbox = self.get_attack_hitbox()
        alvo_rect = Rect(
            self.alvo.x - self.alvo.largura / 2,
            self.alvo.y - self.alvo.altura / 2,
            self.alvo.largura,
            self.alvo.altura
        )
        if hitbox.colliderect(alvo_rect) and not self.hit_player:
            self.alvo.take_damage(self.dano)
            self.hit_player = True

    def draw(self):
        # Opcional: ajuste de deslocamento para alinhar a imagem verticalmente
        deslocamento_y = 10
        self.actor.y -= deslocamento_y
        self.actor.draw()
        self.actor.y += deslocamento_y
