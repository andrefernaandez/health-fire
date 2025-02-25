from datetime import datetime
import pandas as pd
import unicodedata

UNIDADE_FEDERACAO = "Unidade da Federação"
MESES = [
    "Jan", "Fev", "Mar", "Abr", "Mai", "Jun",
    "Jul", "Ago", "Set", "Out", "Nov", "Dez"
]

def process_health_file(file_path):
    try:
        with open(file_path, "r") as file:
            header_lines = [next(file).strip() for _ in range(4)]
        
        header_lines = [line.replace(";", "").strip() for line in header_lines]
        periodo_info = header_lines[3]
        ano = periodo_info.split(":")[1].strip().split(";")[0]
        print(f"Ano detectado: {ano}")

        try:
            data = pd.read_csv(file_path, skiprows=4, encoding='utf-8', delimiter=';')
        except UnicodeDecodeError:
            data = pd.read_csv(file_path, skiprows=4, encoding='ISO-8859-1', delimiter=';')
        
        print("Colunas detectadas no CSV:", data.columns.tolist())
        data = data.drop(data.index[-1])
        unidade_federacao_col = data.columns[0]  
        if unidade_federacao_col.strip() != "Unidade da Federação":
            raise ValueError(
                f"A coluna não contém 'Unidade da Federação'. O nome encontrado foi '{unidade_federacao_col}'.")
        
        columns = data.columns
        year_columns = [
            col for col in columns
            if col.startswith(f"{ano}/") and any(mes in col for mes in MESES)
        ]
        
        filtered_data = data[[unidade_federacao_col] + year_columns]
        
        if unidade_federacao_col not in filtered_data.columns:
            raise ValueError(f"Coluna '{unidade_federacao_col}' não encontrada no arquivo.")
        if len(year_columns) < 12:
            raise ValueError("O arquivo não contém colunas suficientes para os meses do ano.")
        
        data_dicts = []
        for _, row in filtered_data.iterrows():
            for col in year_columns:
                mes = col.split("/")[1]  
                mes_num = MESES.index(mes) + 1  
                
                federative_unit = str(row[unidade_federacao_col]).replace(";", "").strip()
                value = str(row[col]).replace(";", "").strip()
                
                try:
                    date_obj = datetime(year=int(ano), month=mes_num, day=1).date()
                except ValueError:
                    raise ValueError(f"Erro ao criar a data para {ano}-{mes_num}-01.")
                
                data_dicts.append({
                    "unidade_federacao": federative_unit,
                    "data": date_obj,
                    "valor": value  
                })

        return {
            "header_info": {
                "contexto": header_lines[0],
                "tipo_dado": header_lines[1],
                "cid_capitulo": header_lines[2],
                "periodo": header_lines[3],
            },
            "data": data_dicts
        }
    except Exception as e:
        raise ValueError(f"Erro ao processar o arquivo: {e}")









def process_burned_file(file_path):
    try:
        # Leitura do arquivo CSV, ignorando as colunas "Pais" e "Estado"
        data = pd.read_csv(file_path, encoding='utf-8', delimiter=';', usecols=[
            "DataHora", "Satelite", "Municipio", "Bioma", "DiaSemChuva",
            "Precipitacao", "RiscoFogo", "Latitude", "Longitude", "FRP"
        ])

        # Verifica quantos valores NaN existem nas colunas Municipio e Bioma
        print(data[['Municipio', 'Bioma']].isna().sum())

        correcoes = {
            "√É": "Ã", "√â": "É", "√Å": "Á", "√¥": "Ô", "√ì": "Ó",
            "√ç": "Í", "√Ç": "Â", "√ä": "Ê", "√á": "Ç", "√ö": "Ú",
            "√¥": "ô", "√¢": "â", "√î": "Ô",
        }

        # Lista de colunas a serem corrigidas (apenas as utilizadas)
        colunas = ["Municipio", "Bioma"]

        # Aplica as correções
        for coluna in colunas:
            for errado, certo in correcoes.items():
                data[coluna] = data[coluna].str.replace(errado, certo)

        # Lista para armazenar os dicionários de dados
        data_dicts = []

        # Processamento das linhas do arquivo CSV
        for _, row in data.iterrows():
            data_dicts.append({
                "register_at": row["DataHora"],
                "satellite": row["Satelite"],
                "city": row["Municipio"],
                "biome": row["Bioma"],
                "no_rain_days": row["DiaSemChuva"],
                "precipitation": row["Precipitacao"],
                "fire_risk": row["RiscoFogo"],
                "latitude": row["Latitude"],
                "longitude": row["Longitude"],
                "frp": row["FRP"],
            })

        # Exibe um exemplo de dado salvo
        if data_dicts:
            print("Exemplo de registro salvo no dicionário:", data_dicts[0])

        print(f"Total de registros processados: {len(data_dicts)}")

        return {"data": data_dicts}

    except Exception as e:
        raise ValueError(f"Erro ao processar o arquivo de queimadas: {e}")
