import pgzrun
from player import Personagem
from plataformas import Plataforma
from pgzero.actor import Actor
from enemy_NightBorne import Inimigo_NightBorne  # Importe a classe do inimigo

# Definindo o tamanho da tela
WIDTH = 1200
HEIGHT = 800

# Carregar os sons
music_bg = sounds.time_for_adventure  # Substitua 'fundo_musical' pelo nome do seu arquivo de música

# Variável para controlar o estado do áudio
audio_muted = False

class Game:
    def __init__(self, fases):
        self.fases = fases  # Lista de fases
        self.fase_atual = 0  # Inicia com a primeira fase
        self.iniciar_fase(self.fase_atual)  # Chama a função de inicialização da fase

    def iniciar_fase(self, fase_idx):
        # Inicializa a fase de acordo com o índice
        fase = self.fases[fase_idx]
        plataformas = fase['plataformas']
        fundo = fase['fundo']
         # Defina as coordenadas iniciais aqui
        x_inicial = 200  # Por exemplo, início no meio da fase
        y_inicial = 750  # Posição no chão

        # Atualiza o fundo e as plataformas
        self.fundo = Actor(fundo)
        self.personagem = Personagem(plataformas, x_inicial, y_inicial)
        self.plataformas = plataformas
        self.inimigos = []  # Lista para armazenar inimigos
        self.image_timer = 0
        self.image_interval = 1
        
        # Instanciando inimigo
        inimigo = Inimigo_NightBorne(posicao_inicial_x=500, posicao_inicial_y=500, plataformas=plataformas)
        self.inimigos.append(inimigo)

        # Iniciar música de fundo
        if not audio_muted:
            music_bg.play(loops=-1)  # Toca a música em loop
            music_bg.set_volume(0.5)  # Ajusta o volume da música

    def mudar_fase(self):
        # Passa para a próxima fase
        self.fase_atual += 1
        if self.fase_atual >= len(self.fases):
            self.fase_atual = 0  # Volta para a primeira fase (ou pode colocar algo como Game Over)
        self.iniciar_fase(self.fase_atual)

    def update(self):
        self.personagem.update()
        self.image_timer += 1 / 60
        if self.image_timer >= self.image_interval:
            self.personagem.update_image()
            self.image_timer = 0

        # Atualiza os inimigos
        for inimigo in self.inimigos:
            inimigo.update()

    def draw(self):
        screen.clear()
        self.fundo.draw()  # Desenha o fundo da fase
        for plataforma in self.plataformas:
            plataforma.draw()
        self.personagem.draw()
        
        # Desenha os inimigos
        for inimigo in self.inimigos:
            inimigo.draw()

# Definindo as fases
fases = [
    {'nome': 'fase 1', 'fundo': 'cenario2', 'plataformas': [
        Plataforma(95, 350,100),
    ]},
    {'nome': 'fase 2', 'fundo': 'cenario2', 'plataformas': [
        Plataforma(100, 550, 250),
        Plataforma(500, 550, 200),
        Plataforma(800, 450, 200)
    ]},
    {'nome': 'fase 3', 'fundo': 'cenario3', 'plataformas': [
        Plataforma(200, 600, 300),
        Plataforma(700, 500, 200),
        Plataforma(1100, 400, 200)
    ]}
]

def on_mouse_down(pos, button):
    if button == 1:  # Botão esquerdo do mouse
        game.personagem.on_mouse_down()  # Chama a função correta

def on_key_down(key):
    global audio_muted
    if key == keys.M:  # Mudar o estado de mute ao pressionar a tecla 'M'
        audio_muted = not audio_muted
        if audio_muted:
            music_bg.stop()  # Para a música de fundo
        else:
            music_bg.play(loops=-1)  # Reinicia a música de fundo
            music_bg.set_volume(0.5)  # Ajusta o volume da música

# Inicializando o jogo
game = Game(fases)

def update():
    game.update()

def draw():
    game.draw()

pgzrun.go()  # Inicializa o Pygame Zero