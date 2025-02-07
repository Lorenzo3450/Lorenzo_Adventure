from pgzero.actor import Actor
from enemy import Inimigo

class Inimigo_NightBorne(Inimigo):
    def __init__(self, posicao_inicial_x, posicao_inicial_y, plataformas):
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
            dano=10,
            posicao_inicial_x=posicao_inicial_x,
            posicao_inicial_y=posicao_inicial_y,
            plataformas=plataformas
        )
