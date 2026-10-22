import os
from pathlib import Path
import glob
import pandas as pd
import geopandas as gpd

# ==============================================================================
# 1. CONFIGURAÇÕES DE CAMINHOS (AJUSTE CONFORME SUA MÁQUINA)
# ==============================================================================
DIRETORIO_PROJETO = r"C:\Geo\Escola de Governo"
CAMINHO_GEOJSON_GLEBAS = os.path.join(DIRETORIO_PROJETO, "Mesclados.geojson") 

# Arquivos de saída
CAMINHO_SAIDA_LONG = os.path.join(DIRETORIO_PROJETO, "Fomento_Municipal_Anual_LONG.csv")
CAMINHO_SAIDA_WIDE = os.path.join(DIRETORIO_PROJETO, "Fomento_Municipal_Anual_WIDE.csv")

# ==============================================================================
# 2. PROCESSAMENTO E CONCATENAÇÃO DAS OPERAÇÕES POR ANO (2016 A 2026)
# ==============================================================================
print("1/5. Buscando arquivos locais de operações de 2016 a 2026...")

padrao_arquivos = os.path.join(DIRETORIO_PROJETO, "SICOR_OPERACAO_BASICA_ESTADO_*.csv")
arquivos_operacoes = glob.glob(padrao_arquivos)

if not arquivos_operacoes:
    raise FileNotFoundError(f"Nenhum arquivo correspondente a {padrao_arquivos} foi encontrado na pasta.")

print(f"Encontrados {len(arquivos_operacoes)} arquivos de operações para processar.")

dfs_operacoes = []
for caminho_csv in arquivos_operacoes:
    # Extrai o ano do nome do arquivo
    ano = os.path.basename(caminho_csv).split('_')[-1].replace('.csv', '')
    print(f" -> Lendo e limpando ano {ano}...")
    
    try:
        df_ano = pd.read_csv(caminho_csv, sep=';', encoding='utf-8', low_memory=False)
    except UnicodeDecodeError:
        df_ano = pd.read_csv(caminho_csv, sep=';', encoding='latin1', low_memory=False)
    
    col_bacen = '#REF_BACEN'
    col_ordem = 'NU_ORDEM'
    col_recurso = 'VL_PARC_CREDITO'
    
    df_padronizado = pd.DataFrame()
    df_padronizado['id_referencia_bacen'] = df_ano[col_bacen].astype(str)
    df_padronizado['nu_ordem'] = df_ano[col_ordem].astype(str)
    df_padronizado['ano'] = int(ano)
    
    # Tratamento de decimais padrão brasileiro
    if df_ano[col_recurso].dtype == object:
        serie_limpa = df_ano[col_recurso].astype(str)\
                                         .str.replace('.', '', regex=False)\
                                         .str.replace(',', '.', regex=False)
        df_padronizado['vlr_recurso'] = pd.to_numeric(serie_limpa, errors='coerce')
    else:
        df_padronizado['vlr_recurso'] = pd.to_numeric(df_ano[col_recurso], errors='coerce')
    
    df_padronizado['chavenova'] = df_padronizado['id_referencia_bacen'] + "-" + df_padronizado['nu_ordem']
    dfs_operacoes.append(df_padronizado)

df_todas_operacoes = pd.concat(dfs_operacoes, ignore_index=True)
print(f"Total de operações locais acumuladas: {df_todas_operacoes.shape[0]} registros.\n")

# ==============================================================================
# 3. LEITURA DO GEOJSON E JUNÇÃO (MERGE)
# ==============================================================================
print("2/5. Carregando o GeoJSON de glebas...")
if not os.path.exists(CAMINHO_GEOJSON_GLEBAS):
    raise FileNotFoundError(f"O arquivo GeoJSON de glebas não foi localizado em: {CAMINHO_GEOJSON_GLEBAS}")

gdf_glebas = gpd.read_file(CAMINHO_GEOJSON_GLEBAS)
col_municipio_geojson = 'id_municipio'

if col_municipio_geojson not in gdf_glebas.columns:
    raise KeyError(f"A coluna '{col_municipio_geojson}' não foi encontrada no GeoJSON.")

gdf_glebas['chavenova'] = gdf_glebas['chavenova'].astype(str).str.strip()
print(f"GeoJSON carregado com {gdf_glebas.shape[0]} geometrias.")

print("3/5. Realizando o Join (Merge) na memória...")
gdf_unificado = gdf_glebas.merge(df_todas_operacoes, on='chavenova', how='inner')
print(f"Junção concluída! {gdf_unificado.shape[0]} glebas vinculadas.\n")

# ==============================================================================
# 4. AGRUPAMENTO ANUAL E MUNICIPAL
# ==============================================================================
print("4/5. Agrupando por Município e Ano...")

# Agrupamento duplo: Município + Ano
resumo_anual = gdf_unificado.groupby([col_municipio_geojson, 'ano']).agg(
    volume_total_credito=('vlr_recurso', 'sum'),
    quantidade_contratos=('chavenova', 'count')
).reset_index()

resumo_anual.rename(columns={col_municipio_geojson: 'cod_municipio'}, inplace=True)
resumo_anual['cod_municipio'] = resumo_anual['cod_municipio'].astype(str)

# Normalização Anual (Min-Max para cada ano individualmente)
# Isso permite comparar a posição relativa de um município dentro do mesmo ano
resumo_anual['indicador_fomento_normalizado'] = resumo_anual.groupby('ano')['volume_total_credito'].transform(
    lambda x: (x - x.min()) / (x.max() - x.min()) if (x.max() != x.min()) else 1.0
)

# ==============================================================================
# 5. GERANDO FORMATOS LONG E WIDE COM FORMATAÇÃO BRASILEIRA (EXCEL)
# ==============================================================================
print("5/5. Exportando tabelas formatadas para o padrão brasileiro do Excel...")

# Formato LONG (bom para Controlador Temporal no QGIS)
# Delimitador ';' e decimal ',' para o Excel abrir direto com clique duplo
resumo_anual.to_csv(CAMINHO_SAIDA_LONG, index=False, sep=';', decimal=',', encoding='utf-8-sig')
print(f" -> Arquivo LONG salvo em: {CAMINHO_SAIDA_LONG}")

# Formato WIDE (uma linha por município, colunas por ano - excelente para Joins normais e AHP)
# Criando as colunas pivotadas
pivot_volume = resumo_anual.pivot(index='cod_municipio', columns='ano', values='volume_total_credito').add_prefix('vol_')
pivot_contratos = resumo_anual.pivot(index='cod_municipio', columns='ano', values='quantidade_contratos').add_prefix('qtd_')
pivot_indicador = resumo_anual.pivot(index='cod_municipio', columns='ano', values='indicador_fomento_normalizado').add_prefix('ind_')

# Unindo os pivots em uma única tabela WIDE (1 linha por município)
resumo_wide = pd.concat([pivot_volume, pivot_contratos, pivot_indicador], axis=1).reset_index()

# Preenche municípios sem dados em anos específicos com 0
resumo_wide.fillna(0, inplace=True)

# Salva formato WIDE no padrão brasileiro
resumo_wide.to_csv(CAMINHO_SAIDA_WIDE, index=False, sep=';', decimal=',', encoding='utf-8-sig')
print(f" -> Arquivo WIDE salvo em: {CAMINHO_SAIDA_WIDE}")

print("\n--- PROCESSO CONCLUÍDO COM SUCESSO! ---")
print("Agora você possui duas bases de dados perfeitas para sua análise histórica!")
