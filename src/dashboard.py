import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


class Dashboard:
    def __init__(self, output_dir: str = "output/graficos"):
        self.output_dir = output_dir
        os.makedirs(self.output_dir, exist_ok=True)

    def grafico_principal(self, horas, geracao, consumo, decisoes, bateria_pct):
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(14, 10), sharex=True)


        ax1.plot(horas, geracao, 'g-o', linewidth=2, markersize=8, label='Geração Solar (kW)')
        ax1.plot(horas, consumo, 'r-s', linewidth=2, markersize=8, label='Consumo (kW)')
        ax1.fill_between(horas, geracao, consumo,
                         where=np.array(geracao) >= np.array(consumo),
                         color='green', alpha=0.25, label='Excedente')
        ax1.fill_between(horas, geracao, consumo,
                         where=np.array(geracao) < np.array(consumo),
                         color='red', alpha=0.25, label='Déficit')
        ax1.set_ylabel('Potência (kW)', fontsize=12)
        ax1.set_title('Balanço Energético Diário', fontsize=14, fontweight='bold')
        ax1.legend(loc='upper right')
        ax1.grid(True, alpha=0.3, linestyle='--')


        for d in decisoes:
            if d.acao.name == "CARREGAR_VE":
                idx = horas.index(d.hora)
                ax1.annotate('VE', (d.hora, geracao[idx]),
                             fontsize=9, fontweight='bold', color='darkgreen',
                             ha='center', va='bottom',
                             bbox=dict(boxstyle='round,pad=0.3',
                                       facecolor='lightgreen',
                                       edgecolor='darkgreen', alpha=0.7))


        ax2.plot(horas, bateria_pct, 'b-^', linewidth=2, markersize=8,
                 label='Carga da Bateria (%)')
        ax2.axhline(y=20, color='red', linestyle='--', alpha=0.6, label='Mínimo (20%)')
        ax2.axhline(y=95, color='orange', linestyle='--', alpha=0.6, label='Máximo (95%)')
        ax2.set_xlabel('Horário', fontsize=12)
        ax2.set_ylabel('Carga (%)', fontsize=12)
        ax2.set_title('Estado do Banco de Baterias', fontsize=14, fontweight='bold')
        ax2.legend(loc='upper right')
        ax2.grid(True, alpha=0.3, linestyle='--')
        ax2.set_ylim(0, 100)

        plt.xticks(horas, [f"{h:02d}:00" for h in horas], rotation=45)
        plt.tight_layout()

        caminho = os.path.join(self.output_dir, "dashboard_energia.png")
        plt.savefig(caminho, dpi=150, bbox_inches='tight')
        plt.close()
        return caminho