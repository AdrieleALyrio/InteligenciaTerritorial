# Inteligência Territorial Aplicada ao Desenvolvimento Regional (ISVT)
## Identificação de clusters de ecoturismo, economia comunitária e diversificação produtiva para direcionamento estratégico de recursos de desenvolvimento

Este repositório documenta de forma exaustiva o desenvolvimento do modelo de **Inteligência Territorial** para o cálculo do **Índice Sintético de Viabilidade Territorial (ISVT)**. O projeto realiza uma análise comparativa e espacial de duas realidades macroeconômicas brasileiras distintas: os estados da **Bahia (BA)** e do **Rio Grande do Sul (RS)**, buscando identificar "vazios de fomento" e polos com viabilidade para o turismo de base comunitária, ecoturismo e agricultura familiar.

---

## 🗺️ Estrutura do Índice Sintético (ISVT)

O ISVT é calculado a partir de um modelo de **Análise Multicritério** integrado a Sistemas de Informação Geográfica (SIG), baseado em três dimensões principais de dados:

1. **Fomento Rural:** Crédito rural acumulado no SICOR/BCB entre 2016 e 2025.
2. **Alojamento e Emprego Turístico Formal:** Leitos e estabelecimentos de hospedagem, ocupações formais e estabelecimentos formais, com dados do CADASTUR/MTur e RAIS/MTE.
3. **Governança e Conectividade:** Conselho e órgão de turismo, Plano Diretor, Plano Municipal de Turismo, rede móvel, 4G, 5G e banda larga fixa, com dados do MTur/IBGE e Anatel.


---

## 🌍 ETAPA 0: Engenharia de Dados Espaciais & Geoprocessamento no QGIS (SICOR)

Antes da modelagem estatística no Python, os dados espaciais brutos de glebas do **SICOR (Sistema de Operações do Crédito Rural e do Proagro)** passaram por um rigoroso processo de engenharia espacial no QGIS para garantir a consistência geométrica e a correta associação das bases de dados. 

Abaixo está o roteiro passo a passo do fluxo metodológico executado:

### 1. Recorte e Filtros Regionais
* **Ação:** Coleta das malhas municipais do IBGE para o Rio Grande do Sul (RS) e Bahia (BA) e filtragem das bases de operações do SICOR para manter apenas os dados correspondentes aos dois estados de interesse (códigos de UF `43` e `29`, respectivamente).

### 2. Consolidação Temporal (Mesclagem)
* **Ação:** Utilização da ferramenta **Mesclar Camadas Vetoriais** (*Merge Vector Layers*) no QGIS para unificar os 11 anos de arquivos espaciais brutos de glebas (série histórica de 2016 a 2026) em um único mapa unificado de geometrias históricas.
* **Aprendizado Técnico:** A mesclagem gera uma camada temporária de memória (indicada pelo ícone de chip eletrônico no QGIS). Essa camada não é editável diretamente e o provedor impede a criação física de novas colunas de atributos.
* **Solução:** Exportar a camada mesclada temporária como um arquivo físico permanente no formato **GeoPackage (`.gpkg`)**, com o Sistema de Referência de Coordenadas (SRC) definido estritamente como **SIRGAS 2000 (EPSG:4674)**.

### 3. Saneamento Topológico
* **Ação:** Execução do algoritmo **Corrigir Geometrias** (*Fix Geometries*) nas glebas históricas mescladas.
* **Motivo:** As glebas cadastradas no SICOR frequentemente contêm imperfeições topológicas (auto-intersecções, vértices duplicados ou polígonos abertos) decorrentes de erros de digitalização em campo. Essas imperfeições corrompem e travam análises espaciais avançadas de proximidade, área e sobreposição geométrica.

### 4. Criação da Chave Composta de Ligação (Join)
* **Desafio Técnico 1 (Limite de Caracteres):** Inicialmente, tentou-se criar a coluna `chave_composta`. Contudo, o formato de arquivo antigo (Shapefile) trunca automaticamente qualquer campo com mais de 10 caracteres no cabeçalho do arquivo `.dbf`, gerando erros sistemáticos de gravação e perda de estrutura.
  * **Solução:** Adotar o formato moderno e performático **GeoPackage** e reduzir o nome do atributo de ligação simplesmente para `chave`.
