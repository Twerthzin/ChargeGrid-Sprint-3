from dataclasses import dataclass, field
from typing import List, Optional
from enum import Enum

from .config import CONFIG


class OrigemEnergia(Enum):
    SOLAR = "solar"
    BATERIA = "bateria"
    REDE = "rede"


@dataclass
class SessaoRecarga:
    hora_inicio: int
    hora_fim: Optional[int] = None
    energia_entregue_kwh: float = 0.0
    origem: OrigemEnergia = OrigemEnergia.SOLAR
    potencia_media_kw: float = 0.0
    ativa: bool = False


class GerenciadorRecarga:
    def __init__(self):
        self.config = CONFIG
        self.sessoes: List[SessaoRecarga] = []
        self.sessao_atual: Optional[SessaoRecarga] = None
        self.bateria_ve_kwh = 0.0  # estado do VE

    def iniciar_sessao(self, hora: int, origem: OrigemEnergia):
        if self.sessao_atual and self.sessao_atual.ativa:
            return
        self.sessao_atual = SessaoRecarga(hora_inicio=hora, origem=origem, ativa=True)
        self.sessoes.append(self.sessao_atual)

    def entregar_energia(self, potencia_kw: float, hora: int) -> float:

        if not self.sessao_atual or not self.sessao_atual.ativa:
            return 0.0

        espaco_ve = self.config.CAPACIDADE_BATERIA_VE_KWH - self.bateria_ve_kwh
        if espaco_ve <= 0:
            self.encerrar_sessao(hora)
            return 0.0

        potencia_efetiva = min(potencia_kw, self.config.POTENCIA_CARREGADOR_KW)
        energia = min(potencia_efetiva, espaco_ve)

        self.bateria_ve_kwh += energia
        self.sessao_atual.energia_entregue_kwh += energia
        return energia

    def encerrar_sessao(self, hora: int):
        if self.sessao_atual and self.sessao_atual.ativa:
            self.sessao_atual.ativa = False
            self.sessao_atual.hora_fim = hora
            duracao = hora - self.sessao_atual.hora_inicio
            if duracao > 0:
                self.sessao_atual.potencia_media_kw = (
                    self.sessao_atual.energia_entregue_kwh / duracao
                )
            self.sessao_atual = None

    @property
    def carga_ve_pct(self) -> float:
        return (self.bateria_ve_kwh / self.config.CAPACIDADE_BATERIA_VE_KWH) * 100