from dataclasses import dataclass
from enum import Enum
from typing import List

from .config import CONFIG


class Acao(Enum):
    CARREGAR_VE = "carregar_veiculo"
    ARMAZENAR_BATERIA = "armazenar_bateria"
    EXPORTAR_REDE = "exportar_rede"
    IMPORTAR_REDE = "importar_rede"
    SUSPENDER_RECARGA = "suspender_recarga"
    OCIOSO = "ocioso"


@dataclass
class Decisao:
    hora: int
    acao: Acao
    justificativa: str
    potencia_kw: float


class AutomacaoEnergetica:
    def __init__(self):
        self.config = CONFIG
        self.historico: List[Decisao] = []

    def decidir(self, geracao_kw: float, consumo_kw: float,
                bateria_pct: float, hora: int) -> Decisao:
        excedente = geracao_kw - consumo_kw
        cfg = self.config


        if cfg.HORA_INICIO_PONTA <= hora <= cfg.HORA_FIM_PONTA:
            return self._registrar(Decisao(
                hora=hora,
                acao=Acao.SUSPENDER_RECARGA,
                justificativa="Horário de pico tarifário (R$ 1,20/kWh)",
                potencia_kw=0.0,
            ))


        if bateria_pct < cfg.BATERIA_MINIMA:
            return self._registrar(Decisao(
                hora=hora,
                acao=Acao.IMPORTAR_REDE,
                justificativa=f"Bateria em {bateria_pct:.1f}% (abaixo de {cfg.BATERIA_MINIMA}%)",
                potencia_kw=max(consumo_kw - geracao_kw, 0),
            ))


        if excedente >= cfg.EXCEDENTE_MINIMO_VE:
            return self._registrar(Decisao(
                hora=hora,
                acao=Acao.CARREGAR_VE,
                justificativa=f"Excedente solar de {excedente:.2f} kW disponível",
                potencia_kw=min(excedente, cfg.POTENCIA_CARREGADOR_KW),
            ))

        if bateria_pct >= cfg.BATERIA_MAXIMA and excedente > 0:
            return self._registrar(Decisao(
                hora=hora,
                acao=Acao.EXPORTAR_REDE,
                justificativa=f"Bateria cheia ({bateria_pct:.1f}%), exportando excedente",
                potencia_kw=excedente,
            ))

        if excedente > 0:
            return self._registrar(Decisao(
                hora=hora,
                acao=Acao.ARMAZENAR_BATERIA,
                justificativa=f"Excedente de {excedente:.2f} kW armazenado",
                potencia_kw=excedente,
            ))


        if excedente < 0:
            return self._registrar(Decisao(
                hora=hora,
                acao=Acao.IMPORTAR_REDE,
                justificativa=f"Déficit de {abs(excedente):.2f} kW coberto pela rede",
                potencia_kw=abs(excedente),
            ))


        return self._registrar(Decisao(
            hora=hora,
            acao=Acao.OCIOSO,
            justificativa="Geração igual ao consumo, sem excedente",
            potencia_kw=0.0,
        ))

    def _registrar(self, d: Decisao) -> Decisao:
        self.historico.append(d)
        return d