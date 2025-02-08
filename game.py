import pgzrun
from player import Personagem
from plataformas import Plataforma
from pgzero.actor import Actor
from enemy_NightBorne import Inimigo_NightBorne  # Certifique-se de ter essa classe implementada
import audio  # Importa o módulo de áudio

# Definindo o tamanho da tela
WIDTH = 1200
HEIGHT = 800

# Carregar a música de fundo
music_bg = sounds.background  # Certifique-se de ter o arquivo de som "background" na pasta sounds

class Game:
    def __init__(self, fases):
        self.fases = fases  # Lista de fases
        self.fase_atual = 0  # Inicia na primeira fase
        self.iniciar_fase(self.fase_atual)

    def iniciar_fase(self, fase_idx):
        fase = self.fases[fase_idx]
        plataformas = fase['plataformas']
        fundo = fase['fundo']
        x_inicial = 200  # Exemplo: posição inicial do personagem
        y_inicial = 750

        self.fundo = Actor(fundo)
        self.personagem = Personagem(plataformas, x_inicial, y_inicial)
        self.plataformas = plataformas
        self.inimigos = []  # Lista de inimigos
        self.image_timer = 0
        self.image_interval = 1
        
        # Instancia um inimigo
        inimigo = Inimigo_NightBorne(posicao_inicial_x=500, posicao_inicial_y=500, plataformas=plataformas)
        self.inimigos.append(inimigo)

        # Atribui o inimigo à lista de inimigos do personagem
        self.personagem.enemies = [inimigo]
        inimigo.alvo = self.personagem

        # Inicia a música de fundo, se o áudio não estiver mudo
        if not audio.audio_muted:
            music_bg.play(loops=-1)
            music_bg.set_volume(0.5)

    def mudar_fase(self):
        self.fase_atual += 1
        if self.fase_atual >= len(self.fases):
            self.fase_atual = 0  # Reinicia as fases ou implementa outra lógica
        self.iniciar_fase(self.fase_atual)

    def update(self):
        self.personagem.update()
        self.image_timer += 1 / 60
        if self.image_timer >= self.image_interval:
            self.personagem.update_image()
            self.image_timer = 0

        for inimigo in self.inimigos:
            inimigo.update()

    def draw(self):
        screen.clear()
        self.fundo.draw()  # Desenha o fundo da fase
        for plataforma in self.plataformas:
            plataforma.draw()
        self.personagem.draw()
        for inimigo in self.inimigos:
            inimigo.draw()

# Definição das fases
fases = [
    {
        'nome': 'fase 1',
        'fundo': 'cenario2',
        'plataformas': [Plataforma(95, 350, 100)]
    },
    {
        'nome': 'fase 2',
        'fundo': 'cenario2',
        'plataformas': [
            Plataforma(100, 550, 250),
            Plataforma(500, 550, 200),
            Plataforma(800, 450, 200)
        ]
    },
    {
        'nome': 'fase 3',
        'fundo': 'cenario3',
        'plataformas': [
            Plataforma(200, 600, 300),
            Plataforma(700, 500, 200),
            Plataforma(1100, 400, 200)
        ]
    }
]

def on_mouse_down(pos, button):
    if button == 1:  # Botão esquerdo do mouse
        game.personagem.on_mouse_down()

def on_key_down(key):
    # Alterna o estado de mute ao pressionar a tecla 'M'
    if key == keys.M:
        audio.audio_muted = not audio.audio_muted
        if audio.audio_muted:
            music_bg.stop()  # Para a música de fundo
        else:
            music_bg.play(loops=-1)
            music_bg.set_volume(0.5)

game = Game(fases)

def update():
    game.update()

def draw():
    game.draw()

pgzrun.go()
