from dataclasses import dataclass, field
from typing import List

from .config import CONFIG


@dataclass
class EstadoBateria:
    hora: int
    carga_pct: float
    carga_kwh: float
    acao: str
    energia_movimentada: float


class GerenciadorBateria:
    def __init__(self):
        self.config = CONFIG
        self.carga_atual_kwh = self.config.CAPACIDADE_BATERIA_KWH * 0.5
        self.historico: List[EstadoBateria] = []

    @property
    def carga_pct(self) -> float:
        return (self.carga_atual_kwh / self.config.CAPACIDADE_BATERIA_KWH) * 100

    def carregar(self, excedente_kwh: float, hora: int) -> float:

        if self.carga_pct >= self.config.BATERIA_MAXIMA:
            self._registrar(hora, "ociosa", 0)
            return 0.0

        espaco_livre = (
            self.config.CAPACIDADE_BATERIA_KWH
            * (self.config.BATERIA_MAXIMA / 100)
            - self.carga_atual_kwh
        )
        energia_util = min(excedente_kwh * self.config.EFICIENCIA_CARGA, espaco_livre)
        self.carga_atual_kwh += energia_util
        self._registrar(hora, "carregando", energia_util)
        return energia_util

    def descarregar(self, demanda_kwh: float, hora: int) -> float:

        if self.carga_pct <= self.config.BATERIA_MINIMA:
            self._registrar(hora, "ociosa", 0)
            return 0.0

        disponivel = (
            self.carga_atual_kwh
            - self.config.CAPACIDADE_BATERIA_KWH * (self.config.BATERIA_MINIMA / 100)
        )
        energia_util = min(demanda_kwh / self.config.EFICIENCIA_DESCARGA, disponivel)
        self.carga_atual_kwh -= energia_util
        self._registrar(hora, "descarregando", energia_util)
        return energia_util * self.config.EFICIENCIA_DESCARGA

    def _registrar(self, hora: int, acao: str, energia: float):
        self.historico.append(EstadoBateria(
            hora=hora,
            carga_pct=round(self.carga_pct, 2),
            carga_kwh=round(self.carga_atual_kwh, 3),
            acao=acao,
            energia_movimentada=round(energia, 3),
        ))