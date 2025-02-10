import pgzrun
from pgzero.actor import Actor
from player import Personagem
from plataformas import Plataforma
# Certifique-se de que esta classe está implementada
from enemy_NightBorne import Enemy_NightBorne
from enemy_slime import Enemy_Slime
from espinho import Espinho  # Importe a classe dos espinhos
import audio
from audio import play_sound  # Importa a função auxiliar para áudio
from door_key import Key, Door  # Importa as classes de chave e porta
from pygame import Rect
from life_bar import LifeBar


# Definindo o tamanho da tela
WIDTH = 1200
HEIGHT = 800

# Carrega a música de fundo
music_bg = sounds.background


class Game:
    def __init__(self, fases):
        self.fases = fases  # Lista de fases
        self.fase_atual = 0  # Inicia na primeira fase
        self.iniciar_fase(self.fase_atual)

    def iniciar_fase(self, fase_idx):
        fase = self.fases[fase_idx]
        plataformas = fase['plataformas']
        # Recupera os espinhos (se houver) ou retorna lista vazia
        espinhos = fase.get('espinhos', [])
        fundo = fase['fundo']
        x_inicial = 20  # Exemplo: posição inicial do personagem
        y_inicial = 700

        self.fundo = Actor(fundo)
        # Exemplo: barra de vida na posição (10, 10)
        self.barra_vida = LifeBar(10, 10)
        self.personagem = Personagem(
            plataformas, self.barra_vida, x_inicial, y_inicial)
        self.plataformas = plataformas
        self.espinhos = espinhos  # Armazena os espinhos da fase
        self.inimigos = []  # Lista de inimigos
        self.image_timer = 0
        self.image_interval = 1

        # Instancia um inimigo de exemplo
        inimigo = Enemy_Slime(posicao_inicial_x=520, posicao_inicial_y=700,
                              plataformas=plataformas, x_inicial=500, x_final=650)
        
        inimigo2 = Enemy_NightBorne(posicao_inicial_x=580, posicao_inicial_y=320,
                              plataformas=plataformas, x_inicial=400, x_final=700)

        self.inimigos.append(inimigo)
        self.inimigos.append(inimigo2)

        # Atribui o inimigo à lista de inimigos do personagem
        self.personagem.enemies = [inimigo,inimigo2]
        inimigo.alvo = self.personagem
        inimigo2.alvo = self.personagem

        play_sound(music_bg, loops=-1)

        # Cria as chaves e portas da fase
        self.keys = [Key(x, y) for x, y in fase.get(
            'keys', [])]  # Cria a lista de chaves
        self.doors = [Door(x, y) for x, y in fase.get(
            'doors', [])]  # Cria a lista de portas
        self.collected_keys = []  # Lista para armazenar as chaves coletadas

    def mudar_fase(self):
        self.fase_atual += 1
        if self.fase_atual >= len(self.fases):
            self.fase_atual = 0  # Reinicia as fases ou implemente outra lógica
        self.iniciar_fase(self.fase_atual)

    def update(self):
        self.personagem.update()
        self.image_timer += 1 / 60
        if self.image_timer >= self.image_interval:
            self.personagem.update_image()
            self.image_timer = 0

        for inimigo in self.inimigos:
            inimigo.update()
        # Verifica colisão com chaves
        player_rect = self.personagem.get_rect()
        for key in self.keys:
            if key.check_collision(player_rect) and not key.is_collected:
                key.is_collected = True
                self.collected_keys.append(key)
                play_sound(sounds.pega_chave)  # Adicione um som de coleta

        # Atualiza e verifica portas
        for door in self.doors:
            door.update(1/60)
            door_rect = door.actor._rect  # Usar _rect diretamente

            if door.locked:
                if door_rect.colliderect(player_rect) and self.collected_keys:
                    door.unlock()
                    self.collected_keys.pop()
            elif door.is_open and door_rect.colliderect(player_rect):
                self.mudar_fase()

        # Verifica colisão do personagem com os espinhos
        player_rect = Rect(
            self.personagem.x - self.personagem.largura / 2,
            self.personagem.y - self.personagem.altura / 2,
            self.personagem.largura,
            self.personagem.altura
        )
        for espinho in self.espinhos:
            if player_rect.colliderect(espinho.get_rect()):
                self.personagem.take_damage(espinho.damage)

    # Na classe Game, atualize o método draw:
    def draw(self):
        screen.clear()
        self.fundo.draw()
        for plataforma in self.plataformas:
            plataforma.draw()
        for espinho in self.espinhos:
            espinho.draw()
        for key in self.keys:
            key.draw()
        for door in self.doors:
            door.draw()
        self.personagem.draw()
        self.barra_vida.draw(screen)
        for inimigo in self.inimigos:
            inimigo.draw()


# Configuração das fases (exemplo)
fases = [
    {
        'nome': 'fase 1',
        'fundo': 'cenario2',
        'plataformas': [
            Plataforma(0, 750, 250),
            Plataforma(400, 700, 10),
            Plataforma(720, 650, 10),
            Plataforma(550, 600, 3),
            Plataforma(450, 550, 2),
            Plataforma(0, 500, 13),
            Plataforma(10, 450, 2),
            Plataforma(120, 400, 2),
            Plataforma(200, 400, 2),
            Plataforma(280, 350, 2),
            Plataforma(360, 300, 15),
            Plataforma(820, 250, 1),
            Plataforma(920,200,12)


        ],
        'espinhos': [
            Espinho(150, 750, 3),
            Espinho(150, 500, 2),
            Espinho(250, 500, 2),
            Espinho(930, 200, 2),
            ],
            
        'keys': [(1150, 195)],  # Posição da chave
        'doors': [(700, 295)]  # Posição da porta
    },
    {
        'nome': 'fase 2',
        'fundo': 'cenario2',
        'plataformas': [
            Plataforma(100, 550, 250),
            Plataforma(800, 500, 200)
        ],
        'espinhos': [
            # Exemplo de espinhos posicionados sobre a primeira plataforma
            Espinho(200, 540),
            Espinho(300, 540)
        ]
    },
    {
        'nome': 'fase 3',
        'fundo': 'cenario3',
        'plataformas': [
            Plataforma(200, 600, 300),
            Plataforma(700, 500, 200),
            Plataforma(1100, 400, 200)
        ],
        'espinhos': []  # Você pode adicionar espinhos conforme desejar
    }
]

# Funções de interação com o mouse e teclado


def on_mouse_down(pos, button):
    # Converte o valor numérico do botão para uma string
    if button == 1:  # Botão esquerdo
        game.personagem.on_mouse_down(pos, "left")
    elif button == 3:  # Botão direito
        game.personagem.on_mouse_down(pos, "right")


def on_mouse_up(pos, button):
    # Apenas processa o botão direito, conforme o código atual
    if button == 3:
        game.personagem.on_mouse_up(pos, "right")


def on_key_down(key):
    # Alterna o estado de mute ao pressionar a tecla 'M'
    if key == keys.M:
        audio.audio_muted = not audio.audio_muted
        if audio.audio_muted:
            music_bg.stop()  # Para a música de fundo
        else:
            music_bg.play(loops=-1)
            music_bg.set_volume(0.5)


# Instancia o jogo
game = Game(fases)


def update():
    game.update()


def draw():
    game.draw()


pgzrun.go()
