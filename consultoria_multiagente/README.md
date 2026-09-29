# Consultoria Multiagente

Esteira de **4 agentes especializados** para transformar seus dados de funil e
projetos em uma **oferta de consultoria demoável** — útil como produto, portfolio
e acelerador comercial.

## Por que isso impulsiona sua oferta

| Problema do consultor | O que a esteira resolve |
|---|---|
| Oferta genérica demais | Empacota escada Diagnóstico → Sprint → Programa com base no **seu** histórico |
| Discovery lento | Scout qualifica o funil em segundos e aponta leads quentes |
| Precificação no feeling | Estimator calcula preço/hora e risco de abandono |
| Conteúdo comercial improvisado | Narrator gera one-pager, pitch 60s e post LinkedIn |

Na call com o cliente, você **roda a esteira ao vivo** nos dados dele (ou nos
CSVs de demo) e sai com proposta + narrativa — isso vende o método, não só o
resultado.

## Arquitetura

```
tracking.csv ──▶ Scout ────────┐
                               ├─▶ Strategist ─▶ Narrator ─▶ one-pager / pitch / LinkedIn
projects.csv ──▶ Estimator ────┘
```

| Agente | Papel | Entrada |
|---|---|---|
| **Scout** | Qualifica funil, score de maturidade, hot/warm/cold | `tracking.csv` |
| **Estimator** | Preço/hora, faixas, pacotes e risco | `projects.csv` |
| **Strategist** | ICP, posicionamento, escada de oferta | outputs Scout + Estimator |
| **Narrator** | One-pager, pitch 60s, post LinkedIn | outputs anteriores |

Agentes são **determinísticos** (pandas + regras) — rodam sem API key, ideais
para demo comercial. Depois você troca o Narrator/Strategist por LLM se quiser
texto mais livre.

## Como rodar

```bash
cd consultoria_multiagente
pip install -r requirements.txt
python3 main.py
```

Opções:

```bash
python3 main.py --brand "Seu Studio · AI Consulting"
python3 main.py --data-dir .. --output-dir ./outputs
```

Saídas em `outputs/`:

- `relatorio_multiagente.json` — contexto completo da esteira
- `one_pager_oferta.md` — proposta one-pager
- `copys_comerciais.md` — pitch + LinkedIn

## Como usar na consultoria (playbook)

1. **Demo de 15 min** — rode `python main.py` e mostre Scout → Narrator.
2. **Diagnóstico pago** — peça 2 CSVs do cliente (funil + projetos) e rode a esteira.
3. **Upsell** — use a escada gerada (Diagnóstico → Sprint → Programa) na proposta.
4. **Conteúdo** — publique o post LinkedIn gerado e grave o pitch 60s.
5. **Diferenciação** — posicione-se como quem entrega *sistema multiagente*, não slides.

## Extensões naturais

- Trocar Narrator por LLM (OpenAI/Anthropic) mantendo o mesmo contrato `AgentResult`
- Adicionar agente **Compliance** (escopo, aceite, risco jurídico)
- Expor a esteira via API/Streamlit para o cliente acompanhar
- Plug-in CRM: Scout lê leads reais (HubSpot/Sheets) em vez do CSV

## Estrutura

```
consultoria_multiagente/
  main.py              # CLI
  pipeline.py          # Orquestrador
  requirements.txt
  agents/
    base.py            # Contrato AgentResult
    scout.py
    estimator.py
    strategist.py
    narrator.py
  outputs/             # Gerado ao rodar
```
