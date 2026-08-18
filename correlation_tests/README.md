# Testes de correlacao

Esta pasta concentra os testes de correlacao Pearson e Spearman entre:

- registros de queimadas do INPE salvos em `Burned`
- registros de saude do DATASUS/TABNET salvos em `DiseaseCase`

SIVEP-SRAG nao e usado aqui.

## Como a analise funciona

1. Agrupa os registros do INPE por mes e UF.
2. Usa os registros de `DiseaseCase` como ja estao salvos: mes, UF, CID e tipo de dado.
3. Filtra `DiseaseCase` por `cid_id=38` e `type_health_id=43`.
4. Cruza as duas fontes pelo mesmo mes e UF.
5. Calcula os coeficientes Pearson e Spearman.

Os arquivos de saida sao criados em `correlation_tests/results/`.

## Como rodar no VSCode

1. Abra a pasta do projeto `healthfire` no VSCode.
2. Abra o terminal integrado do VSCode.
3. Confirme que o terminal esta na raiz do projeto.
4. Rode:

```powershell
venv\Scripts\python.exe -m correlation_tests.run_correlations
```

Para validar se esta funcionando corretamente, rode:

```powershell
venv\Scripts\python.exe -m correlation_tests.validate_results
```

Se estiver tudo certo, o validador imprime `Correlation validation passed`.

## Comando principal

```bash
python -m correlation_tests.run_correlations
```

Por padrao, a analise usa o periodo completo de 2015 a 2025, considera apenas `cid_id=38` e `type_health_id=43`.

Filtros uteis:

```bash
python -m correlation_tests.run_correlations --federative-units "Acre,Amazonas"
```

Para testar um efeito com atraso apos as queimadas, use `--lag-months`.
Por exemplo, `--lag-months 1` compara queimadas de um mes com dados de saude do mes seguinte.

```bash
python -m correlation_tests.run_correlations --lag-months 1
```

## Arquivos gerados

- `correlation_results.csv`: coeficientes Pearson e Spearman.
- `aligned_monthly_data.csv`: dados mensais usados no calculo.

## Como saber se funcionou

O teste esta funcionando quando:

- `validate_results.py` imprime `Correlation validation passed`.
- `correlation_results.csv` tem linhas para `pearson` e `spearman`.
- `sample_size` e maior que zero.
- `coefficient` esta entre `-1` e `1`.
- `aligned_monthly_data.csv` contem `period`, `federative_unit`, `burned_count`, `health_cases` e `cid_id`.
- `cid_id` aparece apenas como `38`.
- `type_health_id` aparece apenas como `43`.
