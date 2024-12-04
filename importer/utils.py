import pandas as pd

# Constantes com os nomes das colunas
UNIDADE_FEDERACAO = "Unidade da Federação"
MESES = [
    "Jan", "Fev", "Mar", "Abr", "Mai", "Jun", 
    "Jul", "Ago", "Set", "Out", "Nov", "Dez"
]

def process_health_file(file_path):
    try:
        # Ler as primeiras 4 linhas separadamente para capturar informações adicionais
        with open(file_path, "r") as file:
            header_lines = [next(file).strip() for _ in range(4)]

        # Extração dinâmica do ano baseado no cabeçalho
        periodo_info = header_lines[3]
        ano = periodo_info.split(":")[1].strip().split(";")[0]
        print(f"Ano detectado: {ano}")


        try:
            data = pd.read_csv(file_path, skiprows=4, encoding='utf-8', delimiter=';')
        except UnicodeDecodeError:
            data = pd.read_csv(file_path, skiprows=4, encoding='ISO-8859-1', delimiter=';')

        # Log para verificar colunas detectadas
        print("Colunas detectadas no CSV:", data.columns.tolist())

        # Verifica se a primeira coluna contém 'Unidade da Federação'
        if data.columns[0].strip() != UNIDADE_FEDERACAO:
            raise ValueError(f"A primeira coluna não contém '{UNIDADE_FEDERACAO}'. O nome encontrado foi '{data.columns[0]}'.")

        # Detecta dinamicamente as colunas de meses
        columns = data.columns
        year_columns = [
         col for col in columns 
        if col.startswith(f"{ano}/") and any(mes in col for mes in MESES)
]


        # Log para verificar as colunas filtradas
        print(f"Colunas filtradas para {ano}: {year_columns}")

        # Filtra a primeira coluna e as colunas do ano atual
        filtered_data = data[[UNIDADE_FEDERACAO] + year_columns]

        # Verifica se as colunas necessárias existem
        if UNIDADE_FEDERACAO not in filtered_data.columns:
            raise ValueError(f"Coluna '{UNIDADE_FEDERACAO}' não encontrada no arquivo.")
        if len(year_columns) < 12:
            raise ValueError("O arquivo não contém colunas suficientes para os meses do ano.")

        # Converter os dados para uma estrutura adequada
        data_dicts = [
            {
                UNIDADE_FEDERACAO: row[UNIDADE_FEDERACAO],
                **{col: row[col] for col in year_columns}
            }
            for _, row in filtered_data.iterrows()
        ]

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
