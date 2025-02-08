import pygame 
from pgzero.actor import Actor
from pgzero.builtins import sounds  # Importa o objeto sounds do Pygame Zero
from entity import Entity  # Certifique-se de que entity.py esteja disponível
from audio import play_sound  # Função auxiliar para tocar sons (respeita o mute global)

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
        self.current_images_list = self.images_idle_right  
        self.is_attacking     = False  
        self.is_running       = False    
        self.is_taking_damage = False  
        self.is_dying         = False
        self.facing_right     = True  
        self.is_moving        = True  # Para patrulhamento automático
        
        # Vida e dano
        self.vida  = vida
        self.dano  = dano
        
        # Controle da velocidade da animação
        self.frame_count = 0
        
        # Físicas
        self.velocidade_y = 0
        self.no_chao = False
        self.plataformas = plataformas  # Lista de plataformas

        # Atributos para lógica de ataque
        self.alvo = None          # Referência para o personagem (deve ser atribuída externamente)
        self.attack_range = 100   # Distância para iniciar o ataque
        self.hit_player = False   # Indica se o personagem já foi atingido no ataque atual

        # Atributo para controle do som ao correr (run)
        self.run_sound_timer = 0
        
        # Atributos de som – esses podem ser sobrescritos pelas subclasses
        self.sound_attack = None    # Som a ser reproduzido ao iniciar um ataque
        self.sound_run    = None    # Som a ser reproduzido durante o patrulhamento/corrida
        self.sound_damage = None    # Som a ser reproduzido quando o inimigo leva dano
        self.sound_death  = None    # Som a ser reproduzido quando o inimigo morre

    def update(self):
        # Se o inimigo está morrendo, atualiza a animação de morte e interrompe as demais ações.
        if self.is_dying:
            self.update_image(self.images_death_right if self.facing_right else self.images_death_left, finish_on_end=True)
            return

        # Se o inimigo está tomando dano, atualiza a animação de dano e não permite outras ações.
        if self.is_taking_damage:
            dano_list = self.images_dano_right if self.facing_right else self.images_dano_left
            self.update_image(dano_list, finish_on_end=True)
            if self.current_image == len(dano_list) - 1:
                self.is_taking_damage = False
                self.current_image = 0
                self.current_images_list = self.images_idle_right if self.facing_right else self.images_idle_left
            return

        # Se houver um alvo (personagem), verifica a distância para iniciar ou cancelar o ataque.
        if self.alvo is not None:
            distancia = abs(self.alvo.x - self.x)
            if distancia < self.attack_range:
                # Ajusta a direção para "encarar" o personagem.
                self.facing_right = (self.alvo.x > self.x)
                # Se ainda não estiver atacando, inicia o ataque.
                if not self.is_attacking:
                    self.is_attacking = True
                    self.current_image = 0
                    self.current_images_list = self.images_attack_right if self.facing_right else self.images_attack_left
                    self.hit_player = False
                    if self.sound_attack:
                        play_sound(self.sound_attack)
                # Enquanto o personagem estiver no alcance, interrompe o patrulhamento.
                self.is_moving = False
            else:
                # Se o alvo se afastar e o inimigo estava atacando, cancela o ataque.
                if self.is_attacking:
                    self.is_attacking = False
                    self.current_image = 0
                    self.current_images_list = self.images_idle_right if self.facing_right else self.images_idle_left
                self.is_moving = True

        # Se estiver atacando, atualiza a animação de ataque e verifica se o golpe deve atingir o personagem.
        if self.is_attacking:
            self.update_image()
            if self.attack_hit_active():
                self.check_attack_hit()
            return

        # Patrulhamento automático se não estiver atacando.
        if self.is_moving:
            # Toca o som de corrida periodicamente (para evitar repetir a cada frame)
            if self.run_sound_timer <= 0:
                if self.sound_run:
                    play_sound(self.sound_run)
                self.run_sound_timer = 30  # tempo em frames para repetir o som de corrida
            else:
                self.run_sound_timer -= 1

            if self.facing_right:
                self.actor.x += VELOCIDADE_CORRIDA
                self.current_images_list = self.images_run_right
            else:
                self.actor.x -= VELOCIDADE_CORRIDA
                self.current_images_list = self.images_run_left

            # Inverte a direção ao bater nos limites da tela.
            if self.actor.x >= 1200:
                self.facing_right = False
            elif self.actor.x <= 0:
                self.facing_right = True

        # Aplicando gravidade.
        self.velocidade_y += GRAVIDADE
        if self.velocidade_y > VELOCIDADE_QUEDA_MAX:
            self.velocidade_y = VELOCIDADE_QUEDA_MAX
        self.actor.y += self.velocidade_y

        # Sincroniza a posição da entidade com a do actor.
        self.x = self.actor.x
        self.y = self.actor.y

        # Verifica colisões com as plataformas.
        self.verificar_colisoes()

        # Atualiza a animação de estado normal (idle ou patrulhamento).
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
        Aplica dano ao inimigo.
        Se o inimigo já estiver tomando dano ou estiver morrendo, a chamada é ignorada.
        Se a vida chegar a 0, ativa a animação de morte; caso contrário, a animação de dano.
        """
        # Se o inimigo levar dano, interrompe o ataque.
        self.is_attacking = False
        
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
                self.current_images_list = self.images_death_right if self.facing_right else self.images_death_left
        else:
            self.is_taking_damage = True
            self.current_image = 0
            self.current_images_list = self.images_dano_right if self.facing_right else self.images_dano_left
            if self.sound_damage:
                play_sound(self.sound_damage)

    def verificar_colisoes(self):
        """
        Verifica colisão do inimigo com as plataformas utilizando o método da Entity.
        """
        self.no_chao = False  # Reinicia o status de estar no chão antes de verificar
        for plataforma in self.plataformas:
            if self.verificar_colisao_com(plataforma, self.velocidade_y):
                self.actor.y = plataforma.y
                self.velocidade_y = 0
                self.no_chao = True
                break
        if not self.no_chao:
            self.velocidade_y = min(self.velocidade_y, VELOCIDADE_QUEDA_MAX)

    def get_attack_hitbox(self):
        """
        Retorna um objeto pygame.Rect representando a área de alcance do ataque.
        Como os atributos x e y de Entity (e Actor) são o centro do inimigo,
        a área de ataque é calculada para ficar à frente do inimigo.
        """
        hitbox_width = 30   # Largura da área de ataque (ajuste conforme necessário)
        hitbox_height = self.altura  # Utiliza a altura definida em Entity
        if self.facing_right:
            hitbox_x = self.x + self.largura / 2
        else:
            hitbox_x = self.x - self.largura / 2 - hitbox_width
        hitbox_y = self.y - self.altura / 2
        return pygame.Rect(hitbox_x, hitbox_y, hitbox_width, hitbox_height)

    def attack_hit_active(self):
        """
        Retorna True se o frame atual do ataque for um dos frames ativos para aplicar dano.
        Por exemplo, se considerarmos que o frame do meio da animação de ataque é o ativo.
        """
        total_frames = len(self.current_images_list)
        meio = total_frames // 2  # Calcula o frame do meio
        return self.current_image == meio

    def check_attack_hit(self):
        """
        Verifica se o hitbox do ataque colide com o personagem (alvo).
        Se colidir e o personagem ainda não tiver sido atingido no ataque atual,
        aplica dano chamando o método take_damage do personagem.
        """
        if self.alvo is None:
            return
        hitbox = self.get_attack_hitbox()
        alvo_rect = pygame.Rect(self.alvo.x - self.alvo.largura/2,
                                self.alvo.y - self.alvo.altura/2,
                                self.alvo.largura,
                                self.alvo.altura)
        if hitbox.colliderect(alvo_rect) and not self.hit_player:
            self.alvo.take_damage(self.dano)
            self.hit_player = True

    def draw(self):
        # Ajuste de deslocamento para alinhar a imagem verticalmente (opcional)
        deslocamento_y = 10  # Ajuste conforme necessário
        self.actor.y -= deslocamento_y  # Aplica o deslocamento para o desenho
        self.actor.draw()
        self.actor.y += deslocamento_y  # Restaura a posição do ator após o desenho
