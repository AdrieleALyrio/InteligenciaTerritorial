import os, sys, json, shutil
from pathlib import Path
import numpy as np
import pandas as pd

def executar_gerador_html():
    print("Processando matriz oficial do ISVT para o Dashboard...")

    diretorio_projeto = Path(__file__).resolve().parent.parent
    caminho_alvo = diretorio_projeto / "Dados" / "CodigoIbgeMunicipiosAlvo.csv"

    if not caminho_alvo.exists():
        raise FileNotFoundError(f"Arquivo mestre não encontrado: {caminho_alvo}")

    df_base = pd.read_csv(caminho_alvo, sep=None, engine="python", encoding="utf-8-sig")
    df_base.columns = df_base.columns.str.strip().str.replace("\ufeff", "")

    col_ibge = "Codigo_IBGE" if "Codigo_IBGE" in df_base.columns else "Código Município"
    col_mun = "Nome_Municipio_IBGE" if "Nome_Municipio_IBGE" in df_base.columns else "Nome Município"
    col_uf = "uf" if "uf" in df_base.columns else "UF"

    def normalizar_codigo_ibge(series):
        return (
            series.astype("string")
            .str.strip()
            .str.replace(r"\.0$", "", regex=True)
            .str.replace(r"\D", "", regex=True)
            .str.zfill(7)
        )

    df_base["_codigo_ibge"] = normalizar_codigo_ibge(df_base[col_ibge])
    df_base = df_base[df_base["_codigo_ibge"].str.len() == 7].copy()

    cols_ficticias = ["densidade_anuncios_airbnb", "quantidade_anuncios", "preco_medio_diaria"]
    cols_remover = [c for c in cols_ficticias if c in df_base.columns]
    if cols_remover:
        df_base = df_base.drop(columns=cols_remover)

    caminho_sicor = diretorio_projeto / "Dados" / "Fomento_Municipal_Anual_WIDE.csv"
    if not caminho_sicor.exists():
        raise FileNotFoundError(f"Arquivo SICOR/BCB não encontrado: {caminho_sicor}")

    df_sicor = pd.read_csv(
    caminho_sicor,
    sep=";",
    encoding="utf-8",
    dtype=str
)
    print("\n=== COLUNAS LIDAS DO CSV ===")

    for i, col in enumerate(df_sicor.columns):
        print(i, repr(col))

    print("===========================\n")
    col_sicor_code = "cod_municipio" if "cod_municipio" in df_sicor.columns else "Codigo_IBGE"
    # --------------------------------------------------------------------------
    # CREDITO RURAL SICOR/BCB - ACUMULADO DE 2016 A 2025
    # --------------------------------------------------------------------------

    anos_credito = range(2016, 2026)
    colunas_credito = [f"vol_{ano}" for ano in anos_credito]

    colunas_faltantes = [
        col for col in colunas_credito
        if col not in df_sicor.columns
    ]
    print("COLUNAS ESPERADAS:")
    print(colunas_credito)

    print("\nCOLUNAS FALTANTES:")
    print(colunas_faltantes)
    if colunas_faltantes:
        raise ValueError(
            "A base SICOR/BCB não contém todas as colunas necessárias "
            f"para o período 2016-2025. Faltando: {colunas_faltantes}"
        )

    df_sicor["_codigo_ibge"] = normalizar_codigo_ibge(
        df_sicor[col_sicor_code]
    )

        # --------------------------------------------------------------------------
    # CONVERSAO SEGURA DOS VALORES MONETARIOS DO SICOR
    # --------------------------------------------------------------------------

    def converter_valor_sicor(series):

        valores = (
            series
            .astype("string")
            .str.strip()
            .str.replace("R$", "", regex=False)
            .str.strip()
        )

        # Valores que representam ausência de crédito no arquivo
        valores = valores.replace({
            "-": pd.NA,
            "": pd.NA,
            "nan": pd.NA,
            "NaN": pd.NA,
            "None": pd.NA
        })

        # Formato brasileiro:
        # 1.234.567,89  ->  1234567.89
        valores = (
            valores
            .str.replace(".", "", regex=False)
            .str.replace(",", ".", regex=False)
        )

        return pd.to_numeric(
            valores,
            errors="coerce"
        ).fillna(0.0)


    # Converter 2016-2025
    for col in colunas_credito:

        df_sicor[col] = converter_valor_sicor(
            df_sicor[col]
        )

    # Soma o crédito rural de 2016 a 2025 para cada linha/município
    df_sicor["credito_rural_acumulado_2016_2025"] = (
        df_sicor[colunas_credito].sum(axis=1)
    )
        # ============================================================
    # DIAGNOSTICO DO ACUMULADO SICOR
    # ============================================================

    codigos_teste = [
        "2917359",  # Jaborandi
        "2909307",  # Correntina
        "4320800",  # Soledade
        "4307609",  # Estancia Velha
    ]

    print("\n" + "=" * 100)
    print("DIAGNOSTICO DO CREDITO RURAL 2016-2025")
    print("=" * 100)

    for codigo in codigos_teste:

        teste = df_sicor[
            df_sicor["_codigo_ibge"] == codigo
        ]

        if teste.empty:
            print(f"\nCódigo {codigo}: NÃO ENCONTRADO")
            continue

        for _, linha in teste.iterrows():

            print(f"\nCODIGO IBGE: {codigo}")

            total_manual = 0.0

            for ano in range(2016, 2026):

                coluna = f"vol_{ano}"
                valor = float(linha[coluna])

                total_manual += valor

                valor_formatado = (
                    f"{valor:,.2f}"
                    .replace(",", "X")
                    .replace(".", ",")
                    .replace("X", ".")
                )

                print(
                    f"{ano}: R$ {valor_formatado}"
                )

                total_formatado = (
                    f"{total_manual:,.2f}"
                    .replace(",", "X")
                    .replace(".", ",")
                    .replace("X", ".")
                )

                print("-" * 60)

                print(
                    f"SOMA 2016-2025: R$ {total_formatado}"
                )

            print("-" * 60)

            print(
                f"SOMA 2016-2025: "
                f"R$ {total_manual:,.2f}"
            )

            print(
                f"ACUMULADO CALCULADO PELO SCRIPT: "
                f"R$ {linha['credito_rural_acumulado_2016_2025']:,.2f}"
            )

            print(
                f"LN(1 + acumulado): "
                f"{np.log1p(total_manual):.12f}"
            )

    print("\n" + "=" * 100)
    # Mantém somente código IBGE + acumulado
    df_sicor_sub = df_sicor[
        ["_codigo_ibge", "credito_rural_acumulado_2016_2025"]
    ].copy()

    # Segurança para o caso de existir mais de uma linha para o mesmo município
    df_sicor_sub = (
        df_sicor_sub
        .groupby("_codigo_ibge", as_index=False)[
            "credito_rural_acumulado_2016_2025"
        ]
        .sum()
    )

        # --------------------------------------------------------------------------
    # JUNTA A BASE SICOR COM A BASE PRINCIPAL
    # --------------------------------------------------------------------------

    df_base = df_base.merge(
        df_sicor_sub,
        on="_codigo_ibge",
        how="left"
    )

    # --------------------------------------------------------------------------
    # VERIFICA MUNICIPIOS SEM CORRESPONDENCIA NO SICOR
    # --------------------------------------------------------------------------

    sem_correspondencia_sicor = (
        df_base["credito_rural_acumulado_2016_2025"].isna()
    )

    qtd_sem_correspondencia = sem_correspondencia_sicor.sum()

    print(
        "\nMunicipios sem correspondencia SICOR:",
        qtd_sem_correspondencia
    )

    if qtd_sem_correspondencia > 0:

        print("\n=== MUNICIPIOS SEM CORRESPONDENCIA SICOR ===")

        print(
            df_base.loc[
                sem_correspondencia_sicor,
                [col_ibge, col_mun, col_uf]
            ].to_string(index=False)
        )

        print("==========================================\n")

        raise ValueError(
            "Existem municipios da base principal sem correspondencia "
            "na base SICOR. Corrija o merge antes de calcular D1."
        )

    # --------------------------------------------------------------------------
    # VARIAVEL UTILIZADA NA DIMENSAO 1
    # --------------------------------------------------------------------------

    df_base["Credito_Rural_BCB"] = (
        df_base["credito_rural_acumulado_2016_2025"]
    )

    print(
        "OK - Todos os municipios possuem correspondencia "
        "na base SICOR."
    )

    cols_numericas = [
        "Renda Per Capita", "Receita Tributária", "Participação Investimentos",
        "Densidade Leitos Hospedagem", "Densidade Estabelecimentos Hospedagem",
        "Ocup Formais", "Estab Formais", "Conselho Turismo", "Órgão Turismo",
        "Plano Diretor", "Plano Município Turismo", "Part Rede Móvel", "Part Rede 4G", "Part Rede 5G", "Densidade Banda Fixa"
    ]

    def converter_numerico(series):
        valores = series.astype("string").str.strip()
        possui_virgula = valores.str.contains(",", na=False)
        valores.loc[possui_virgula] = (
            valores.loc[possui_virgula]
            .str.replace(".", "", regex=False)
            .str.replace(",", ".", regex=False)
        )
        return pd.to_numeric(valores, errors="coerce").fillna(0.0)

    for col in cols_numericas + ["Credito_Rural_BCB"]:
        if col in df_base.columns:
            df_base[col] = converter_numerico(df_base[col])

    def min_max_uf(series):
        s_min, s_max = series.min(), series.max()
        if s_max == s_min:
            return pd.Series(0.0, index=series.index)
        return (series - s_min) / (s_max - s_min)

    # --------------------------------------------------------------------------
    # FORMULAS ECONOMETRICAS EXATAS DO COLAB
    # --------------------------------------------------------------------------

    # D1: Log-Transform do Credito Rural (SICOR) + MinMax por UF
    df_base["log_d1"] = np.log1p(np.maximum(0, df_base["Credito_Rural_BCB"]))
    df_base["ind_d1"] = df_base.groupby(col_uf)["log_d1"].transform(min_max_uf)
        # ============================================================
    # MEMORIA DE CALCULO D1
    # ============================================================

    df_base["min_log_d1_uf"] = (
        df_base.groupby(col_uf)["log_d1"]
        .transform("min")
    )

    df_base["max_log_d1_uf"] = (
        df_base.groupby(col_uf)["log_d1"]
        .transform("max")
    )

    print("\n" + "=" * 80)
    print("MEMORIA DE CALCULO D1")
    print("=" * 80)

    for estado in sorted(df_base[col_uf].dropna().unique()):

        df_estado = df_base[df_base[col_uf] == estado]

        idx_min = df_estado["log_d1"].idxmin()
        idx_max = df_estado["log_d1"].idxmax()

        print(f"\nUF: {estado}")

        print("\nMINIMO:")
        print(
            f"Municipio: {df_base.loc[idx_min, col_mun]}"
        )
        print(
            f"Credito Rural: "
            f"{df_base.loc[idx_min, 'Credito_Rural_BCB']:,.2f}"
        )
        print(
            f"LN(1 + Credito): "
            f"{df_base.loc[idx_min, 'log_d1']:.12f}"
        )

        print("\nMAXIMO:")
        print(
            f"Municipio: {df_base.loc[idx_max, col_mun]}"
        )
        print(
            f"Credito Rural: "
            f"{df_base.loc[idx_max, 'Credito_Rural_BCB']:,.2f}"
        )
        print(
            f"LN(1 + Credito): "
            f"{df_base.loc[idx_max, 'log_d1']:.12f}"
        )

    print("\n" + "=" * 80)
    # D2: Log-Transform das 4 variaveis de Alojamento/RAIS + MinMax por UF -> Media
    d2_cols = ["Densidade Leitos Hospedagem", "Densidade Estabelecimentos Hospedagem", "Ocup Formais", "Estab Formais"]
    for col in d2_cols:
        df_base[f"log_{col}"] = np.log1p(np.maximum(0, df_base[col]))
        df_base[f"norm_{col}"] = df_base.groupby(col_uf)[f"log_{col}"].transform(min_max_uf)
    df_base["ind_d2"] = df_base[[f"norm_{c}" for c in d2_cols]].mean(axis=1)

    # D3: MinMax por UF das 8 variaveis de MTur/Anatel -> Media (sem log)
    d3_cols = ["Conselho Turismo", "Órgão Turismo", "Plano Diretor", "Plano Município Turismo",
               "Part Rede Móvel", "Part Rede 4G", "Part Rede 5G", "Densidade Banda Fixa"]
    for col in d3_cols:
        df_base[f"norm_{col}"] = df_base.groupby(col_uf)[col].transform(min_max_uf)
    df_base["ind_d3"] = df_base[[f"norm_{c}" for c in d3_cols]].mean(axis=1)

    # ISVT Final: Media das 3 Dimensoes
    df_base["isvt_final"] = df_base[
        ["ind_d1", "ind_d2", "ind_d3"]
    ].mean(axis=1)

    # ==========================================================================
    # ESTATISTICAS DESCRITIVAS POR UF
    # ==========================================================================

    print("\n" + "=" * 80)
    print("ESTATISTICAS DESCRITIVAS POR UF")
    print("=" * 80)

    for estado in sorted(df_base[col_uf].dropna().unique()):

        dados_estado = df_base[
            df_base[col_uf] == estado
        ]

        print(f"\nUF: {estado}")
        print(f"N = {len(dados_estado)}")

        for coluna in [
            "ind_d1",
            "ind_d2",
            "ind_d3",
            "isvt_final"
        ]:

            print(
                f"{coluna}: "
                f"media={dados_estado[coluna].mean():.4f} | "
                f"dp={dados_estado[coluna].std():.4f} | "
                f"mediana={dados_estado[coluna].median():.4f}"
            )

    print("\nGERAL")
    print(f"N = {len(df_base)}")

    for coluna in [
        "ind_d1",
        "ind_d2",
        "ind_d3",
        "isvt_final"
    ]:

        print(
            f"{coluna}: "
            f"media={df_base[coluna].mean():.4f} | "
            f"dp={df_base[coluna].std():.4f} | "
            f"mediana={df_base[coluna].median():.4f}"
        )

    # ==========================================================================
    # MATRIZ DE CORRELACAO
    # ==========================================================================

    print("\n" + "=" * 80)
    print("MATRIZ DE CORRELACAO - D1, D2, D3 E ISVT")
    print("=" * 80)

    matriz_correlacao = (
        df_base[
            [
                "ind_d1",
                "ind_d2",
                "ind_d3",
                "isvt_final"
            ]
        ]
        .corr(method="pearson")
        .round(4)
    )

    print(matriz_correlacao.to_string())

    # --------------------------------------------------------------------------
    # MATRIZ DE TRACAO TERRITORIAL
    # --------------------------------------------------------------------------

    # Capacidade Territorial: média das dimensões D2 e D3
    df_base["capacidade_territorial"] = (
        df_base[["ind_d2", "ind_d3"]].mean(axis=1)
    )

    # Medianas estaduais utilizadas como pontos de corte
    df_base["mediana_d1_uf"] = (
        df_base.groupby(col_uf)["ind_d1"].transform("median")
    )

    df_base["mediana_ct_uf"] = (
        df_base.groupby(col_uf)["capacidade_territorial"].transform("median")
    )

    # Gap de Fomento
    df_base["gap_fomento"] = (
        df_base["capacidade_territorial"] - df_base["ind_d1"]
    )

    # Níveis relativos
    df_base["nivel_capacidade"] = np.where(
        df_base["capacidade_territorial"] >= df_base["mediana_ct_uf"],
        "Alta",
        "Baixa"
    )

    df_base["nivel_fomento"] = np.where(
        df_base["ind_d1"] >= df_base["mediana_d1_uf"],
        "Alto",
        "Baixo"
    )

    # Classificação dos quatro quadrantes
    condicoes_quadrantes = [
        (
            (df_base["nivel_capacidade"] == "Alta") &
            (df_base["nivel_fomento"] == "Alto")
        ),
        (
            (df_base["nivel_capacidade"] == "Alta") &
            (df_base["nivel_fomento"] == "Baixo")
        ),
        (
            (df_base["nivel_capacidade"] == "Baixa") &
            (df_base["nivel_fomento"] == "Baixo")
        ),
        (
            (df_base["nivel_capacidade"] == "Baixa") &
            (df_base["nivel_fomento"] == "Alto")
        )
    ]

    nomes_quadrantes = [
        "Quadrante I",
        "Quadrante II",
        "Quadrante III",
        "Quadrante IV"
    ]

    df_base["quadrante"] = np.select(
        condicoes_quadrantes,
        nomes_quadrantes,
        default="Não classificado"
    )

    classificacoes_quadrantes = {
        "Quadrante I":
            "Alta Capacidade Territorial e Alto Fomento - "
            "Polo Estruturado e Financiado",

        "Quadrante II":
            "Alta Capacidade Territorial e Baixo Fomento - "
            "Vazio Relativo de Fomento",

        "Quadrante III":
            "Baixa Capacidade Territorial e Baixo Fomento - "
            "Fragilidade Territorial e Financeira",

        "Quadrante IV":
            "Baixa Capacidade Territorial e Alto Fomento - "
            "Fomento Relativamente Elevado"
    }

    df_base["classificacao_quadrante"] = (
        df_base["quadrante"].map(classificacoes_quadrantes)
    )

    df_base["vazio_relativo_fomento"] = np.where(
        df_base["quadrante"] == "Quadrante II",
        "SIM",
        "NÃO"
    )

    print("\n" + "=" * 80)
    print("DISTRIBUICAO DOS QUADRANTES")
    print("=" * 80)

    resumo_quadrantes = (
        df_base.groupby([col_uf, "quadrante"])
        .size()
        .unstack(fill_value=0)
    )

    print(resumo_quadrantes.to_string())

    print("\nMaiores gaps positivos de fomento:")

    print(
        df_base[
            [
                col_mun,
                col_uf,
                "ind_d1",
                "capacidade_territorial",
                "gap_fomento",
                "quadrante"
            ]
        ]
        .sort_values("gap_fomento", ascending=False)
        .head(20)
        .to_string(index=False)
    )
    # Exibe no terminal os cinco municípios mais bem classificados em cada UF.
    colunas_ranking = [col_mun, col_uf, "ind_d1", "ind_d2", "ind_d3", "isvt_final"]
    print("\nTop 5 municípios por estado:")
    for estado in sorted(df_base[col_uf].dropna().unique()):
        top_5 = (
            df_base.loc[df_base[col_uf] == estado, colunas_ranking]
            .sort_values("isvt_final", ascending=False)
            .head(5)
            .rename(columns={
                col_mun: "Nome_Municipio_IBGE",
                col_uf: "uf",
                "isvt_final": "ISVT Final",
            })
        )
        print(f"\nEstado: {estado}")
        print(top_5.to_string(index=False, formatters={
            "ind_d1": "{:.4f}".format,
            "ind_d2": "{:.4f}".format,
            "ind_d3": "{:.4f}".format,
            "ISVT Final": "{:.4f}".format,
        }))

    caminho_coordenadas = diretorio_projeto / "Dados" / "municipios_coordenadas.csv"
    if not caminho_coordenadas.exists():
        raise FileNotFoundError(f"Base de coordenadas não encontrada: {caminho_coordenadas}")

    df_coordenadas = pd.read_csv(
        caminho_coordenadas,
        usecols=["codigo_ibge", "latitude", "longitude"],
    )
    df_coordenadas["_codigo_ibge"] = normalizar_codigo_ibge(df_coordenadas["codigo_ibge"])
    df_coordenadas = df_coordenadas.rename(
        columns={"latitude": "lat", "longitude": "lon"}
    )[["_codigo_ibge", "lat", "lon"]]
    df_base = df_base.merge(
        df_coordenadas,
        on="_codigo_ibge",
        how="left",
        validate="one_to_one",
    )
    if df_base[["lat", "lon"]].isna().any().any():
        faltantes = df_base.loc[
            df_base[["lat", "lon"]].isna().any(axis=1), "_codigo_ibge"
        ].tolist()
        raise ValueError(f"Coordenadas não encontradas para códigos IBGE: {faltantes}")
        # ==========================================================================
    # EXPORTACAO DA TABELA CONSOLIDADA DO ISVT
    # ==========================================================================

    print("\n" + "=" * 80)
    print("GERANDO TABELA CONSOLIDADA DO ISVT")
    print("=" * 80)

    # Diretório de saída utilizado também pelo HTML
    diretorio_saida = diretorio_projeto / "out"
    diretorio_saida.mkdir(parents=True, exist_ok=True)

    # Nomes padronizados das colunas principais
    df_resultado = df_base.rename(
        columns={
            col_ibge: "Codigo_IBGE",
            col_mun: "Nome_Municipio_IBGE",
            col_uf: "uf"
        }
    ).copy()

    # --------------------------------------------------------------------------
    # ORDEM DAS COLUNAS DA TABELA FINAL
    # --------------------------------------------------------------------------

    colunas_resultado = [
        # Identificação
        "Codigo_IBGE",
        "Nome_Municipio_IBGE",
        "uf",

        # Valor bruto utilizado na Dimensão 1
        "credito_rural_acumulado_2016_2025",

        # Memória de cálculo da Dimensão 1
        "log_d1",
        "min_log_d1_uf",
        "max_log_d1_uf",

        # Dimensões e indicador sintético
        "ind_d1",
        "ind_d2",
        "ind_d3",
        "isvt_final",

        # Matriz de Tração Territorial
        "capacidade_territorial",
        "mediana_d1_uf",
        "mediana_ct_uf",
        "gap_fomento",
        "nivel_capacidade",
        "nivel_fomento",
        "quadrante",
        "classificacao_quadrante",
        "vazio_relativo_fomento",

        # Variáveis utilizadas em D2
        "Densidade Leitos Hospedagem",
        "Densidade Estabelecimentos Hospedagem",
        "Ocup Formais",
        "Estab Formais",

        # Variáveis utilizadas em D3
        "Conselho Turismo",
        "Órgão Turismo",
        "Plano Diretor",
        "Plano Município Turismo",
        "Part Rede Móvel",
        "Part Rede 4G",
        "Part Rede 5G",
        "Densidade Banda Fixa",

        # Coordenadas utilizadas no mapa
        "lat",
        "lon"
    ]

    # Mantém somente as colunas que realmente existem.
    # Isso evita KeyError se alguma coluna opcional não estiver na base.
    colunas_resultado_existentes = [
        coluna
        for coluna in colunas_resultado
        if coluna in df_resultado.columns
    ]

    colunas_resultado_ausentes = [
        coluna
        for coluna in colunas_resultado
        if coluna not in df_resultado.columns
    ]

    if colunas_resultado_ausentes:
        print(
            "\nAVISO - Colunas não encontradas e não exportadas:"
        )

        for coluna in colunas_resultado_ausentes:
            print(f"  - {coluna}")

    df_saida = df_resultado[
        colunas_resultado_existentes
    ].copy()
    if len(df_saida) != len(df_base):
        raise ValueError(
            "A quantidade de registros da tabela de saída difere "
            "da quantidade de municípios calculados."
        )

    if df_saida["Codigo_IBGE"].duplicated().any():
        duplicados = df_saida.loc[
            df_saida["Codigo_IBGE"].duplicated(
                keep=False
            ),
            [
                "Codigo_IBGE",
                "Nome_Municipio_IBGE",
                "uf"
            ]
        ]

        raise ValueError(
            "Foram encontrados códigos IBGE duplicados na saída:\n"
            + duplicados.to_string(index=False)
        )

    # --------------------------------------------------------------------------
    # PADRONIZACAO DO CODIGO IBGE
    # --------------------------------------------------------------------------

    if "Codigo_IBGE" in df_saida.columns:
        df_saida["Codigo_IBGE"] = (
            df_saida["Codigo_IBGE"]
            .astype("string")
            .str.strip()
            .str.replace(r"\.0$", "", regex=True)
            .str.replace(r"\D", "", regex=True)
            .str.zfill(7)
        )

    # --------------------------------------------------------------------------
    # ARREDONDAMENTO DOS INDICADORES
    # --------------------------------------------------------------------------

    colunas_quatro_casas = [
        "ind_d1",
        "ind_d2",
        "ind_d3",
        "isvt_final",
        "capacidade_territorial",
        "mediana_d1_uf",
        "mediana_ct_uf",
        "gap_fomento"
    ]

    for coluna in colunas_quatro_casas:
        if coluna in df_saida.columns:
            df_saida[coluna] = (
                pd.to_numeric(
                    df_saida[coluna],
                    errors="coerce"
                )
                .round(4)
            )

    colunas_doze_casas = [
        "log_d1",
        "min_log_d1_uf",
        "max_log_d1_uf"
    ]

    for coluna in colunas_doze_casas:
        if coluna in df_saida.columns:
            df_saida[coluna] = (
                pd.to_numeric(
                    df_saida[coluna],
                    errors="coerce"
                )
                .round(12)
            )

    if "credito_rural_acumulado_2016_2025" in df_saida.columns:
        df_saida["credito_rural_acumulado_2016_2025"] = (
            pd.to_numeric(
                df_saida["credito_rural_acumulado_2016_2025"],
                errors="coerce"
            )
            .round(2)
        )

    # --------------------------------------------------------------------------
    # ORDENACAO DA TABELA
    # --------------------------------------------------------------------------

    colunas_ordenacao = [
        coluna
        for coluna in ["uf", "isvt_final", "Nome_Municipio_IBGE"]
        if coluna in df_saida.columns
    ]

    if "isvt_final" in colunas_ordenacao:
        df_saida = df_saida.sort_values(
            by=colunas_ordenacao,
            ascending=[
                True if coluna == "uf" else
                False if coluna == "isvt_final" else
                True
                for coluna in colunas_ordenacao
            ]
        )

    # --------------------------------------------------------------------------
    # CAMINHOS DOS ARQUIVOS
    # --------------------------------------------------------------------------

    caminho_saida_csv = (
        diretorio_saida /
        "ISVT_Resultado_Final_3Dimensoes.csv"
    )

    caminho_saida_xlsx = (
        diretorio_saida /
        "ISVT_Resultado_Final_3Dimensoes.xlsx"
    )

    caminho_saida_csv_raiz = (
        diretorio_projeto /
        "ISVT_Resultado_Final_3Dimensoes.csv"
    )

    caminho_saida_xlsx_raiz = (
        diretorio_projeto /
        "ISVT_Resultado_Final_3Dimensoes.xlsx"
    )

    # --------------------------------------------------------------------------
    # EXPORTACAO CSV
    # --------------------------------------------------------------------------

    df_saida.to_csv(
        caminho_saida_csv,
        index=False,
        sep=";",
        decimal=",",
        encoding="utf-8-sig"
    )

    # Cópia na raiz do projeto
    shutil.copy2(
        caminho_saida_csv,
        caminho_saida_csv_raiz
    )

    print(
        f"\nCSV consolidado gerado em: "
        f"{caminho_saida_csv}"
    )

    # --------------------------------------------------------------------------
    # EXPORTACAO EXCEL
    # --------------------------------------------------------------------------

    try:
        with pd.ExcelWriter(
            caminho_saida_xlsx,
            engine="openpyxl"
        ) as writer:

            # Planilha principal
            df_saida.to_excel(
                writer,
                sheet_name="Resultado_ISVT",
                index=False
            )

            # Resumo estatístico por UF
            resumo_estatistico = (
                df_base
                .groupby(col_uf)[
                    [
                        "ind_d1",
                        "ind_d2",
                        "ind_d3",
                        "isvt_final",
                        "capacidade_territorial",
                        "gap_fomento"
                    ]
                ]
                .agg(
                    [
                        "count",
                        "mean",
                        "std",
                        "median",
                        "min",
                        "max"
                    ]
                )
                .round(4)
            )

            resumo_estatistico.to_excel(
                writer,
                sheet_name="Resumo_por_UF"
            )

            # Distribuição dos quadrantes
            distribuicao_quadrantes = (
                pd.crosstab(
                    df_base[col_uf],
                    df_base["quadrante"],
                    margins=True,
                    margins_name="Total"
                )
            )

            distribuicao_quadrantes.to_excel(
                writer,
                sheet_name="Quadrantes"
            )

            # Municípios do Quadrante II
            vazios_relativos = (
                df_resultado.loc[
                    df_resultado["quadrante"] == "Quadrante II",
                    [
                        "Codigo_IBGE",
                        "Nome_Municipio_IBGE",
                        "uf",
                        "credito_rural_acumulado_2016_2025",
                        "ind_d1",
                        "ind_d2",
                        "ind_d3",
                        "isvt_final",
                        "capacidade_territorial",
                        "gap_fomento",
                        "quadrante",
                        "classificacao_quadrante"
                    ]
                ]
                .sort_values(
                    "gap_fomento",
                    ascending=False
                )
                .copy()
            )

            colunas_arredondar_vazios = [
                "ind_d1",
                "ind_d2",
                "ind_d3",
                "isvt_final",
                "capacidade_territorial",
                "gap_fomento"
            ]

            vazios_relativos[
                colunas_arredondar_vazios
            ] = vazios_relativos[
                colunas_arredondar_vazios
            ].round(4)

            vazios_relativos.to_excel(
                writer,
                sheet_name="Vazios_Relativos",
                index=False
            )

            # Top 5 do ISVT em cada estado
            top_5_por_uf = (
                df_resultado
                .sort_values(
                    ["uf", "isvt_final"],
                    ascending=[True, False]
                )
                .groupby("uf", as_index=False)
                .head(5)
                [
                    [
                        "Codigo_IBGE",
                        "Nome_Municipio_IBGE",
                        "uf",
                        "credito_rural_acumulado_2016_2025",
                        "ind_d1",
                        "ind_d2",
                        "ind_d3",
                        "isvt_final",
                        "quadrante"
                    ]
                ]
                .copy()
            )

            for coluna in [
                "ind_d1",
                "ind_d2",
                "ind_d3",
                "isvt_final"
            ]:
                top_5_por_uf[coluna] = (
                    top_5_por_uf[coluna].round(4)
                )

            top_5_por_uf.to_excel(
                writer,
                sheet_name="Top_5_por_UF",
                index=False
            )

        # Cópia na raiz do projeto
        shutil.copy2(
            caminho_saida_xlsx,
            caminho_saida_xlsx_raiz
        )

        print(
            f"Excel consolidado gerado em: "
            f"{caminho_saida_xlsx}"
        )

    except Exception as erro_excel:
        print(
            "\nAVISO - Não foi possível gerar o arquivo Excel:"
        )
        print(repr(erro_excel))

        print(
            "O CSV foi gerado normalmente."
        )

    print(
        f"Total de municípios exportados: "
        f"{len(df_saida)}"
    )

    print(
        f"Total de colunas exportadas: "
        f"{len(df_saida.columns)}"
    )

    print("=" * 80)
    dados_export = []
    for _, r in df_base.iterrows():
        dados_export.append({
            "codigo_ibge": str(r["_codigo_ibge"]),
            "nome_municipio": str(r[col_mun]),
            "uf": str(r[col_uf]),
            "leitos_cadastur": int(round(r["Densidade Leitos Hospedagem"])),
            "estab_cadastur": int(round(r["Densidade Estabelecimentos Hospedagem"])),
            "renda_per_capita": float(round(r["Renda Per Capita"], 2)),
            "receita_tributaria": float(round(r["Receita Tributária"], 2)),
            "ocup_formais": float(round(r["Ocup Formais"], 2)),
            "estab_formais": float(round(r["Estab Formais"], 2)),
            "comtur": "Sim" if r["Conselho Turismo"] > 0 else "Não",
            "ind_d1": float(round(r["ind_d1"], 4)),
            "ind_d2": float(round(r["ind_d2"], 4)),
            "ind_d3": float(round(r["ind_d3"], 4)),
            "isvt_final": float(round(r["isvt_final"], 4)),
                        "capacidade_territorial": float(
                round(r["capacidade_territorial"], 4)
            ),
            "mediana_d1_uf": float(
                round(r["mediana_d1_uf"], 4)
            ),
            "mediana_ct_uf": float(
                round(r["mediana_ct_uf"], 4)
            ),
            "gap_fomento": float(
                round(r["gap_fomento"], 4)
            ),
            "nivel_capacidade": str(r["nivel_capacidade"]),
            "nivel_fomento": str(r["nivel_fomento"]),
            "quadrante": str(r["quadrante"]),
            "classificacao_quadrante": str(
                r["classificacao_quadrante"]
            ),
            "vazio_relativo_fomento": str(
                r["vazio_relativo_fomento"]
            ),
            "lat": float(r["lat"]),
            "lon": float(r["lon"])
        })

    json_dados = json.dumps(dados_export, ensure_ascii=False)
    total_mun = len(dados_export)
    avg_ba_val = df_base[df_base[col_uf]=="BA"]["isvt_final"].mean()
    avg_rs_val = df_base[df_base[col_uf]=="RS"]["isvt_final"].mean()
    comtur_val = (df_base["Conselho Turismo"] > 0).sum()

    s_prot = 'h' + 't' + 't' + 'p' + 's' + ':' + '/' + '/'
    s_jsd = 'cdn' + '.' + 'jsdelivr' + '.' + 'net/npm/'
    s_unp = 'un' + 'pkg' + '.' + 'com/'
    s_osm = 'www' + '.' + 'openstreetmap' + '.' + 'org/copyright'
    s_carto = 'carto' + '.' + 'com/attributions'

    p_boot = s_prot + s_jsd + "bootstrap@5.3.0/dist/css/bootstrap.min.css"
    p_lf_css = s_prot + s_unp + "leaflet@1.9.4/dist/leaflet.css"
    p_chart = s_prot + s_jsd + "chart.js"
    p_lf_js = s_prot + s_unp + "leaflet@1.9.4/dist/leaflet.js"
    p_tile = s_prot + "server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}"
    p_osm = s_prot + s_osm
    p_carto = s_prot + s_carto

    html_parts = []
    html_parts.append("<!DOCTYPE html>\n<html lang='pt-BR'>\n<head>\n    <meta charset='UTF-8'>\n    <meta name='viewport' content='width=device-width, initial-scale=1.0'>\n    <title>Painel de Inteligencia Territorial ISVT - IBGE / Cadastur / MTur / SICOR</title>\n    <link href='" + p_boot + "' rel='stylesheet'>\n    <link rel='stylesheet' href='" + p_lf_css + "' />\n    <script src='" + p_chart + "'></script>\n    <style>\n        body { background-color: #f4f6f9; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }\n        .header-bg { background: linear-gradient(135deg, #0f2027 0%, #203a43 50%, #2c5364 100%); color: white; padding: 35px 0; border-bottom: 4px solid #00b4db; }\n        .card-stat { border: none; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.06); transition: transform 0.2s; background: #ffffff; }\n        .card-stat:hover { transform: translateY(-3px); }\n        #map { height: 520px; width: 100%; border-radius: 12px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); border: 2px solid #e0e0e0; }\n        .map-status { display: none; }\n        .badge-isvt { font-size: 1.0em; padding: 6px 12px; border-radius: 20px; }\n        .legend-dot { height: 12px; width: 12px; border-radius: 50%; display: inline-block; margin-right: 5px; }\n        .sort-button { width: 100%; border: 0; background: transparent; color: inherit; font-weight: 700; padding: 0; text-align: left; }\n        .sort-arrow { float: right; opacity: 0.7; }\n        .isvt-modal { display: none; position: fixed; inset: 0; z-index: 2000; background: rgba(15, 32, 39, 0.65); padding: 4vh 1rem; overflow-y: auto; }\n        .isvt-modal.show { display: flex; align-items: flex-start; justify-content: center; }\n        .isvt-modal-content { width: min(760px, 100%); background: #fff; border-radius: 12px; box-shadow: 0 8px 30px rgba(0,0,0,0.25); }\n    </style>\n</head>\n<body>\n\n<div class='header-bg text-center mb-4'>\n    <div class='container'>\n        <h1 class='fw-bold'>Painel de Inteligencia Territorial (ISVT)</h1>\n        <p class='lead mb-0'>Analise de Viabilidade do Ecoturismo com Dados Oficiais: IBGE, Cadastur, RAIS, MTur &amp; SICOR</p>\n    </div>\n</div>\n\n<div class='container mb-5'>\n    <div class='row g-3 mb-4 text-center'>\n        <div class='col-md-3'>\n            <div class='card card-stat p-3'>\n                <h6 class='text-muted fw-bold'>Municípios Mapeados</h6>\n                <h2 class='fw-bold text-primary mb-0'>" + str(total_mun) + "</h2>\n                <small class='text-muted'>BA e RS Alvo</small>\n            </div>\n        </div>\n        <div class='col-md-3'>\n            <div class='card card-stat p-3'>\n                <h6 class='text-muted fw-bold'>Média ISVT (Bahia)</h6>\n                <h2 class='fw-bold text-success mb-0'>" + f"{avg_ba_val:.4f}" + "</h2>\n                <small class='text-muted'>Top 1: Mata de São João</small>\n            </div>\n        </div>\n        <div class='col-md-3'>\n            <div class='card card-stat p-3'>\n                <h6 class='text-muted fw-bold'>Média ISVT (Rio Grande do Sul)</h6>\n                <h2 class='fw-bold text-warning mb-0'>" + f"{avg_rs_val:.4f}" + "</h2>\n                <small class='text-muted'>Top 1: Gramado</small>\n            </div>\n        </div>\n        <div class='col-md-3'>\n            <div class='card card-stat p-3'>\n                <h6 class='text-muted fw-bold'>Presença de COMTUR</h6>\n                <h2 class='fw-bold text-info mb-0'>" + str(comtur_val) + "</h2>\n                <small class='text-muted'>Municípios com Conselho Ativo</small>\n            </div>\n        </div>\n    </div>\n\n    <div class='card card-stat p-4 mb-4'>\n        <div class='d-flex justify-content-between align-items-center mb-3 flex-wrap'>\n            <div>\n                <h4 class='fw-bold text-dark mb-1'>Cartografia Interativa do ISVT</h4>\n                <p class='text-muted small mb-0'>Clique nos marcadores para inspecionar os valores brutos do Cadastur e as notas das 3 dimensões.</p>\n            </div>\n            <div class='mt-2 mt-md-0 d-flex gap-2'>\n                <button type='button' class='btn btn-outline-info btn-sm' onclick='openIsvtModal()'>Saiba mais sobre o ISVT</button>\n                <button class='btn btn-outline-primary btn-sm filter-btn active' onclick=\"filterMap('ALL')\">Todos (" + str(total_mun) + ")</button>\n                <button class='btn btn-outline-success btn-sm filter-btn' onclick=\"filterMap('BA')\">Bahia (136)</button>\n                <button class='btn btn-outline-warning btn-sm filter-btn' onclick=\"filterMap('RS')\">Rio Grande do Sul (285)</button>\n                <button class='btn btn-outline-danger btn-sm filter-btn' onclick=\"filterMap('HIGH')\">Alto Desempenho (>=0.70)</button>\n            </div>\n        </div>\n\n        <div id='map'></div>\n        <div id='mapStatus' class='map-status alert alert-warning mt-2 mb-0' role='alert'>Servidor de mapas instável. Recarregue a página se os blocos não carregarem.</div>\n\n        <div class='d-flex align-items-center justify-content-center mt-3 small'>\n            <span class='me-3'><span class='legend-dot bg-success'></span> Alto ISVT (>= 0.70)</span>\n            <span class='me-3'><span class='legend-dot bg-warning'></span> Médio ISVT (0.40 - 0.69)</span>\n            <span><span class='legend-dot bg-danger'></span> Baixo ISVT (&lt; 0.40)</span>\n        </div>\n    </div>\n\n    <div id='isvtModal' class='isvt-modal' onclick='closeIsvtModal(event)'>\n        <div class='isvt-modal-content p-4' onclick='event.stopPropagation()'>\n            <div class='d-flex justify-content-between align-items-start mb-3'>\n                <h4 id='isvtModalTitle' class='fw-bold text-dark mb-0'>Sobre o ISVT</h4>\n                <button type='button' class='btn-close' aria-label='Fechar' onclick='closeIsvtModal()'></button>\n            </div>\n            <p><strong>Definição do ISVT:</strong> Modelo de inteligência territorial formulado para mensurar a capacidade de desenvolvimento regional e atração de investimentos em municípios com vocação para o ecoturismo e o turismo rural.</p>\n            <p><strong>As 3 Dimensões Oficiais:</strong></p>\n            <ul>\n                <li><strong>Dimensão 1 — Fomento Financeiro (D1):</strong> Mede o volume de Crédito Rural (SICOR/Banco Central) injetado na economia local.</li>\n                <li><strong>Dimensão 2 — Alojamento e Emprego Formal (D2):</strong> Mede a infraestrutura receptiva (CADASTUR/MTur) e o estoque de empregos/empresas formais no turismo (RAIS/MTE).</li>\n                <li><strong>Dimensão 3 — Governança e Conectividade (D3):</strong> Avalia instrumentos institucionais de gestão pública (MTur) e cobertura digital 4G/5G/Banda Fixa (Anatel).</li>\n            </ul>\n            <p><strong>Passos do Cálculo Econométrico:</strong></p>\n            <ol>\n                <li>Aplicação do Log-Transform <code>Y = ln(1 + X)</code> em variáveis contínuas.</li>\n                <li>Normalização Min-Max Intra-Estado (<code>groupby UF</code>) em escala de 0,00 a 1,00.</li>\n                <li>Cálculo do ISVT Final pela média simples: <strong>(D1 + D2 + D3) / 3</strong>.</li>\n            </ol>\n            <p><strong>Escala de Interpretação:</strong></p>\n            <ul>\n                <li><span class='badge bg-success'>Alto</span> ISVT >= 0,70 - Polos Estruturados.</li>\n                <li><span class='badge bg-warning text-dark'>Médio</span> ISVT 0,40 - 0,69 - Em Consolidação.</li>\n                <li><span class='badge bg-danger'>Baixo</span> ISVT &lt; 0,40 - Vazios Estruturais.</li>\n            </ul>\n        </div>\n    </div>\n\n    <div class='row g-4 mb-4'>\n        <div class='col-md-6'>\n            <div class='card card-stat p-4 h-100'>\n                <h5 class='fw-bold text-dark mb-3'>Top 5 Municípios Por Estado</h5>\n                <canvas id='barChart' height='220'></canvas>\n                <div class='d-flex justify-content-center gap-4 mt-3 small'>\n                    <span><span class='legend-dot' style='background-color: #1565c0;'></span> Bahia (BA)</span>\n                    <span><span class='legend-dot' style='background-color: #f2c300;'></span> Rio Grande do Sul (RS)</span>\n                </div>\n            </div>\n        </div>\n        <div class='col-md-6'>\n            <div class='card card-stat p-4 h-100'>\n                <h5 class='fw-bold text-dark mb-3'>Média das 3 Dimensões (BA vs RS)</h5>\n                <canvas id='radarChart' height='220'></canvas>\n            </div>\n        </div>\n    </div>\n\n    <div class='card card-stat p-4'>\n        <div class='d-flex justify-content-between align-items-center mb-3 flex-wrap'>\n            <h4 class='fw-bold text-dark'>Tabela Completa de Municípios e Rankings</h4>\n            <input type='text' id='searchInput' class='form-control w-auto mt-2 mt-md-0' placeholder='Buscar município ou UF...'>\n        </div>\n        <div class='table-responsive'>\n            <table class='table table-hover align-middle'>\n                <thead class='table-dark'>\n                    <tr>\n                        <th><button class='sort-button' onclick=\"sortTable('codigo_ibge')\">Código IBGE <span class='sort-arrow'>↕</span></button></th>\n                        <th><button class='sort-button' onclick=\"sortTable('nome_municipio')\">Município <span class='sort-arrow'>↕</span></button></th>\n                        <th><button class='sort-button' onclick=\"sortTable('uf')\">UF <span class='sort-arrow'>↕</span></button></th>\n                        <th><button class='sort-button' onclick=\"sortTable('leitos_cadastur')\">Leitos (Cadastur) <span class='sort-arrow'>↕</span></button></th>\n                        <th><button class='sort-button' onclick=\"sortTable('renda_per_capita')\">Renda (IBGE) <span class='sort-arrow'>↕</span></button></th>\n                        <th><button class='sort-button' onclick=\"sortTable('receita_tributaria')\">Receita Tributária <span class='sort-arrow'>↕</span></button></th>\n                        <th><button class='sort-button' onclick=\"sortTable('ocup_formais')\">Ocup. Formais <span class='sort-arrow'>↕</span></button></th>\n                        <th><button class='sort-button' onclick=\"sortTable('estab_formais')\">Empresas Formais <span class='sort-arrow'>↕</span></button></th>\n                        <th><button class='sort-button' onclick=\"sortTable('comtur')\">COMTUR <span class='sort-arrow'>↕</span></button></th>\n                        <th><button class='sort-button' onclick=\"sortTable('ind_d1')\">D1 (Fomento) <span class='sort-arrow'>↕</span></button></th>\n                        <th><button class='sort-button' onclick=\"sortTable('ind_d2')\">D2 (Alojamento) <span class='sort-arrow'>↕</span></button></th>\n                        <th><button class='sort-button' onclick=\"sortTable('ind_d3')\">D3 (Governança) <span class='sort-arrow'>↕</span></button></th>\n                        <th><button class='sort-button' onclick=\"sortTable('isvt_final')\">ISVT Final <span class='sort-arrow'>↕</span></button></th>\n                    </tr>\n                </thead>\n                <tbody id='tableBody'></tbody>\n            </table>\n        </div>\n    </div>\n</div>\n\n<script src='" + p_lf_js + "'></script>\n\n<script>\nconst dados = " + json_dados + ";\n\nfunction openIsvtModal() {\n    document.getElementById('isvtModal').classList.add('show');\n    document.body.style.overflow = 'hidden';\n}\n\nfunction closeIsvtModal(event) {\n    if (!event || event.target.id === 'isvtModal' || event.target.classList.contains('btn-close')) {\n        document.getElementById('isvtModal').classList.remove('show');\n        document.body.style.overflow = '';\n    }\n}\n\ndocument.addEventListener('keydown', event => {\n    if (event.key === 'Escape') closeIsvtModal();\n});\n\nconst map = L.map('map').setView([-20.0, -45.0], 5);\n\nconst cartoDBLayer = L.tileLayer('" + p_tile + "', {\n    maxZoom: 18,\n    attribution: '&copy; OpenStreetMap &copy; CARTO | Fonte: IBGE, Cadastur, RAIS, MTur, SICOR'\n});\ncartoDBLayer.addTo(map);\n\nconst markersGroup = L.layerGroup().addTo(map);\n\nfunction getMarkerColor(isvt) {\n    if (isvt >= 0.70) return '#28a745';\n    if (isvt >= 0.40) return '#ffc107';\n    return '#dc3545';\n}\n\nfunction renderMap(dataList) {\n    markersGroup.clearLayers();\n    dataList.forEach(item => {\n        if (item.lat && item.lon) {\n            const markerColor = getMarkerColor(item.isvt_final);\n            const marker = L.circleMarker([item.lat, item.lon], {\n                radius: 7,\n                fillColor: markerColor,\n                color: '#ffffff',\n                weight: 1.5,\n                opacity: 1,\n                fillOpacity: 0.85\n            });\n\n                        const popupText = '<div style=\"font-family: sans-serif; min-width: 280px;\"><h6 style=\"margin: 0; color: #0f2027; font-weight: bold;\">' + item.nome_municipio + ' (' + item.uf + ')</h6><small class=\"text-muted\">Código IBGE: ' + item.codigo_ibge + '</small><hr style=\"margin: 6px 0;\"><b>ISVT Final:</b> <span class=\"badge bg-secondary\">' + item.isvt_final.toFixed(4) + '</span><br><small><b>D1 - Fomento:</b> ' + item.ind_d1.toFixed(4) + '</small><br><small><b>D2 - Alojamento e Emprego:</b> ' + item.ind_d2.toFixed(4) + '</small><br><small><b>D3 - Governança e Conectividade:</b> ' + item.ind_d3.toFixed(4) + '</small><hr style=\"margin: 6px 0;\"><small><b>Capacidade Territorial:</b> ' + item.capacidade_territorial.toFixed(4) + '</small><br><small><b>Mediana CT da UF:</b> ' + item.mediana_ct_uf.toFixed(4) + '</small><br><small><b>Mediana D1 da UF:</b> ' + item.mediana_d1_uf.toFixed(4) + '</small><br><small><b>Gap de Fomento:</b> ' + item.gap_fomento.toFixed(4) + '</small><br><small><b>Quadrante:</b> ' + item.quadrante + '</small><br><small><b>Classificação:</b> ' + item.classificacao_quadrante + '</small><hr style=\"margin: 6px 0;\"><small style=\"color: #444;\">Leitos: ' + item.leitos_cadastur.toLocaleString('pt-BR') + '<br>Estabelecimentos: ' + item.estab_cadastur.toLocaleString('pt-BR') + '<br>Ocupações Formais: ' + item.ocup_formais.toFixed(2) + '<br>COMTUR: ' + item.comtur + '</small></div>';\n            marker.bindPopup(popupText);\n            markersGroup.addLayer(marker);\n        }\n    });\n}\n\nrenderMap(dados);\n\nfunction filterMap(type) {\n    document.querySelectorAll('.filter-btn').forEach(btn => btn.classList.remove('active'));\n    if (event && event.target) event.target.classList.add('active');\n\n    let filtered = dados;\n    if (type === 'BA') { filtered = dados.filter(d => d.uf === 'BA'); map.setView([-12.5, -41.5], 6); }\n    else if (type === 'RS') { filtered = dados.filter(d => d.uf === 'RS'); map.setView([-30.0, -53.0], 6); }\n    else if (type === 'HIGH') { filtered = dados.filter(d => d.isvt_final >= 0.70); map.setView([-19.0, -46.0], 5); }\n    else { map.setView([-20.0, -45.0], 5); }\n\n    renderMap(filtered);\n    renderTable(filtered);\n}\n\nlet currentTableData = dados.slice();\nlet sortKey = null;\nlet sortAscending = true;\nfunction renderTable(dataList) {\n    currentTableData = dataList.slice();\n    const tbody = document.getElementById('tableBody');\n    tbody.innerHTML = '';\n    dataList.forEach(item => {\n        const badgeClass = item.isvt_final >= 0.70 ? 'bg-success' : (item.isvt_final >= 0.40 ? 'bg-warning text-dark' : 'bg-danger');\n        let quadranteClass = 'bg-secondary';\n        if (item.quadrante === 'Quadrante I') {\n            quadranteClass = 'bg-success';\n        } else if (item.quadrante === 'Quadrante II') {\n            quadranteClass = 'bg-primary';\n        } else if (item.quadrante === 'Quadrante III') {\n            quadranteClass = 'bg-danger';\n        } else if (item.quadrante === 'Quadrante IV') {\n            quadranteClass = 'bg-warning text-dark';\n        }\n                const row = '<tr><td><code>' + item.codigo_ibge + '</code></td><td class=\"fw-bold\">' + item.nome_municipio + '</td><td><span class=\"badge bg-secondary\">' + item.uf + '</span></td><td>' + item.leitos_cadastur.toLocaleString('pt-BR') + '</td><td>' + item.ocup_formais.toFixed(2) + '</td><td>' + item.estab_formais.toFixed(2) + '</td><td>' + (item.comtur === 'Sim' ? '✅' : '❌') + '</td><td>' + item.ind_d1.toFixed(4) + '</td><td>' + item.ind_d2.toFixed(4) + '</td><td>' + item.ind_d3.toFixed(4) + '</td><td>' + item.capacidade_territorial.toFixed(4) + '</td><td>' + item.gap_fomento.toFixed(4) + '</td><td><span class=\"badge ' + quadranteClass + '\" title=\"' + item.classificacao_quadrante + '\">' + item.quadrante + '</span></td><td><span class=\"badge badge-isvt ' + badgeClass + '\">' + item.isvt_final.toFixed(4) + '</span></td></tr>';\n        tbody.innerHTML += row;\n    });\n}\n\n\n\nfunction sortTable(key) {\n    if (sortKey === key) {\n        sortAscending = !sortAscending;\n    } else {\n        sortKey = key;\n        sortAscending = true;\n    }\n\n    const isNumeric = ['codigo_ibge', 'leitos_cadastur', 'ocup_formais', 'estab_formais', 'ind_d1', 'ind_d2', 'ind_d3', 'capacidade_territorial','gap_fomento','isvt_final'].includes(key);\n\n    const sorted = currentTableData.slice().sort((a, b) => {\n        let comparison = 0;\n        if (isNumeric) {\n            comparison = Number(a[key]) - Number(b[key]);\n        } else {\n            comparison = String(a[key]).localeCompare(String(b[key]), 'pt-BR', { sensitivity: 'base' });\n        }\n        return sortAscending ? comparison : -comparison;\n    });\n\n    renderTable(sorted);\n\n    document.querySelectorAll('.sort-arrow').forEach(arrow => arrow.textContent = '↕');\n    const activeButton = document.querySelector('[onclick=\"sortTable(\\\"' + key + '\\\")\"] .sort-arrow');\n    if (activeButton) {\n        activeButton.textContent = sortAscending ? '↑' : '↓';\n    }\n}\n\nrenderTable(dados);\n\ndocument.getElementById('searchInput').addEventListener('keyup', function() {\n    const val = this.value.toLowerCase().trim();\n    const filtered = dados.filter(d => d.nome_municipio.toLowerCase().includes(val) || d.uf.toLowerCase().includes(val) || d.codigo_ibge.includes(val));\n    renderTable(filtered);\n    renderMap(filtered);\n});\n\nconst baTop5 = dados.filter(d => d.uf === 'BA').sort((a,b) => b.isvt_final - a.isvt_final).slice(0,5);\nconst rsTop5 = dados.filter(d => d.uf === 'RS').sort((a,b) => b.isvt_final - a.isvt_final).slice(0,5);\n\nconst ctxBar = document.getElementById('barChart').getContext('2d');\nnew Chart(ctxBar, {\n    type: 'bar',\n    data: {\n        labels: [...baTop5.map(d => d.nome_municipio), ...rsTop5.map(d => d.nome_municipio)],\n        datasets: [{\n            label: 'ISVT Final',\n            data: [...baTop5.map(d => d.isvt_final), ...rsTop5.map(d => d.isvt_final)],\n            backgroundColor: [\n                ...Array(baTop5.length).fill('#1565c0'),\n                ...Array(rsTop5.length).fill('#f2c300')\n            ]\n        }]\n    },\n    options: { responsive: true, plugins: { legend: { display: false } } }\n});\n\nconst avgD1_BA = dados.filter(d => d.uf === 'BA').reduce((s,d) => s + d.ind_d1, 0) / dados.filter(d => d.uf === 'BA').length;\nconst avgD2_BA = dados.filter(d => d.uf === 'BA').reduce((s,d) => s + d.ind_d2, 0) / dados.filter(d => d.uf === 'BA').length;\nconst avgD3_BA = dados.filter(d => d.uf === 'BA').reduce((s,d) => s + d.ind_d3, 0) / dados.filter(d => d.uf === 'BA').length;\n\nconst avgD1_RS = dados.filter(d => d.uf === 'RS').reduce((s,d) => s + d.ind_d1, 0) / dados.filter(d => d.uf === 'RS').length;\nconst avgD2_RS = dados.filter(d => d.uf === 'RS').reduce((s,d) => s + d.ind_d2, 0) / dados.filter(d => d.uf === 'RS').length;\nconst avgD3_RS = dados.filter(d => d.uf === 'RS').reduce((s,d) => s + d.ind_d3, 0) / dados.filter(d => d.uf === 'RS').length;\n\nconst ctxRadar = document.getElementById('radarChart').getContext('2d');\nnew Chart(ctxRadar, {\n    type: 'radar',\n    data: {\n        labels: ['D1 (Fomento SICOR)', 'D2 (Alojamento/RAIS)', 'D3 (Governança/Anatel)'],\n        datasets: [\n            {\n                label: 'Bahia (Média)',\n                data: [avgD1_BA, avgD2_BA, avgD3_BA],\n                backgroundColor: 'rgba(21, 101, 192, 0.2)',\n                borderColor: '#1565c0',\n                pointBackgroundColor: '#1565c0'\n            },\n            {\n                label: 'Rio Grande do Sul (Média)',\n                data: [avgD1_RS, avgD2_RS, avgD3_RS],\n                backgroundColor: 'rgba(242, 195, 0, 0.2)',\n                borderColor: '#f2c300',\n                pointBackgroundColor: '#f2c300'\n            }\n        ]\n    },\n    options: { responsive: true, scales: { r: { min: 0, max: 1 } } }\n});\n</script></body></html>")

    final_html = "".join(html_parts)
    # ============================================================
    # BLOCO INFORMATIVO ANTES DA CARTOGRAFIA
    # ============================================================

    bloco_informativo = """
    <div class='card card-stat p-4 mb-4'>
        <div class='row align-items-center g-3'>

            <div class='col-md-8'>
                <h4 class='fw-bold text-dark mb-1'>
                    Metodologia e interpretação dos resultados
                </h4>

                <p class='text-muted mb-0'>
                    Consulte a composição do ISVT e os critérios utilizados
                    para classificar os municípios na Matriz de Tração
                    Territorial.
                </p>
            </div>

            <div class='col-md-4'>
                <div class='d-flex flex-wrap justify-content-md-end gap-2'>

                    <button
                        type='button'
                        class='btn btn-outline-info'
                        onclick='openIsvtModal()'
                    >
                        Saiba mais sobre o ISVT
                    </button>

                    <button
                        type='button'
                        class='btn btn-outline-primary'
                        onclick='openQuadrantesModal()'
                    >
                        Saiba mais sobre os quadrantes
                    </button>

                </div>
            </div>

        </div>
    </div>
"""

    marcador_cartografia = """
    <div class='card card-stat p-4 mb-4'>
        <div class='d-flex justify-content-between align-items-center mb-3 flex-wrap'>
            <div>
                <h4 class='fw-bold text-dark mb-1'>Cartografia Interativa do ISVT</h4>
"""

    if marcador_cartografia not in final_html:
        raise ValueError(
            "Não foi possível localizar o bloco da Cartografia Interativa "
            "para inserir o bloco informativo."
        )

    final_html = final_html.replace(
        marcador_cartografia,
        bloco_informativo + marcador_cartografia,
        1
    )
        # Remove o botão antigo de dentro da cartografia
    botao_isvt_antigo = (
        "<button type='button' "
        "class='btn btn-outline-info btn-sm' "
        "onclick='openIsvtModal()'>"
        "Saiba mais sobre o ISVT"
        "</button>"
    )

    final_html = final_html.replace(
        botao_isvt_antigo,
        "",
        1
    )

        # ============================================================
    # MODAL EXPLICATIVO DOS QUADRANTES
    # ============================================================

    modal_quadrantes = """
<div id='quadrantesModal'
     class='isvt-modal'
     onclick='closeQuadrantesModal(event)'>

    <div class='isvt-modal-content p-4'
         onclick='event.stopPropagation()'>

        <div class='d-flex justify-content-between align-items-start mb-3'>

            <div>
                <h4 class='fw-bold text-dark mb-1'>
                    Matriz de Tração Territorial
                </h4>

                <p class='text-muted small mb-0'>
                    Interpretação dos quadrantes e dos vazios relativos
                    de fomento.
                </p>
            </div>

            <button
                type='button'
                class='btn-close'
                aria-label='Fechar'
                onclick='closeQuadrantesModal()'
            ></button>

        </div>

        <p>
            Os quadrantes resultam do cruzamento entre a
            <strong>Capacidade Territorial (CT)</strong> e a dimensão de
            <strong>Fomento Rural (D1)</strong>.
        </p>

        <div class='alert alert-light border'>
            <strong>Capacidade Territorial:</strong>
            média entre D2, referente a alojamento e emprego turístico formal,
            e D3, referente a governança e conectividade.
            <br><br>
            <code>CT = (D2 + D3) / 2</code>
        </div>

        <div class='alert alert-light border'>
            <strong>Gap de Fomento:</strong>
            diferença entre a Capacidade Territorial e o nível relativo
            de fomento.
            <br><br>
            <code>GF = CT - D1</code>
        </div>

        <div class='mb-3 p-3 border rounded'>
            <h6 class='fw-bold text-success'>
                Quadrante I — Alta capacidade e alto fomento
            </h6>

            <p class='mb-0'>
                Reúne municípios com Capacidade Territorial e Fomento Rural
                iguais ou superiores às respectivas medianas estaduais.
                Representa polos relativamente estruturados e financiados.
            </p>
        </div>

        <div class='mb-3 p-3 border border-primary rounded'>
            <h6 class='fw-bold text-primary'>
                Quadrante II — Alta capacidade e baixo fomento
            </h6>

            <p class='mb-0'>
                Reúne municípios com Capacidade Territorial igual ou superior
                à mediana estadual, mas com Fomento Rural abaixo da mediana.
                Este grupo corresponde aos
                <strong>vazios relativos de fomento</strong>, nos quais as
                condições territoriais observadas são relativamente superiores
                à intensidade do fomento registrado.
            </p>
        </div>

        <div class='mb-3 p-3 border border-danger rounded'>
            <h6 class='fw-bold text-danger'>
                Quadrante III — Baixa capacidade e baixo fomento
            </h6>

            <p class='mb-0'>
                Reúne municípios com Capacidade Territorial e Fomento Rural
                abaixo das respectivas medianas estaduais. Indica situações
                de fragilidade territorial e financeira relativa.
            </p>
        </div>

        <div class='mb-3 p-3 border border-warning rounded'>
            <h6 class='fw-bold text-warning-emphasis'>
                Quadrante IV — Baixa capacidade e alto fomento
            </h6>

            <p class='mb-0'>
                Reúne municípios com Fomento Rural igual ou superior à mediana,
                mas com Capacidade Territorial abaixo da mediana estadual.
                Indica fomento relativamente elevado diante das condições
                territoriais mensuradas.
            </p>
        </div>

        <div class='alert alert-warning mb-0'>
            <strong>Importante:</strong>
            a classificação é relativa à distribuição dos municípios de cada
            estado. O Quadrante II não comprova, isoladamente, demanda reprimida,
            racionamento de crédito ou falha das instituições financeiras.
        </div>

    </div>
</div>
"""

    marcador_modal_isvt = "<div id='isvtModal' class='isvt-modal'"

    if marcador_modal_isvt not in final_html:
        raise ValueError(
            "Não foi possível localizar o modal do ISVT para inserir "
            "o modal dos quadrantes."
        )

    final_html = final_html.replace(
        marcador_modal_isvt,
        modal_quadrantes + "\n" + marcador_modal_isvt,
        1
    )
        # ============================================================
    # FUNCOES JAVASCRIPT DO MODAL DOS QUADRANTES
    # ============================================================

    funcoes_modal_quadrantes = """
function openQuadrantesModal() {
    document
        .getElementById('quadrantesModal')
        .classList
        .add('show');

    document.body.style.overflow = 'hidden';
}

function closeQuadrantesModal(event) {
    if (
        !event ||
        event.target.id === 'quadrantesModal' ||
        event.target.classList.contains('btn-close')
    ) {
        document
            .getElementById('quadrantesModal')
            .classList
            .remove('show');

        document.body.style.overflow = '';
    }
}

"""

    marcador_evento_teclado = (
        "document.addEventListener('keydown', event => {"
    )

    if marcador_evento_teclado not in final_html:
        raise ValueError(
            "Não foi possível localizar o evento de teclado "
            "para adicionar as funções do modal dos quadrantes."
        )

    final_html = final_html.replace(
        marcador_evento_teclado,
        funcoes_modal_quadrantes + marcador_evento_teclado,
        1
    )

        # ============================================================
    # BOTOES DE FILTRO DOS QUADRANTES
    # ============================================================

    botao_alto_desempenho = (
        "<button class='btn btn-outline-danger btn-sm filter-btn' "
        "onclick=\"filterMap('HIGH')\">"
        "Alto Desempenho (>=0.70)"
        "</button>"
    )

    botoes_quadrantes = """
<button
    class='btn btn-outline-success btn-sm filter-btn'
    onclick="filterMap('Q1', event)"
    title='Alta Capacidade Territorial e Alto Fomento'
>
    Quadrante I
</button>

<button
    class='btn btn-outline-primary btn-sm filter-btn'
    onclick="filterMap('Q2', event)"
    title='Alta Capacidade Territorial e Baixo Fomento'
>
    Quadrante II
</button>

<button
    class='btn btn-outline-danger btn-sm filter-btn'
    onclick="filterMap('Q3', event)"
    title='Baixa Capacidade Territorial e Baixo Fomento'
>
    Quadrante III
</button>

<button
    class='btn btn-outline-warning btn-sm filter-btn'
    onclick="filterMap('Q4', event)"
    title='Baixa Capacidade Territorial e Alto Fomento'
>
    Quadrante IV
</button>
"""

    if botao_alto_desempenho not in final_html:
        raise ValueError(
            "Não foi possível localizar o botão Alto Desempenho."
        )

    final_html = final_html.replace(
        botao_alto_desempenho,
        botao_alto_desempenho + botoes_quadrantes,
        1
    )
        # ============================================================
    # SUBSTITUI A FUNCAO DE FILTRO DO MAPA
    # ============================================================

    inicio_filter = final_html.index(
        "function filterMap(type)"
    )

    fim_filter = final_html.index(
        "let currentTableData",
        inicio_filter
    )

    nova_funcao_filter = """
function filterMap(type, event) {

    document
        .querySelectorAll('.filter-btn')
        .forEach(btn => btn.classList.remove('active'));

    if (event && event.currentTarget) {
        event.currentTarget.classList.add('active');
    }

    let filtered = dados;

    if (type === 'BA') {

        filtered = dados.filter(
            d => d.uf === 'BA'
        );

        map.setView([-12.5, -41.5], 6);

    } else if (type === 'RS') {

        filtered = dados.filter(
            d => d.uf === 'RS'
        );

        map.setView([-30.0, -53.0], 6);

    } else if (type === 'HIGH') {

        filtered = dados.filter(
            d => d.isvt_final >= 0.70
        );

        map.setView([-19.0, -46.0], 5);

    } else if (type === 'Q1') {

        filtered = dados.filter(
            d => d.quadrante === 'Quadrante I'
        );

        map.setView([-20.0, -45.0], 5);

    } else if (type === 'Q2') {

        filtered = dados.filter(
            d => d.quadrante === 'Quadrante II'
        );

        map.setView([-20.0, -45.0], 5);

    } else if (type === 'Q3') {

        filtered = dados.filter(
            d => d.quadrante === 'Quadrante III'
        );

        map.setView([-20.0, -45.0], 5);

    } else if (type === 'Q4') {

        filtered = dados.filter(
            d => d.quadrante === 'Quadrante IV'
        );

        map.setView([-20.0, -45.0], 5);

    } else {

        filtered = dados;

        map.setView([-20.0, -45.0], 5);
    }

    filtered = filtered
        .slice()
        .sort(
            (a, b) => b.isvt_final - a.isvt_final
        );

    renderMap(filtered);
    renderTable(filtered);
}

"""

    final_html = (
        final_html[:inicio_filter]
        + nova_funcao_filter
        + final_html[fim_filter:]
    )
    # ============================================================
    # SUBSTITUI CABECALHO DA TABELA
    # ============================================================

    inicio_thead = final_html.index(
        "<thead class='table-dark'>"
    )

    fim_thead = final_html.index(
        "</thead>",
        inicio_thead
    ) + len("</thead>")

    novo_thead = """
<thead class='table-dark'>
    <tr>
        <th>
            <button class='sort-button' onclick="sortTable('codigo_ibge')">
                Código IBGE <span class='sort-arrow'>↕</span>
            </button>
        </th>

        <th>
            <button class='sort-button' onclick="sortTable('nome_municipio')">
                Município <span class='sort-arrow'>↕</span>
            </button>
        </th>

        <th>
            <button class='sort-button' onclick="sortTable('uf')">
                UF <span class='sort-arrow'>↕</span>
            </button>
        </th>

        <th>
            <button class='sort-button' onclick="sortTable('leitos_cadastur')">
                Leitos (Cadastur) <span class='sort-arrow'>↕</span>
            </button>
        </th>

        <th>
            <button class='sort-button' onclick="sortTable('ocup_formais')">
                Ocup. Formais <span class='sort-arrow'>↕</span>
            </button>
        </th>

        <th>
            <button class='sort-button' onclick="sortTable('estab_formais')">
                Empresas Formais <span class='sort-arrow'>↕</span>
            </button>
        </th>

        <th>
            <button class='sort-button' onclick="sortTable('comtur')">
                COMTUR <span class='sort-arrow'>↕</span>
            </button>
        </th>

        <th>
            <button class='sort-button' onclick="sortTable('ind_d1')">
                D1 (Fomento) <span class='sort-arrow'>↕</span>
            </button>
        </th>

        <th>
            <button class='sort-button' onclick="sortTable('ind_d2')">
                D2 (Alojamento) <span class='sort-arrow'>↕</span>
            </button>
        </th>

        <th>
            <button class='sort-button' onclick="sortTable('ind_d3')">
                D3 (Governança) <span class='sort-arrow'>↕</span>
            </button>
        </th>

        <th>
            <button class='sort-button' onclick="sortTable('capacidade_territorial')">
                Capacidade Territorial <span class='sort-arrow'>↕</span>
            </button>
        </th>

        <th>
            <button class='sort-button' onclick="sortTable('gap_fomento')">
                Gap de Fomento <span class='sort-arrow'>↕</span>
            </button>
        </th>

        <th>
            <button class='sort-button' onclick="sortTable('quadrante')">
                Quadrante <span class='sort-arrow'>↕</span>
            </button>
        </th>

        <th>
            <button class='sort-button' onclick="sortTable('isvt_final')">
                ISVT Final <span class='sort-arrow'>↕</span>
            </button>
        </th>
    </tr>
</thead>
"""

    final_html = (
        final_html[:inicio_thead]
        + novo_thead
        + final_html[fim_thead:]
    )
    final_html = final_html.replace(
        "cartoDBLayer.addTo(map);",
        """cartoDBLayer.addTo(map);

const esriFallbackLayer = L.tileLayer(
    'https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}',
    {
        maxZoom: 18,
        attribution: '&copy; Esri | Fonte: IBGE, Cadastur, RAIS, MTur, SICOR'
    }
);
let cartoFallbackActivated = false;
cartoDBLayer.on('tileerror', () => {
    if (!cartoFallbackActivated) {
        cartoFallbackActivated = true;
        map.removeLayer(cartoDBLayer);
        esriFallbackLayer.addTo(map);
        const status = document.getElementById('mapStatus');
        status.textContent = 'CartoDB indisponível no momento. O mapa foi carregado com uma camada alternativa.';
        status.style.display = 'block';
    }
});"""
    )
    final_html = final_html.replace(
        ".isvt-modal-content { width: min(760px, 100%); background: #fff; border-radius: 12px; box-shadow: 0 8px 30px rgba(0,0,0,0.25); }",
        ".isvt-modal-content { width: min(760px, 100%); background: #fff; border-radius: 12px; box-shadow: 0 8px 30px rgba(0,0,0,0.25); }\n"
        ".chart-row { align-items: flex-start; }\n"
        ".chart-card { height: auto !important; }\n"
        ".chart-card canvas { max-height: 300px; }"
    )
    final_html = final_html.replace(
        "<div class='row g-4 mb-4'>\n        <div class='col-md-6'>\n            <div class='card card-stat p-4 h-100'>",
        "<div class='row g-4 mb-4 chart-row'>\n        <div class='col-md-6'>\n            <div class='card card-stat p-4 chart-card'>"
    )
    final_html = final_html.replace(
        "<div class='col-md-6'>\n            <div class='card card-stat p-4 h-100'>\n                <h5 class='fw-bold text-dark mb-3'>Média das 3 Dimensões (BA vs RS)</h5>",
        "<div class='col-md-6'>\n            <div class='card card-stat p-4 chart-card'>\n                <h5 class='fw-bold text-dark mb-3'>Média das 3 Dimensões (BA vs RS)</h5>"
    )
    final_html = final_html.replace(
        "let sortKey = null;\nlet sortAscending = true;",
        "let sortKey = 'isvt_final';\nlet sortAscending = false;"
    )
    final_html = final_html.replace(
        "renderTable(dados);",
        "renderTable(dados.slice().sort((a, b) => b.isvt_final - a.isvt_final));"
    )
    final_html = final_html.replace(
        "const filtered = dados.filter(d => d.nome_municipio.toLowerCase().includes(val) || d.uf.toLowerCase().includes(val) || d.codigo_ibge.includes(val));",
        "const filtered = dados.filter(d => d.nome_municipio.toLowerCase().includes(val) || d.uf.toLowerCase().includes(val) || d.codigo_ibge.includes(val)).sort((a, b) => b.isvt_final - a.isvt_final);"
    )
    diretorio_saida = diretorio_projeto / "out"
    diretorio_saida.mkdir(parents=True, exist_ok=True)
    caminho_index = diretorio_saida / "index.html"
    with open(caminho_index, "w", encoding="utf-8") as f:
        f.write(final_html)

    caminho_index_raiz = diretorio_projeto / "index.html"
    shutil.copy2(caminho_index, caminho_index_raiz)
    print("Matriz calculada com sucesso!")
    print(f"HTML gerado em: {caminho_index}")
    print(f"Cópia publicada em: {caminho_index_raiz}")

if __name__ == '__main__':
    executar_gerador_html()


