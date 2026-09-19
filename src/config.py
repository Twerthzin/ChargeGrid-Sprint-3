from dataclasses import dataclass

@dataclass
class ConfigSistema:

    POTENCIA_PICO_KWP: float = 5.0
    EFICIENCIA_INVERSOR: float = 0.96
    FATOR_PERDA_TEMPERATURA: float = 0.92
    FATOR_SOMBREAMENTO: float = 0.97


    CAPACIDADE_BATERIA_KWH: float = 10.0
    BATERIA_MINIMA: float = 20.0
    BATERIA_MAXIMA: float = 95.0
    EFICIENCIA_CARGA: float = 0.95
    EFICIENCIA_DESCARGA: float = 0.95


    POTENCIA_CARREGADOR_KW: float = 7.0
    CAPACIDADE_BATERIA_VE_KWH: float = 40.0
    EXCEDENTE_MINIMO_VE: float = 2.0


    TARIFA_PONTA: float = 1.20
    TARIFA_FORA_PONTA: float = 0.75
    HORA_INICIO_PONTA: int = 18
    HORA_FIM_PONTA: int = 21


    FATOR_EMISSAO_CO2: float = 0.084
    CO2_POR_ARVORE_ANO: float = 18.0

    HORA_INICIO: int = 6
    HORA_FIM: int = 19
    DIAS_SIMULACAO: int = 1



CONFIG = ConfigSistema()