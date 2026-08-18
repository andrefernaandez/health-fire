from datetime import datetime
import pandas as pd

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
            data = pd.read_csv(file_path, skiprows=4, encoding="utf-8-sig", delimiter=";")
        except UnicodeDecodeError:
            data = pd.read_csv(file_path, skiprows=4, encoding="ISO-8859-1", delimiter=";")

        print("Colunas detectadas no CSV:", data.columns.tolist())

        data = data.drop(data.index[-1])
        unidade_federacao_col = data.columns[0]

        if unidade_federacao_col.strip() != UNIDADE_FEDERACAO:
            raise ValueError(
                f"A coluna não contém '{UNIDADE_FEDERACAO}'. Encontrado: '{unidade_federacao_col}'"
            )

        year_columns = [
            col for col in data.columns
            if col.startswith(f"{ano}/") and any(mes in col for mes in MESES)
        ]

        if len(year_columns) == 0:
            raise ValueError("Nenhuma coluna de meses encontrada para o ano.")

        data_dicts = []

        for _, row in data.iterrows():
            federative_unit_name = str(row[unidade_federacao_col]).strip()

            if pd.isna(federative_unit_name) or federative_unit_name == "" or federative_unit_name.lower() == "nan":
                continue

            for col in year_columns:
                mes = col.split("/")[1]
                mes_num = MESES.index(mes) + 1
                value = str(row[col]).replace(";", "").strip()

                try:
                    date_obj = datetime(
                        year=int(ano),
                        month=mes_num,
                        day=1
                    ).date()
                except ValueError:
                    raise ValueError(f"Data inválida: {ano}-{mes_num}-01")

                data_dicts.append({
                    "unidade_federacao": federative_unit_name,
                    "data": date_obj,
                    "valor": value
                })

        print(f"Quantidade de registros processados: {len(data_dicts)}")

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
        data = pd.read_csv(file_path, encoding="utf-8", delimiter=";", usecols=[
            "DataHora", "Satelite", "Municipio", "Estado", "Bioma", "DiaSemChuva",
            "Precipitacao", "RiscoFogo", "Latitude", "Longitude", "FRP"
        ])

        print(data[["Municipio", "Estado", "Bioma"]].isna().sum())

        correcoes = {
            "âˆšÃ‰": "Ãƒ", "âˆšÃ¢": "Ã‰", "âˆšÃ…": "Ã", "âˆšÂ¥": "Ã”", "âˆšÃ¬": "Ã“",
            "âˆšÃ§": "Ã", "âˆšÃ‡": "Ã‚", "âˆšÃ¤": "ÃŠ", "âˆšÃ¡": "Ã‡", "âˆšÃ¶": "Ãš",
            "âˆšÂ¢": "Ã¢", "âˆšÃ®": "Ã”",
        }

        colunas = ["Municipio", "Bioma", "Estado"]

        for coluna in colunas:
            for errado, certo in correcoes.items():
                data[coluna] = data[coluna].str.replace(errado, certo)

        data_dicts = []

        for _, row in data.iterrows():
            data_dicts.append({
                "register_at": row["DataHora"],
                "satellite": row["Satelite"],
                "city": row["Municipio"],
                "federative_unit": row["Estado"],
                "biome": row["Bioma"],
                "no_rain_days": row["DiaSemChuva"],
                "precipitation": row["Precipitacao"],
                "fire_risk": row["RiscoFogo"],
                "latitude": row["Latitude"],
                "longitude": row["Longitude"],
                "frp": row["FRP"],
            })

        if data_dicts:
            print("Exemplo de registro salvo no dicionário:", data_dicts[0])

        print(f"Total de registros processados: {len(data_dicts)}")

        return {"data": data_dicts}

    except Exception as e:
        raise ValueError(f"Erro ao processar o arquivo de queimadas: {e}")





SIVEP_COLUMNS = [
    "NU_NOTIFIC",
    "DT_INTERNA",
    "SG_UF",
    "CO_MUN_RES",
    "CLASSI_FIN",
    "EVOLUCAO",
    "CS_SEXO",
    "NU_IDADE_N",
]


def _read_csv_with_fallback(file_path, **kwargs):
    for encoding in ("utf-8-sig", "ISO-8859-1"):
        try:
            return pd.read_csv(file_path, encoding=encoding, **kwargs)
        except UnicodeDecodeError:
            continue

    return pd.read_csv(file_path, encoding="utf-8", **kwargs)


def _empty_to_none(value):
    if pd.isna(value):
        return None

    value = str(value).strip()

    if value == "" or value.lower() in ("nan", "none"):
        return None

    return value


def _parse_int(value):
    value = _empty_to_none(value)

    if value is None:
        return None

    value = str(value).strip()

    # remove espaços
    value = value.replace(" ", "")

    # corrige formato BR científico: 3,15478E+11 → 3.15478E+11
    value = value.replace(",", ".")

    try:
        return int(float(value))
    except Exception:
        return None


def _parse_date(value):
    value = _empty_to_none(value)

    if value is None:
        return None

    parsed = pd.to_datetime(value, dayfirst=True, errors="coerce")

    if pd.isna(parsed):
        return None

    return parsed.date()



def process_sivep_srag_file(file_path):
    try:
        data = _read_csv_with_fallback(
            file_path,
            delimiter=";",
            dtype=str,
            usecols=lambda col: col.strip().upper() in SIVEP_COLUMNS
        )

        data.columns = [c.strip().upper() for c in data.columns]

        missing = [c for c in SIVEP_COLUMNS if c not in data.columns]
        if missing:
            raise ValueError(f"Colunas ausentes: {missing}")

        data_dicts = []

        for _, row in data.iterrows():
            try:
                nu_notific_raw = row.get("NU_NOTIFIC")

                nu_notific = _parse_int(nu_notific_raw)
                sg_uf = _empty_to_none(row.get("SG_UF"))

                # regra mínima obrigatória
                if not nu_notific or not sg_uf:
                    continue

                data_dicts.append({
                    "nu_notific": nu_notific,
                    "dt_interna": _parse_date(row.get("DT_INTERNA")),
                    "sg_uf": sg_uf[:2].upper(),
                    "co_mun_res": _parse_int(row.get("CO_MUN_RES")),
                    "classi_fin": _parse_int(row.get("CLASSI_FIN")),
                    "evolucao": _parse_int(row.get("EVOLUCAO")),
                    "cs_sexo": (_empty_to_none(row.get("CS_SEXO")) or "")[:1].upper() or None,
                    "nu_idade_n": _parse_int(row.get("NU_IDADE_N")),
                })

            except Exception as e:
                print(f"Linha ignorada por erro: {e}")

        print(f"TOTAL PROCESSADO SIVEP: {len(data_dicts)}")

        return {"data": data_dicts}

    except Exception as e:
        raise ValueError(f"Erro SIVEP: {e}")
    



    
