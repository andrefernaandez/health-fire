# Health-Fire: Integração e Análise de Dados sobre Queimadas e Saúde Respiratória no Brasil (2015-2025)

## Descrição

O **Health-Fire** é um projeto de integração, modelagem e análise de dados públicos sobre focos de queimadas e indicadores de saúde respiratória no Brasil. O estudo considera o período de **2015 a 2025** e foi desenvolvido com foco em Engenharia de Dados, Data Mart, processamento de dados e visualização analítica em Power BI.

O projeto integra dados de queimadas do INPE/BDQueimadas com registros de internações hospitalares do SIH/SUS-DATASUS e registros epidemiológicos do SIVEP-Gripe. A partir dessas fontes, os dados são tratados, padronizados, agregados e consolidados em um Data Mart orientado à análise de indicadores ambientais e de saúde pública.

## Objetivo

Construir uma solução analítica capaz de integrar bases públicas heterogêneas, estruturar os dados em modelo dimensional e apoiar a análise exploratória da relação entre queimadas e indicadores respiratórios no Brasil.

O painel desenvolvido permite investigar os dados por ano, mês, região, unidade federativa, bioma e grupos de doenças respiratórias, além de apoiar a validação dos resultados com fontes oficiais e análises complementares de correlação.

## Fontes de Dados

- **INPE/BDQueimadas**: focos de queimadas, bioma, unidade federativa e variáveis ambientais associadas.
- **SIH/SUS-DATASUS**: internações hospitalares, óbitos e taxa de mortalidade por doenças do aparelho respiratório.
- **SIVEP-Gripe**: registros epidemiológicos de SRAG, utilizados como fonte complementar para contextualizar o período da pandemia de COVID-19.

## Estrutura do Projeto

### Aplicação

- Projeto Django responsável pela organização da aplicação e dos módulos de importação.
- Módulos de domínio para dados de queimadas, saúde, localização geográfica e importação de arquivos.

### Processamento e ETL

- Rotinas em Python/Django responsáveis pela importação, tratamento inicial e padronização das bases públicas.
- Transformações no Pentaho Data Integration (Kettle) utilizadas principalmente para agregação, consolidação e carga das dimensões e tabelas fato no Data Mart.
- Organização dos dados para análise OLAP e consumo pelo dashboard em Power BI.

### Data Mart

- Modelo dimensional voltado para análise OLAP.
- Dimensões de tempo, localidade, bioma e CID.
- Tabelas fato para consolidação dos indicadores de queimadas, internações, óbitos, SIVEP-Gripe e análises por CID.

### Dashboard Power BI

- Painel interativo para exploração dos indicadores.
- Visualizações por período, região, estado, bioma e CID.
- Comparações entre DATASUS, SIVEP-Gripe e queimadas.
- Apoio à validação dos resultados com fontes oficiais.
- [Acessar dashboard](https://app.powerbi.com/view?r=eyJrIjoiZDk0MGE2NzMtOTAzYi00YmI5LTlkODAtNjQyZGYxM2NhZDQ4IiwidCI6ImY5MTQ5YTgzLTM5MjAtNDFiZS04YjU2LTdjYWQyMzY4MGE2YSJ9)

### Análises Complementares

- Scripts em Python para testes de correlação.
- Cálculo dos coeficientes de Pearson e Spearman.
- Geração de bases alinhadas para análise temporal dos indicadores.

## Principais Indicadores

- Total de focos de queimadas.
- Internações por doenças do aparelho respiratório.
- Internações por grupos específicos de CID.
- Óbitos e taxa de mortalidade.
- Casos e óbitos por SRAG/COVID-19 e SRAG não COVID-19.
- Correlação entre focos de queimadas e internações respiratórias.
Acesse o dashboard interativo publicado no Power BI Service (https://app.powerbi.com/view?r=eyJrIjoiZmM0MzZmODMtNDE4My00YjFhLThiZDgtZmIwMWM2NzNhMmEwIiwidCI6ImY5MTQ5YTgzLTM5MjAtNDFiZS04YjU2LTdjYWQyMzY4MGE2YSJ9).


## Tecnologias Utilizadas

- Python
- Django
- PostgreSQL
- Pentaho Data Integration (Kettle)
- Power BI

## Organização Geral

- `burned/`: módulo relacionado aos dados de queimadas.
- `disease_cases/`: módulo relacionado aos dados de internações e saúde.
- `geo_data/`: dados geográficos e unidades federativas.
- `health/`: cadastros e tipos de conteúdo de saúde.
- `importer/`: rotinas de importação e processamento.
- `data_mart/`: transformações do Pentaho para agregação e carga do Data Mart.
- `dashboard/`: arquivos relacionados ao painel analítico.
- `correlation_tests/`: scripts e resultados dos testes de correlação.
- `uploads/`: arquivos de entrada utilizados no processo de carga.

## Observações

As bases públicas utilizadas no projeto podem ser obtidas nas fontes oficiais indicadas no trabalho acadêmico. Arquivos brutos de grande volume não são versionados diretamente neste repositório.

## Autor

André Fernandes  
[GitHub](https://github.com/andrefernaandez)