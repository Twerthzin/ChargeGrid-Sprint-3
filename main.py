from src.config import CONFIG
from src.simulador_solar import SimuladorSolar
from src.simulador_consumo import SimuladorConsumo
from src.gerenciador_bateria import GerenciadorBateria
from src.gerenciador_recarga import GerenciadorRecarga, OrigemEnergia
from src.automacao import AutomacaoEnergetica, Acao
from src.metricas import CalculadoraMetricas
from src.dashboard import Dashboard


def imprimir_cabecalho():
    print("=" * 72)
    print("  SISTEMA INTEGRADO DE GESTÃO ENERGÉTICA - SPRINT 3 FIAP")
    print("  Energia Solar + Automação + Recarga de VE")
    print("=" * 72)


def main():
    imprimir_cabecalho()

    # --- Instanciação dos módulos ---
    solar = SimuladorSolar()
    consumo = SimuladorConsumo()
    bateria = GerenciadorBateria()
    recarga = GerenciadorRecarga()
    automacao = AutomacaoEnergetica()
    metricas = CalculadoraMetricas()
    dashboard = Dashboard()

    leituras_solar = {l.hora: l for l in solar.gerar_leituras()}
    leituras_consumo = {l.hora: l for l in consumo.gerar_leituras()}

    horas = sorted(set(leituras_solar) | set(leituras_consumo))
    geracoes, consumos, baterias_pct = [], [], []
    exportado_total = 0.0
    importado_total = 0.0

    print("\n[EXECUÇÃO DA SIMULAÇÃO HORÁRIA]")
    print("-" * 72)
    print(f"{'Hora':<6} {'Ger(kW)':<10} {'Cons(kW)':<10} {'Bat(%)':<8} {'Ação':<22} {'Justificativa'}")
    print("-" * 72)

    for h in horas:
        g = leituras_solar.get(h).geracao_kw if h in leituras_solar else 0
        c = leituras_consumo.get(h).consumo_kw if h in leituras_consumo else 0

        decisao = automacao.decidir(g, c, bateria.carga_pct, h)


        if decisao.acao == Acao.CARREGAR_VE:
            if not (recarga.sessao_atual and recarga.sessao_atual.ativa):
                recarga.iniciar_sessao(h, OrigemEnergia.SOLAR)
            entregue = recarga.entregar_energia(decisao.potencia_kw, h)

            resto = decisao.potencia_kw - entregue
            if resto > 0:
                bateria.carregar(resto, h)

        elif decisao.acao == Acao.ARMAZENAR_BATERIA:
            bateria.carregar(decisao.potencia_kw, h)

        elif decisao.acao == Acao.IMPORTAR_REDE:
            importado_total += decisao.potencia_kw
            # Tenta cobrir com bateria primeiro
            if bateria.carga_pct > CONFIG.BATERIA_MINIMA:
                bateria.descarregar(decisao.potencia_kw * 0.5, h)

        elif decisao.acao == Acao.SUSPENDER_RECARGA:
            recarga.encerrar_sessao(h)


        baterias_pct.append(round(bateria.carga_pct, 2))
        geracoes.append(round(g, 2))
        consumos.append(round(c, 2))

        print(f"{h:02d}:00  {g:<10.2f} {c:<10.2f} {bateria.carga_pct:<8.1f} "
              f"{decisao.acao.value:<22} {decisao.justificativa}")


    if recarga.sessao_atual and recarga.sessao_atual.ativa:
        recarga.encerrar_sessao(horas[-1])


    m = metricas.calcular(
        total_gerado=solar.total_gerado_kwh(),
        total_consumido=consumo.total_consumido_kwh(),
        total_ve=recarga.bateria_ve_kwh,
        exportado=exportado_total,
        importado=importado_total,
    )

    print("\n" + "=" * 72)
    print("  MÉTRICAS FINAIS")
    print("=" * 72)
    print(f"Energia gerada:            {m.total_gerado_kwh:.2f} kWh")
    print(f"Energia consumida:         {m.total_consumido_kwh:.2f} kWh")
    print(f"Energia recarregada no VE: {m.total_recarregado_ve_kwh:.2f} kWh")
    print(f"Energia importada da rede: {m.energia_importada_kwh:.2f} kWh")
    print(f"Eficiência do sistema:     {m.eficiencia_sistema_pct:.2f}%")
    print(f"CO₂ evitado:               {m.co2_evitado_kg:.3f} kg")
    print(f"Equivalente em árvores:    {m.arvores_equivalentes:.4f} árvores/ano")
    print(f"Economia financeira:       R$ {m.economia_brl:.2f}")

    print(f"\nSessões de recarga registradas: {len(recarga.sessoes)}")
    for s in recarga.sessoes:
        print(f"  - Início {s.hora_inicio:02d}:00 → Fim {s.hora_fim:02d}:00 | "
              f"{s.energia_entregue_kwh:.2f} kWh | Origem: {s.origem.value}")


    caminho = dashboard.grafico_principal(
        horas, geracoes, consumos, automacao.historico, baterias_pct
    )
    print(f"\nGráfico salvo em: {caminho}")

    print("\n" + "=" * 72)
    print("  SIMULAÇÃO CONCLUÍDA COM SUCESSO")
    print("=" * 72)


if __name__ == "__main__":
    main()