* **Desafio Técnico 2 (Chave Composta e Valores Nulos):** O identificador `id_referencia_bacen` não é estritamente único no SICOR, pois uma mesma operação de crédito agrícola pode possuir múltiplas glebas espaciais (diferenciadas pelo número da ordem da gleba, ex: 1, 2, 3...). Fazer um *Join* convencional utilizando apenas o ID de referência corrompe a correspondência espacial 1-para-muitos. Ademais, tentativas iniciais de concatenação simples resultaram em valores inteiramente `NULL` devido à incompatibilidade de tipos de dados (tentativa de concatenar números como string diretamente).
  * **Solução:** Configurar a coluna `chave` como o tipo **Texto (string)** na Calculadora de Campo e utilizar uma expressão de concatenação robusta e imune a tipos numéricos:
    ```sql
    concat(to_string("id_referencia_bacen"), '_', to_string("nu_ordem"))
    ```
    *(Nota metodológica: Caso a coluna de ordem da camada de glebas esteja nomeada de forma diferente no arquivo de origem, como `numero_ordem` ou `nu_seq_gleba`, a expressão foi adaptada em conformidade).*

---

## 🏛️ ETAPA 1: Dimensão 1 - Fomento Financeiro (SICOR )

A modelagem matemática e estatística da Dimensão 1 foi totalmente reestruturada para o ambiente do **Google Colab**, assegurando que os cálculos financeiros fossem baseados em dados reais, auditáveis e metodologicamente validados.

### 1. Separação Científica entre "Finance" vs. "Funding"
Apoiando-se na teoria macroeconômica pós-keynesiana (Studart, 1993/1995; Paula et al., 2023), diferenciamos a provisão de liquidez de curto prazo para custeio agropecuário (*Finance*), capturada nas contratações do **SICOR/BACEN**, dos fluxos estáveis de investimento de longo prazo (*Funding*), representados pelos desembolsos do **BNDES**.
* Centros urbanos e municípios industriais polos tendem a concentrar recursos do BNDES, enquanto as regiões rurais voltadas à agricultura familiar e circuitos de ecoturismo captam volumes expressivos via SICOR. Cruzar ambos resulta na verdadeira **Densidade de Capital** do território.

### 2. Implementação Rigorosa do AHP de Saaty
Para afastar a crítica de adoção de pesos arbitrários, o pipeline calcula e valida de forma integrada a matriz de comparação paritária do **Processo de Hierarquia Analítica (AHP)**:
* **Matriz de Julgamento Paritário (3x3):** Definida com base na capilaridade local (Crédito Rural > Fomento Regional > Diversidade).
* **Validação de Consistência:** O código calcula os autovalores e autovetores, extraindo a Razão de Consistência ($CR \approx 0.03 < 0.10$), provando cientificamente a coerência dos pesos:
  * 🌾 **Crédito Rural (ind_sicor):** `0.5000` (~50% do peso)
  * 🏦 **Fomento Regional (ind_fomento):** `0.4000` (~40% do peso)
  * 🔄 **Diversidade Financeira (ind_diversidade):** `0.1000` (~10% do peso)

### 3. Mitigação de Outliers via Log-Transform ($np.log1p$)
Devido à profunda **Heterogeneidade Estrutural** (conceito clássico da CEPAL formulado por Aníbal Pinto), municípios polo concentram volumes bilionários de crédito, o que esmagaria a escala de pontuação de pequenos municípios turísticos ou agrícolas na normalização linear. 
* A aplicação da transformação logarítmica natural ($np.log1p$) estabiliza a variância dos dados, eliminando o efeito distorcido dos outliers extremos e resgatando a sensibilidade analítica para as pequenas localidades do interior.

### 4. Correção do Viés Regional (A Eliminação do FNE)
Dado que os fundos constitucionais regionais (como o FNE) atuam exclusivamente na Bahia, incluir o FNE na comparação direta penalizaria de forma artificial os municípios do Rio Grande do Sul. 
* Para solucionar este viés federativo, o pipeline implementa a **Normalização Min-Max Intra-Estado (groupby por UF)**. Os indicadores de fomento são normalizados primeiro dentro da "régua" de cada estado antes de serem ponderados pelo AHP, garantindo uma comparação justa, equilibrada e cientificamente comparável.

