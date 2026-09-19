# Justificativa Técnica — Sistema Inteligente de Gestão Energética

**Sprint 3 — FIAP**  
**Disciplina:** Análise de Dados com Python

---

## 1. Contexto e Problema

O crescimento da adoção de veículos elétricos (VEs) e de sistemas fotovoltaicos residenciais cria um novo desafio: **como integrar essas duas tecnologias de forma inteligente**, aproveitando ao máximo a energia solar e evitando consumir da rede em horários de tarifa elevada?

Sem automação, o usuário tende a:
- Carregar o VE em horários aleatórios (inclusive em horário de pico)
- Desperdiçar excedente solar
- Não ter visibilidade sobre o balanço energético da residência

**Nossa solução:** um sistema que **automatiza a decisão** de quando carregar o VE, quando armazenar na bateria e quando importar da rede — tudo baseado em dados em tempo real.

---

## 2. Escolhas Técnicas e Justificativas

### 2.1 Por que Python?

| Critério | Justificativa |
|---|---|
| **Aderência à disciplina** | Python é a linguagem-base da disciplina de Análise de Dados |
| **Ecossistema científico** | pandas, numpy e matplotlib formam o tripé padrão da área |
| **Legibilidade** | Código limpo, ideal para documentação e apresentação |
| **Integração com IoT** | Bibliotecas como `pyserial` e `paho-mqtt` permitiriam conectar a hardware real |
| **Zero custo** | Open-source, sem licenças |

### 2.2 Por que `dataclasses`?

Usamos `@dataclass` para modelar entidades como `LeituraSolar`, `Decisao`, `SessaoRecarga` e `EstadoBateria`.

**Vantagens:**
- Código **auto-documentado** (os tipos ficam explícitos)
- Menos boilerplate que classes tradicionais
- Facilita testes e manutenção
- Alinhado com **boas práticas modernas de Python (PEP 557)**

### 2.3 Por que `enum` para Ações?

As decisões da automação são representadas por um `Enum` (`Acao.CARREGAR_VE`, `Acao.SUSPENDER_RECARGA`, etc.).

**Vantagens:**
- Evita erros de digitação (nada de strings soltas como `"carregar"`)
- Permite autocomplete na IDE
- Torna o código **à prova de refatoração**
- Boa prática de **programação orientada a tipos**

### 2.4 Por que modularizar em 8 arquivos?

Cada módulo tem **uma única responsabilidade** (princípio SRP — *Single Responsibility Principle*):

| Arquivo | Responsabilidade única |
|---|---|
| `config.py` | Centralizar parâmetros |
| `simulador_solar.py` | Gerar dados de geração |
| `simulador_consumo.py` | Gerar dados de consumo |
| `gerenciador_bateria.py` | Controlar estado da bateria |
| `gerenciador_recarga.py` | Gerenciar sessões do VE |
| `automacao.py` | Tomar decisões |
| `metricas.py` | Calcular KPIs |
| `dashboard.py` | Visualizar dados |

**Vantagens:**
- **Testável:** cada módulo pode ser testado isoladamente
- **Substituível:** trocar o simulador solar por uma API real não afeta o resto
- **Escalável:** adicionar novos componentes é trivial
- **Didático:** facilita a explicação no vídeo

### 2.5 Por que simulação em vez de hardware?

Optamos por **simulação** pelos seguintes motivos:

| Motivo | Detalhe |
|---|---|
| **Acessibilidade** | Todos os integrantes podem rodar em qualquer máquina |
| **Reprodutibilidade** | Resultados idênticos a cada execução |
| **Segurança** | Sem risco de choque elétrico ou danos a equipamentos |
| **Custo zero** | Sem necessidade de painéis, baterias ou VEs reais |
| **Foco na lógica** | O objetivo é demonstrar **a automação e a análise**, não a eletrônica |

> **Importante:** o código foi projetado para ser **facilmente adaptável** a hardware real. Basta substituir os simuladores por leituras de sensores (ex.: INA219 via I²C, API de inversor solar) — a automação e as métricas continuam funcionando sem alteração.

### 2.6 Por que a tarifa diferenciada (ponta vs. fora-ponta)?

Modelamos duas tarifas com base em **tarifas reais brasileiras** (ANEEL):

