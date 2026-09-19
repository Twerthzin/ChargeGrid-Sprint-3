from dataclasses import dataclass

from .config import CONFIG


@dataclass
class MetricasFinais:
    total_gerado_kwh: float
    total_consumido_kwh: float
    total_recarregado_ve_kwh: float
    energia_exportada_kwh: float
    energia_importada_kwh: float
    eficiencia_sistema_pct: float
    co2_evitado_kg: float
    arvores_equivalentes: float
    economia_brl: float


class CalculadoraMetricas:
    def __init__(self):
        self.config = CONFIG

    def calcular(self, total_gerado: float, total_consumido: float,
                 total_ve: float, exportado: float, importado: float) -> MetricasFinais:
        cfg = self.config

        energia_util = min(total_consumido + total_ve, total_gerado)
        if total_gerado > 0:
            eficiencia_bruta = (energia_util / total_gerado) * 100
            eficiencia = eficiencia_bruta * cfg.EFICIENCIA_INVERSOR * cfg.EFICIENCIA_CARGA
        else:
            eficiencia = 0


        co2 = energia_util * cfg.FATOR_EMISSAO_CO2
        arvores = co2 / cfg.CO2_POR_ARVORE_ANO


        economia = energia_util * cfg.TARIFA_FORA_PONTA

        return MetricasFinais(
            total_gerado_kwh=round(total_gerado, 2),
            total_consumido_kwh=round(total_consumido, 2),
            total_recarregado_ve_kwh=round(total_ve, 2),
            energia_exportada_kwh=round(exportado, 2),
            energia_importada_kwh=round(importado, 2),
            eficiencia_sistema_pct=round(eficiencia, 2),
            co2_evitado_kg=round(co2, 3),
            arvores_equivalentes=round(arvores, 4),
            economia_brl=round(economia, 2),
        )