### 5. Engenharia e Higienização de Dados Offline (A Otimização de RAM)
Para evitar instabilidades de conexões externas e exigências de contas de faturamento no BigQuery, o pipeline opera de forma **100% offline** lendo o CSV massivo unificado de desembolsos do BNDES (719.6 MB) por meio de uma estratégia de **carregamento em blocos (*Chunking*)**:
* **Leitura em Fluxo:** O Pandas lê o arquivo massivo em pedaços de 100.000 linhas, descartando instantaneamente as linhas e colunas que não pertencem aos estados da Bahia e RS ou ao ano de análise. O consumo de RAM é reduzido de 2 GB para menos de 50 MB.
* **Tratamento de Aspas Silenciosas (`csv.QUOTE_NONE`):** Para evitar erros de quebra de leitura em aspas simples ou duplas não fechadas (como na linha `132.842` do CSV do governo), o interpretador ignora as aspas durante o parse.
* **Higienização Activa de Strings:** O script higieniza os valores em tempo real, removendo aspas extras que faziam valores como `'BA'` serem lidos incorretamente como `'\"BA\"'`, o que anteriormente gerava tabelas e resultados vazios.

---

## 📂 Organização dos Arquivos de Código

O repositório está estruturado em frentes coordenadas de trabalho:

### Engenharia de Dados (Local / VS Code)
* `processamento_local_sicor_v6.py`: Limpa, georreferencia e unifica as bases de dados anuais do SICOR do Banco Central de 2016 a 2026, gerando o arquivo otimizado `Fomento_Municipal_Anual_WIDE.csv`.

### Modelagem, Análise e Cartografia (Google Colab / Nuvem)
* `analise_isvt_dimensao1_revisada_v16.py`: O pipeline definitivo e blindado para a Dimensão 1. Realiza o cálculo matemático do AHP de Saaty, processa offline em blocos o CSV gigante do BNDES, remove aspas e ruídos estruturais, calcula o Índice de Fomento Final (`IF_final`), plota os mapas coropléticos integrados, exporta relatórios de estatísticas reais descritivas e salva as saídas em **PNG de alta resolução (300 DPI)** e **PDF Vetorial** para inserção imediata no Word.
* `analise_isvt_dimensao2_colab.py`: Processamento espacial da Dimensão 2 (Demanda Digital / Airbnb). Realiza o cruzamento geométrico de pontos (*listings*) e polígonos municipais (*Spatial Join*) com tratamento de distorção de variância.


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

## 📖 Fundamentação Teórica de Suporte Acadêmico

| Conceito / Indicador | Linha Teórica de Suporte | Autores de Referência | Aplicação no TCC |
| :--- | :--- | :--- | :--- |
| **Finance vs. Funding** | Teoria Monetária da Produção | Keynes (1937), Studart (1995), Paula et al. (2023) | Justifica a diferenciação de peso e tratamento entre crédito de curto prazo de varejo (SICOR) e investimento estável de longo prazo (BNDES). |
| **Heterogeneidade Estrutural** | Teoria do Subdesenvolvimento CEPALina | Aníbal Pinto, Celso Furtado, Raúl Prebisch | Fundamenta estatisticamente o uso do log-transform ($np.log1p$) e da normalização intra-estado para captar disparidades em territórios periféricos. |
| **Intervenção do Estado** | Papel dos Bancos de Desenvolvimento | Araújo (2018), Fochezatto (2026), BNDES | Sustenta teoreticamente o fomento regional de longo prazo como canal essencial de correção de assimetrias espaciais de fomento. |
| **Análise Espacial (SIG)** | Primeira Lei da Geografia / Autocorrelação | Tobler (1970), Luc Anselin (LISA), PySAL | Embasamento cartográfico para o uso de Geopandas, correção topológica de geometrias de glebas e futura análise de clusters de ecoturismo. |

---
*Documentação de Progresso Metodológico revisada, atualizada e consolidada com o mais rigoroso padrão acadêmico em agosto de 2026.*