- **Ponta (18h–21h):** R$ 1,20/kWh
- **Fora-ponta:** R$ 0,75/kWh

Isso permite que o sistema demonstre **economia real**, evitando a rede em horário caro — comportamento típico de sistemas de **demand response**.

---

## 3. Modelagem Matemática

### 3.1 Geração solar — curva gaussiana

A irradiância solar ao longo do dia segue uma distribuição aproximadamente gaussiana, centrada no meio-dia solar:

$$
I(h) = \exp\left(-\frac{(h - 12{,}5)^2}{2 \cdot 3^2}\right)
$$

A geração instantânea é:

$$
P_{solar}(h) = P_{pico} \cdot I(h) \cdot \eta_{inv} \cdot \eta_{temp} \cdot \eta_{somb}
$$

Onde:
- $P_{pico} = 5\,\text{kWp}$
- $\eta_{inv} = 0{,}96$ (inversor)
- $\eta_{temp} = 0{,}92$ (temperatura)
- $\eta_{somb} = 0{,}97$ (sombreamento)

**Justificativa:** modelos gaussianos são usados em softwares profissionais (PVsyst, SAM) para estimar geração horária.

### 3.2 Eficiência do sistema

$$
\eta_{sistema} = \frac{\min(E_{consumo} + E_{VE},\ E_{gerado})}{E_{gerado}} \cdot \eta_{inv} \cdot \eta_{carga} \cdot 100\%
$$

Resultado obtido: **91,20%** — valor dentro da faixa realista de sistemas fotovoltaicos residenciais (85%–93%).

### 3.3 CO₂ evitado

$$
CO_2 = E_{útil} \times 0{,}084\ \text{kg/kWh}
$$

**Fator de emissão:** 0,084 kg CO₂/kWh (média do Sistema Interligado Nacional — SIN, fonte MCTI).

### 3.4 Economia financeira

$$
\text{Economia} = E_{útil} \times \text{tarifa}_{fora\text{-}ponta}
$$

Usamos a tarifa fora-ponta por ser conservador (a energia solar substitui principalmente consumo diurno).

---

## 4. Lógica de Automação

### 4.1 Prioridades (ordem importa)

1. **Segurança da bateria** → não descarregar abaixo de 20%
2. **Economia** → nunca importar da rede no horário de pico (se evitável)
3. **Sustentabilidade** → usar energia solar sempre que possível
4. **Conveniência** → carregar VE quando houver excedente

### 4.2 Por que 6 regras em cascata?

Regras em cascata (**if/elif encadeados**) são:
- **Previsíveis:** fácil explicar por que cada decisão foi tomada
- **Auditáveis:** cada ação vem com uma justificativa textual registrada
- **Extensíveis:** adicionar uma nova regra não quebra as existentes
- **Alinhadas com sistemas especialistas** (usados em SCADA industrial)

Alternativas como machine learning seriam **overkill** para este escopo e dificultariam a explicabilidade — que é um requisito do projeto.

---

## 5. Resultados e Validação

### 5.1 Coerência física
- Curva solar com pico ao meio-dia ✅
- Bateria nunca atingiu limites críticos (< 20% ou > 95%) ✅
- Sessão de recarga ocorreu apenas em horário com sol ✅
- Recarga suspensa automaticamente às 18h (pico) ✅

### 5.2 Coerência econômica
- Importação da rede ocorreu apenas quando necessário ✅
- Economia diária de R$ 23,70 → projeção de ~R$ 8.650/ano ✅
- Valor compatível com sistemas fotovoltaicos residenciais reais ✅

### 5.3 Coerência ambiental
- 2,65 kg CO₂ evitado/dia → ~969 kg/ano ✅
- Equivalente a ~54 árvores/ano ✅
- Valor coerente com metodologia GHG Protocol ✅



---

## 6. Referências Técnicas

- **ANEEL** — Resolução Normativa nº 482/2012 (geração distribuída)
- **INMET** — Dados de irradiância solar para a região Sudeste
- **MCTI** — Fatores de emissão do Sistema Interligado Nacional
- **PEP 557** — Data Classes (Python Enhancement Proposal)
- **ABVE** — Associação Brasileira do Veículo Elétrico
- **GHG Protocol** — Metodologia de contabilização de emissões

---

**Documento elaborado pela equipe — Sprint 3 FIAP — 2026**