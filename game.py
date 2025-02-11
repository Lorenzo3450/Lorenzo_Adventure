import pgzrun
from pgzero.actor import Actor
from player import Personagem
from platforms import Platforms
from enemy_NightBorne import Enemy_NightBorne
from enemy_slime import Enemy_Slime
from espinho import Espinho  # Classe dos espinhos
from saw_blade import Saw_Blade
import audio
from audio import play_sound  # Função auxiliar para áudio
from door_key import Key, Door  # Classes de chave e porta
from pygame import Rect
from life_bar import LifeBar

# Definindo o tamanho da tela
WIDTH = 1200
HEIGHT = 800

# Carrega a música de fundo
music_bg = sounds.background

# =================================================================
# CLASSE DO JOGO
# =================================================================


class Game:
    def __init__(self, fases):
        self.fases = fases  # Lista de fases
        self.fase_atual = 0  # Inicia na primeira fase
        self.iniciar_fase(self.fase_atual)
        play_sound(music_bg, loops=-1)
        # Atributo para controlar se o game over já foi iniciado
        self.game_over_started = False
        # Cria o Actor para a imagem de game over (certifique-se que "game_over_image" exista em images/)
        self.game_over_image = Actor(
            "game_over", center=(WIDTH // 2, HEIGHT // 2))

    def iniciar_fase(self, fase_idx):
 
        fase = self.fases[fase_idx]
        self.plataformas = fase.get('plataformas', [])
        self.espinhos = fase.get('spikes', [])
        self.saw_blades = fase.get('saw_blade', [])
        self.fundo = Actor(fase.get('background', 'default_background'))
         # Exibe o tutorial somente na primeira fase (índice 0)
        self.show_tutorial = (fase_idx == 0)

        spawn_player = fase.get('spawn_player', (20, 700))
        x_inicial, y_inicial = spawn_player
        self.barra_vida = LifeBar(10, 10)
        self.personagem = Personagem(
            self.plataformas, self.barra_vida, x_inicial, y_inicial)

        self.inimigos = []
        enemy_configs = fase.get('enemies', [])
        for config in enemy_configs:
            enemy = self.criar_inimigo(config)
            if enemy:
                enemy.alvo = self.personagem
                self.inimigos.append(enemy)

        if not self.inimigos:
            inimigo = Enemy_Slime(posicao_inicial_x=520, posicao_inicial_y=700,
                                  plataformas=self.plataformas, x_inicial=500, x_final=650)
            inimigo.alvo = self.personagem
            self.inimigos.append(inimigo)

            inimigo2 = Enemy_NightBorne(posicao_inicial_x=580, posicao_inicial_y=320,
                                        plataformas=self.plataformas, x_inicial=400, x_final=700)
            inimigo2.alvo = self.personagem
            self.inimigos.append(inimigo2)

        self.personagem.enemies = self.inimigos

        self.keys = [Key(x, y) for x, y in fase.get('keys', [])]
        self.doors = [Door(x, y) for x, y in fase.get('doors', [])]
        self.collected_keys = []

        self.image_timer = 0
        self.image_interval = 1

        # Reinicia a flag de game over ao iniciar a fase
        self.game_over_started = False

    def criar_inimigo(self, config):
        tipo = config.get('type', '').lower()
        x = config.get('x', 0)
        y = config.get('y', 0)
        x_min = config.get('x_min', x)
        x_max = config.get('x_max', x)
        if tipo == 'slime':
            return Enemy_Slime(posicao_inicial_x=x, posicao_inicial_y=y,
                               plataformas=self.plataformas, x_inicial=x_min, x_final=x_max)
        elif tipo == 'nightborne':
            return Enemy_NightBorne(posicao_inicial_x=x, posicao_inicial_y=y,
                                    plataformas=self.plataformas, x_inicial=x_min, x_final=x_max)
        else:
            return None

    def mudar_fase(self):
        global game_state
        self.fase_atual += 1
        if self.fase_atual >= len(self.fases):  # Se chegou ao fim das fases
            game_state = "menu"  # Retorna ao menu inicial
            self.fase_atual = 0  # Reseta para a primeira fase para próxima jogada
        else:
            self.iniciar_fase(self.fase_atual)

    def restart_level(self):
        # Reinicia a fase atual e reseta a flag de game over
        self.iniciar_fase(self.fase_atual)
        self.game_over_started = False

    def update(self):
        # Se o personagem morreu, inicia a lógica de game over
        if self.personagem.is_dead:
            if not self.game_over_started:
                self.game_over_started = True
                # Toca o som de game over (certifique-se que "game_over" exista em sounds/)
                play_sound(sounds.game_over)
                # Agende o reinício da fase para quando o som terminar
                # Para isso, usamos a duração do som (em segundos)
                clock.schedule_unique(self.restart_level,
                                      sounds.game_over.get_length())
            # Não atualiza os demais elementos enquanto estiver na tela de game over
            return

        # Atualiza o personagem e seus sprites
        self.personagem.update()
        self.image_timer += 1 / 60
        if self.image_timer >= self.image_interval:
            self.personagem.update_image()
            self.image_timer = 0

        # Atualiza os inimigos
        for inimigo in self.inimigos:
            inimigo.update()

        # Atualiza as serras
        for saw_blade in self.saw_blades:
            saw_blade.update()

        # Verifica colisões com chaves
        player_rect = self.personagem.get_rect()
        for key in self.keys:
            if key.check_collision(player_rect) and not key.is_collected:
                key.is_collected = True
                self.collected_keys.append(key)
                play_sound(sounds.pega_chave)

        # Atualiza portas
        for door in self.doors:
            door.update(1/60)
            door_rect = door.actor._rect
            if door.locked:
                if door_rect.colliderect(player_rect) and self.collected_keys:
                    door.unlock()
                    self.collected_keys.pop()
            elif door.is_open and door_rect.colliderect(player_rect):
                self.mudar_fase()

        # Verifica colisões do personagem com espinhos
        player_rect = Rect(
            self.personagem.x - self.personagem.largura / 2,
            self.personagem.y - self.personagem.altura / 2,
            self.personagem.largura,
            self.personagem.altura
        )
        for espinho in self.espinhos:
            if player_rect.colliderect(espinho.get_rect()):
                self.personagem.take_damage(espinho.damage)

        # Verifica colisões do personagem com as serras
        for saw_blade in self.saw_blades:
            if player_rect.colliderect(saw_blade.get_rect()):
                self.personagem.take_damage(saw_blade.damage)

    def draw(self):
        screen.clear()
        self.fundo.draw()
        for plataforma in self.plataformas:
            plataforma.draw()
        for espinho in self.espinhos:
            espinho.draw()
        for saw_blade in self.saw_blades:
            saw_blade.draw()
        for key in self.keys:
            key.draw()
        for door in self.doors:
            door.draw()
        self.personagem.draw()
        self.barra_vida.draw(screen)
        for inimigo in self.inimigos:
            inimigo.draw()

        # Se o personagem estiver morto, exibe a imagem de game over
        if self.personagem.is_dead:
            self.game_over_image.draw()

        # Se o tutorial estiver ativo, desenha a sobreposição
        if self.show_tutorial:
            # Define a posição e o tamanho do retângulo do tutorial
            tutorial_rect = Rect((100, 100), (WIDTH - 200, HEIGHT - 200))
            # Desenha um retângulo preenchido de preto (você pode ajustar a cor, transparência, etc.)
            screen.draw.filled_rect(tutorial_rect, "black")
            # Adiciona o texto do tutorial (ajuste a mensagem, fonte e posição conforme necessário)
            screen.draw.text(
                "Tutorial:\n\n"
                "- Use as teclas A e D do teclado para mover seu personagem.\n"
                "- Clique com o botão esquerdo do mouse para atacar e com o direito para defender.\n"
                "- Colete as chaves para abrir as portas.\n\n"
                "Clique para fechar este tutorial.",
                center=tutorial_rect.center,
                color="white",
                fontsize=24,
                align="center"
            )


# =================================================================
# CONFIGURAÇÃO DAS FASES (exemplo)
# =================================================================
fases = [
    # Fase 1 – Introdução
    {

        'name': 'fase 1',
        'background': 'cenario1',
        'spawn_player': (20, 700),
        'plataformas': [
                Platforms(0, 750, 300),      # chão: x de 0 
                Platforms(350, 700, 8),    # plataforma intermediária
                Platforms(550, 630, 50),    # plataforma superior


        ],
        'spikes': [
            Espinho(150, 750, 3),         # sobre o chão

        ],
        'saw_blade': [
            # sobre a plataforma de 350,700
            Saw_Blade(x_inicial=360, y=700, x_final=480)
        ],
        'keys': [(550, 630)],           # chave na plataforma de 500,550
        'doors': [(850, 630)],          # porta na plataforma de 800,600
        'enemies': [
            {'type': 'slime', 'x': 630, 'y': 650, 'x_min': 550, 'x_max': 750}
        ]
    },

    # Fase 2 – Mais obstáculos
    {
        'name': 'fase 2',
        'background': 'cenario1',
        'spawn_player': (20, 700),
        'plataformas': [
                Platforms(0, 750, 350),
                Platforms(400, 680, 20),
                Platforms(850, 630, 10),
                Platforms(800, 580, 1),
                Platforms(250, 540, 15),

        ],
        'spikes': [
            Espinho(200, 750, 3),

        ],
        'saw_blade': [
            Saw_Blade(x_inicial=410, y=680, x_final=580)
        ],
        'keys': [(255, 540)],
        'doors': [(870, 630)],
        'enemies': [
            {'type': 'slime', 'x': 350, 'y': 530, 'x_min': 300, 'x_max': 450}
        ]
    },

    # Fase 3 – Plataforma em escada
    {
        'name': 'fase 3',
        'background': 'cenario1',
        'spawn_player': (20, 700),
        'plataformas': [
                Platforms(0, 750, 300),
                Platforms(320, 670, 15),
                Platforms(750, 600, 1),
                Platforms(820, 550, 15),
                Platforms(600, 530, 2),
                Platforms(150, 470, 15),

        ],
        'spikes': [
            Espinho(100, 750, 3),
            Espinho(370, 670, 2),
            Espinho(550, 670, 2),
            Espinho(850, 550, 2)
        ],
        'saw_blade': [
            Saw_Blade(x_inicial=250, y=470, x_final=500)
        ],
        'keys': [(1140, 550)],
        'doors': [(200, 470)],
        'enemies': [
            {'type': 'slime', 'x': 830, 'y': 550, 'x_min': 920, 'x_max': 1070},
            {'type': 'slime', 'x': 400, 'y': 750, 'x_min': 200, 'x_max': 500}
        ]
    },

    # Fase 4 – Mais plataformas e obstáculos móveis
    {
        'name': 'fase 4',
        'background': 'cenario1',
        'spawn_player': (20, 700),
        'plataformas': [
                Platforms(0, 750, 400),
                Platforms(900, 700, 5),
                Platforms(700, 650, 5),
                Platforms(300, 600, 7),
                Platforms(570, 650, 1),
                Platforms(600, 520, 16),
                Platforms(1150, 520, 1),
                Platforms(250, 420, 10),
                Platforms(100, 330, 3),

        ],
        'spikes': [
            Espinho(280, 750, 3),
            Espinho(740, 650, 2),
            Espinho(650, 520, 2),
            Espinho(950, 520, 2)
        ],
        'saw_blade': [
            Saw_Blade(x_inicial=360, y=750, x_final=500),
            Saw_Blade(x_inicial=310, y=600, x_final=450),

            Saw_Blade(x_inicial=260, y=420, x_final=460)
        ],
        'keys': [(1150, 520)],
        'doors': [(120, 330)],
        'enemies': [
            {'type': 'slime', 'x': 700, 'y': 550, 'x_min': 710, 'x_max': 890}
        ]
    },

    # Fase 5 – Configuração mais complexa
    {
        'name': 'fase 5',
        'background': 'cenario1',
        'spawn_player': (20, 700),
        'plataformas': [
                Platforms(0, 750, 500),
                Platforms(550, 680, 4),
                Platforms(250, 600, 8),
                Platforms(600, 550, 8),
                Platforms(900, 500, 15),
                Platforms(1100, 440, 1),
                Platforms(980, 360, 3),
                Platforms(1100, 300, 12),
                Platforms(400, 300, 20)
        ],
        'spikes': [
            Espinho(250, 750, 3),
            Espinho(600, 680, 1),


            Espinho(950, 500, 2),

        ],
        'saw_blade': [

            Saw_Blade(x_inicial=710, y=300, x_final=900),
            Saw_Blade(x_inicial=470, y=300, x_final=700)
        ],
        'keys': [(1180, 300)],
        'doors': [(430, 300)],
        'enemies': [
            {'type': 'slime', 'x': 340, 'y': 750, 'x_min': 340, 'x_max': 500},
            {'type': 'nightborne', 'x': 650,
             'y': 550, 'x_min': 600, 'x_max': 800},
            {'type': 'slime', 'x': 200, 'y': 650, 'x_min': 250, 'x_max': 400}
        ]
    },

    # Fase 6 – Obstáculos em maior quantidade
    {
        'name': 'fase 6',
        'saw_blade': 'cenario1',
        'spawn_player': (20, 700),
        'plataformas': [
                Platforms(0, 750, 500),
                Platforms(1050, 680, 4),
                Platforms(700, 620, 8),
                Platforms(600, 550, 1),
                Platforms(130, 550, 19),
                Platforms(50, 490, 1),
                Platforms(120, 420, 32),

        ],
        'spikes': [
            Espinho(400, 750, 3),
            Espinho(620, 750, 2),
            Espinho(300, 750, 2),
            Espinho(1100, 680, 2),
            Espinho(190, 550, 2),
            Espinho(500, 550, 2),
            Espinho(500, 420, 2),
            Espinho(300, 420, 2),
            Espinho(750, 420, 2)

        ],
        'saw_blade': [

            Saw_Blade(x_inicial=700, y=620, x_final=900),
            Saw_Blade(x_inicial=240, y=550, x_final=480),
            Saw_Blade(x_inicial=110, y=400, x_final=500),
            Saw_Blade(x_inicial=600, y=400, x_final=900),
        ],
        'keys': [(150, 550)],
        'doors': [(950, 420)],
        'enemies': [
            {'type': 'nightborne', 'x': 730,
             'y': 750, 'x_min': 700, 'x_max': 890}
        ]
    },

    # Fase 7 – Layout com “escada” de plataformas
    {
        'name': 'fase 7',
        'background': 'cenario1',
        'spawn_player': (20, 700),
        'plataformas': [
                Platforms(0, 750, 500),
                Platforms(110, 670, 1),
                Platforms(200, 620, 1),
                Platforms(290, 550, 5),
                Platforms(500, 500, 10),
                Platforms(840, 420, 1),
                Platforms(920, 420, 1),
                Platforms(760, 360, 1),
                Platforms(400, 300, 10)

        ],
        'spikes': [
            Espinho(150, 750, 39),
            Espinho(320, 550, 2)


        ],
        'saw_blade': [
            Saw_Blade(x_inicial=840, y=425, x_final=1000),
        ],
        'keys': [(920, 420)],
        'doors': [(420, 300)],
        'enemies': [
            {'type': 'nightborne', 'x': 520,
             'y': 500, 'x_min': 520, 'x_max': 750}
        ]
    },


    # Fase 8 – Obstáculos em ambiente mais “horizontal”
    {
        'name': 'fase 8',
        'background': 'cenario1',
        'spawn_player': (20, 700),
        'plataformas': [
                Platforms(0, 750, 500),
                Platforms(110, 670, 1),
                Platforms(15, 600, 1),
                Platforms(110, 530, 5),
                Platforms(320, 530, 10),
                Platforms(15, 460, 1),
                Platforms(110, 420, 3),
                Platforms(220, 360, 1),
                Platforms(290, 300, 2),
                Platforms(540, 460, 1),
                Platforms(600, 400, 1),
                Platforms(520, 340, 1),
                Platforms(600, 280, 15)

        ],
        'spikes': [
            Espinho(150, 750, 39),
            Espinho(135, 420, 1),
            Espinho(315, 530, 4),
            Espinho(505, 530, 3)


        ],
        'saw_blade': [
            Saw_Blade(x_inicial=110, y=530, x_final=280),
            Saw_Blade(x_inicial=580, y=400, x_final=780),
        ],
        'keys': [(290, 300)],
        'doors': [(950, 280)],
        'enemies': [
            {'type': 'nightborne', 'x': 650,
             'y': 280, 'x_min': 630, 'x_max': 900}
        ]
    },

    # Fase 9 – Fase “final” antes da maior dificuldade
    {
        'name': 'fase 9',
        'background': 'cenario1',
        'spawn_player': (20, 700),
        'plataformas': [
                Platforms(0, 750, 500),
                Platforms(110, 670, 1),
                Platforms(210, 670, 1),
                Platforms(310, 670, 1),
                Platforms(410, 670, 1),
                Platforms(510, 670, 1),
                Platforms(610, 670, 1),
                Platforms(710, 670, 1),
                Platforms(810, 670, 1),
                Platforms(910, 670, 1),
                Platforms(1010, 670, 1),
                Platforms(1110, 670, 1),
                Platforms(1150, 600, 1),
                Platforms(1100, 540, 1),
                Platforms(1000, 500, 1),
                Platforms(900, 500, 1),
                Platforms(800, 500, 1),
                Platforms(700, 500, 1),
                Platforms(600, 500, 1),
                Platforms(500, 500, 1),
                Platforms(400, 500, 1),
                Platforms(300, 500, 1),
                Platforms(200, 500, 1),
                Platforms(100, 500, 1),
                Platforms(50, 420, 1),
                Platforms(100, 360, 1),
                Platforms(200, 360, 1),
                Platforms(300, 360, 1),
                Platforms(400, 360, 1),
                Platforms(500, 360, 1),
                Platforms(600, 360, 1),
                Platforms(700, 360, 1),
                Platforms(800, 360, 1),
                Platforms(900, 360, 15)





        ],
        'spikes': [
            Espinho(150, 750, 39),



        ],
        'saw_blade': [
            Saw_Blade(x_inicial=110, y=500, x_final=1100),
            Saw_Blade(x_inicial=110, y=360, x_final=850),

        ],
        'keys': [(100, 500)],
        'doors': [(1150, 360)],
        'enemies': [
            {'type': 'nightborne', 'x': 910,
             'y': 360, 'x_min': 910, 'x_max': 1100}
        ]
    },

    # Fase 10 – A fase máxima com o maior número de obstáculos
    {
        'name': 'fase 10',
        'background': 'cenario1',
        'spawn_player': (20, 700),
        'plataformas': [
            Platforms(0, 750, 500),
            Platforms(110, 670, 1),
            Platforms(210, 670, 1),
            Platforms(310, 670, 1),
            Platforms(410, 670, 1),
            Platforms(510, 670, 1),
            Platforms(610, 670, 1),
            Platforms(710, 670, 1),
            Platforms(810, 670, 1),
            Platforms(910, 670, 1),
            Platforms(1010, 670, 1),
            Platforms(1110, 670, 1),
            Platforms(1150, 600, 1),
            Platforms(1100, 540, 1),
            Platforms(20, 500, 18),
            Platforms(600, 500, 16),
            Platforms(50, 440, 1),
            Platforms(100, 380, 1),
            Platforms(200, 320, 1),
            Platforms(300, 320, 1),
            Platforms(400, 320, 1),
            Platforms(500, 320, 1),
            Platforms(600, 320, 1),
            Platforms(700, 320, 1),
            Platforms(800, 320, 1),
            Platforms(900, 320, 15)






        ],
        'spikes': [
            Espinho(150, 750, 39),
            Espinho(980, 500, 2),
            Espinho(800, 500, 4),
            Espinho(650, 500, 4),
            Espinho(460, 500, 2)



        ],
        'saw_blade': [
            Saw_Blade(x_inicial=110, y=670, x_final=600),
            Saw_Blade(x_inicial=500, y=670, x_final=980),
            Saw_Blade(x_inicial=110, y=320, x_final=450),
            Saw_Blade(x_inicial=500, y=320, x_final=850)

        ],
        'keys': [(100, 500)],
        'doors': [(1150, 320)],
        'enemies': [
            {'type': 'nightborne', 'x': 910, 'y': 360,
             'x_min': 910, 'x_max': 1100},
            {'type': 'nightborne', 'x': 80,
             'y': 500, 'x_min': 80, 'x_max': 400}
        ]
    },
]

# =================================================================
# CLASSE DO MENU (TELA INICIAL)
# =================================================================
# Variável global para controlar o estado do jogo: "menu" ou "playing"
game_state = "menu"


class Menu:
    def __init__(self):
        # Substitua os nomes das imagens pelos nomes que você já tem
        self.background = Actor("menu_background")
        self.start_button = Actor("btn_start", center=(WIDTH // 2, 300))
        self.quit_button = Actor("btn_quit", center=(WIDTH // 2, 400))
        # O botão de som alterna a imagem conforme o estado
        sound_img = "btn_mute" if audio.audio_muted else "btn_sound"
        self.sound_button = Actor(sound_img, center=(WIDTH - 100, 50))

    def update_sound_button(self):
        if audio.audio_muted:
            self.sound_button.image = "btn_mute"
        else:
            self.sound_button.image = "btn_sound"

    def draw(self):
        self.background.draw()
        self.start_button.draw()
        self.quit_button.draw()
        self.sound_button.draw()

    def on_mouse_down(self, pos):
        global game_state
        if self.start_button.collidepoint(pos):
            # Inicia o jogo
            game_state = "playing"
        elif self.quit_button.collidepoint(pos):
            # Fecha o jogo
            quit()  # ou use exit()
        elif self.sound_button.collidepoint(pos):
            # Alterna o áudio
            audio.audio_muted = not audio.audio_muted
            self.update_sound_button()
            if audio.audio_muted:
                music_bg.stop()
            else:
                music_bg.play(loops=-1)
                music_bg.set_volume(0.5)


# =================================================================
# INSTANCIANDO O JOGO E O MENU
# =================================================================
game = Game(fases)
menu = Menu()

# =================================================================
# FUNÇÕES DE INTERAÇÃO (mouse e teclado)
# =================================================================


def update():
    if game_state == "menu":
        # Se desejar, adicione animações no menu aqui
        pass
    elif game_state == "playing":
        game.update()


def draw():
    if game_state == "menu":
        menu.draw()
    elif game_state == "playing":
        game.draw()


def on_mouse_down(pos, button):
    global game_state
    if game_state == "menu":
        menu.on_mouse_down(pos)
    else:
        # Se o tutorial estiver ativo, ao clicar, ele é desativado
        if game.show_tutorial:
            game.show_tutorial = False
        else:
            if button == 1:  # botão esquerdo
                game.personagem.on_mouse_down(pos, "left")
            elif button == 3:  # botão direito
                game.personagem.on_mouse_down(pos, "right")



def on_mouse_up(pos, button):
    if game_state == "playing" and button == 3:
        game.personagem.on_mouse_up(pos, "right")


def on_key_down(key):

    if key == keys.M:
        audio.audio_muted = not audio.audio_muted
        if game_state == "menu":
            menu.update_sound_button()
        if audio.audio_muted:
            music_bg.stop()
        else:
            music_bg.play(loops=-1)
            music_bg.set_volume(0.5)
    if game_state == "playing":
        pass


pgzrun.go()
