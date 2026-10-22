# Inteligência Territorial Aplicada ao Desenvolvimento Regional (ISVT)

Modelo comparativo para 421 municípios prioritários da Bahia (136) e do Rio Grande do Sul (285), com foco na relação entre fomento rural, estrutura turística formal, governança e conectividade.

## Modelo vigente

O Índice Sintético de Viabilidade Territorial utiliza três dimensões:

1. **D1 – Fomento Rural:** crédito rural acumulado no SICOR/BCB entre 2016 e 2025.
2. **D2 – Alojamento e Emprego Turístico Formal:** leitos e estabelecimentos de hospedagem, ocupações formais e estabelecimentos formais, com dados do CADASTUR/MTur e RAIS/MTE.
3. **D3 – Governança e Conectividade:** conselho e órgão de turismo, Plano Diretor, Plano Municipal de Turismo, rede móvel, 4G, 5G e banda larga fixa, com dados do MTur/IBGE e Anatel.

O modelo atual **não utiliza AHP, BNDES, FNE, Airbnb, Waze ou diversidade financeira**. As três dimensões recebem pesos equivalentes.

## Cálculo

Variáveis quantitativas assimétricas são transformadas por:

```text
Y = ln(1 + X)
```

A normalização Min-Max é feita separadamente por UF:

```text
I_m,UF = (Y_m - min(Y_UF)) / (max(Y_UF) - min(Y_UF))
```

O índice final é:

```text
ISVT = (D1 + D2 + D3) / 3
```

## Matriz de Tração Territorial

A Capacidade Territorial e o Gap de Fomento são calculados por:

```text
CT = (D2 + D3) / 2
GF = CT - D1
```

Os pontos de corte são as medianas estaduais de CT e D1:

| Quadrante | CT | D1 | Interpretação |
|---|---|---|---|
| I | Alta | Alto | Estruturado e financiado |
| II | Alta | Baixo | Vazio relativo de fomento |
| III | Baixa | Baixo | Fragilidade territorial e financeira |
| IV | Baixa | Alto | Fomento relativamente elevado |

> A classificação é relativa à distribuição de cada estado. Quadrante II não comprova, isoladamente, demanda reprimida ou racionamento de crédito. D1 = 0,0000 pode representar apenas o mínimo da distribuição normalizada.

## Arquivos de entrada

- `Dados/CodigoIbgeMunicipiosAlvo.csv`
- `Dados/Fomento_Municipal_Anual_WIDE.csv`
- `Dados/municipios_coordenadas.csv`

A integração utiliza o código IBGE municipal padronizado com sete dígitos. O acumulado SICOR usa exclusivamente `vol_2016` a `vol_2025`.

## Pipeline principal

O script Python executa, em uma única rotina:

1. leitura e validação das bases;
2. conversão dos valores monetários do SICOR;
3. soma do crédito rural de 2016–2025;
4. cálculo de D1, D2, D3 e ISVT;
5. cálculo de CT, Gap e quadrantes;
6. estatísticas descritivas, correlação exploratória e rankings;
7. exportação da tabela consolidada;
8. geração do dashboard HTML.

## Saídas

Na pasta `out/` e na raiz do projeto são gerados:

- `index.html` – dashboard interativo;
- `ISVT_Resultado_Final_3Dimensoes.csv` – tabela consolidada;
- `ISVT_Resultado_Final_3Dimensoes.xlsx` – planilha com resultado municipal, resumo por UF, quadrantes, vazios relativos e Top 5 por UF.

## Dashboard

O painel apresenta:

- mapa municipal com popup de D1, D2, D3, ISVT, CT, Gap e quadrante;
- filtros por UF, alto ISVT e quadrantes;
- explicações sobre o ISVT e a Matriz de Tração;
- gráficos comparativos;
- tabela municipal ordenável e pesquisável.

## Interpretação metodológica

A normalização intraestado produz posições relativas. Portanto, os indicadores normalizados não substituem os valores brutos e não devem ser interpretados como comparação direta de montantes absolutos entre Bahia e Rio Grande do Sul. O ISVT e a Matriz de Tração apoiam a priorização territorial e não substituem a análise individual de risco de crédito.
