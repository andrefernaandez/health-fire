from datetime import datetime
import pandas as pd

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

        # Limpar as linhas do cabeçalho removendo os pontos e vírgulas
        header_lines = [line.replace(";", "").strip() for line in header_lines]

        # Extração dinâmica do ano baseado no cabeçalho
        periodo_info = header_lines[3]
        ano = periodo_info.split(":")[1].strip().split(";")[0]
        print(f"Ano detectado: {ano}")

        try:
            data = pd.read_csv(file_path, skiprows=4, encoding='utf-8', delimiter=';')
        except UnicodeDecodeError:
            data = pd.read_csv(file_path, skiprows=4, encoding='ISO-8859-1', delimiter=';')

        # Verifica as colunas detectadas no arquivo
        print("Colunas detectadas no CSV:", data.columns.tolist())

        # Remove a última linha (total) do DataFrame
        data = data.drop(data.index[-1])

        # considera que a linha 5 (índice 4) contém as unidades da federação
        unidade_federacao_col = data.columns[0]  # Primeira coluna com os dados das UFs
        if unidade_federacao_col.strip() != "Unidade da Federação":
            raise ValueError(
                f"A coluna não contém 'Unidade da Federação'. O nome encontrado foi '{unidade_federacao_col}'.")

        # Detecta dinamicamente as colunas de meses
        columns = data.columns
        year_columns = [
            col for col in columns
            if col.startswith(f"{ano}/") and any(mes in col for mes in MESES)
        ]

        # Filtra a primeira coluna e as colunas do ano atual
        filtered_data = data[[unidade_federacao_col] + year_columns]

        # Verifica se as colunas necessárias existem
        if unidade_federacao_col not in filtered_data.columns:
            raise ValueError(f"Coluna '{unidade_federacao_col}' não encontrada no arquivo.")
        if len(year_columns) < 12:
            raise ValueError("O arquivo não contém colunas suficientes para os meses do ano.")

        data_dicts = []
        for _, row in filtered_data.iterrows():
            for col in year_columns:
                mes = col.split("/")[1]  # Extrai o mês (por exemplo, "Jan", "Fev")
                mes_num = MESES.index(mes) + 1  # Converte o mês para número (1 para Jan, 2 para Fev, etc.)
                
                # Limpa os campos removendo qualquer ';'
                federative_unit = str(row[unidade_federacao_col]).replace(";", "").strip()
                value = str(row[col]).replace(";", "").strip()

                # Adiciona o valor limpo no dicionário
                try:
                    date_obj = datetime(year=int(ano), month=mes_num, day=1).date()
                except ValueError:
                    raise ValueError(f"Erro ao criar a data para {ano}-{mes_num}-01.")

                data_dicts.append({
                    "unidade_federacao": federative_unit,
                    "data": date_obj,  # Primeiro dia de cada mês
                    "valor": value  # Armazena o valor da coluna também
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
