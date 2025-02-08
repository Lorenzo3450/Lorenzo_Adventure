# audio.py

# Variável global para controlar o áudio (True = mudo, False = com áudio)
audio_muted = False

def play_sound(sound, loops=0, **kwargs):
    """
    Toca o som somente se o áudio não estiver mutado.
    Recebe o objeto de som (por exemplo, sounds.jump) e repassa os parâmetros.
    """
    if not audio_muted:
        sound.play(loops=loops, **kwargs)
