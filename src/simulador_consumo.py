from dataclasses import dataclass
from typing import List

from .config import CONFIG


@dataclass
class LeituraConsumo:
    hora: int
    consumo_kw: float
    consumo_kwh: float


class SimuladorConsumo:
    def __init__(self):
        self.config = CONFIG

        self._perfil_base = {
            6: 1.8, 7: 2.0, 8: 1.5, 9: 1.2, 10: 1.0,
            11: 1.1, 12: 1.3, 13: 1.2, 14: 1.1, 15: 1.0,
            16: 1.2, 17: 1.5, 18: 2.2, 19: 2.5,
        }

    def gerar_leituras(self) -> List[LeituraConsumo]:
        leituras = []
        for hora in range(self.config.HORA_INICIO, self.config.HORA_FIM + 1):
            consumo = self._perfil_base.get(hora, 1.0)
            leituras.append(LeituraConsumo(
                hora=hora,
                consumo_kw=round(consumo, 3),
                consumo_kwh=round(consumo, 3),
            ))
        return leituras

    def total_consumido_kwh(self) -> float:
        return round(sum(l.consumo_kwh for l in self.gerar_leituras()), 2)
