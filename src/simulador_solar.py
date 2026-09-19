import math
from dataclasses import dataclass
from typing import List

from .config import CONFIG


@dataclass
class LeituraSolar:
    hora: int
    irradiancia_relativa: float   # 0.0 a 1.0
    geracao_kw: float             # kW instantâneo
    geracao_kwh: float            # kWh no intervalo


class SimuladorSolar:
    def __init__(self):
        self.config = CONFIG
        self.fator_perdas_total = (
            self.config.EFICIENCIA_INVERSOR
            * self.config.FATOR_PERDA_TEMPERATURA
            * self.config.FATOR_SOMBREAMENTO
        )

    def _irradiancia(self, hora: int) -> float:
        """
        Curva gaussiana: pico ao meio-dia (12h), decaimento suave.
        Retorna valor entre 0 e 1.
        """
        if hora < self.config.HORA_INICIO or hora > self.config.HORA_FIM:
            return 0.0
        # Gaussiana centrada em 12h30 com desvio padrão de 3h
        return math.exp(-((hora - 12.5) ** 2) / (2 * 3.0 ** 2))

    def gerar_leituras(self) -> List[LeituraSolar]:
        leituras = []
        for hora in range(self.config.HORA_INICIO, self.config.HORA_FIM + 1):
            irr = self._irradiancia(hora)
            geracao_kw = (
                self.config.POTENCIA_PICO_KWP
                * irr
                * self.fator_perdas_total
            )
            leituras.append(LeituraSolar(
                hora=hora,
                irradiancia_relativa=round(irr, 3),
                geracao_kw=round(geracao_kw, 3),
                geracao_kwh=round(geracao_kw, 3),  # intervalo de 1h
            ))
        return leituras

    def total_gerado_kwh(self) -> float:
        return round(sum(l.geracao_kwh for l in self.gerar_leituras()), 2)