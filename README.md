# Health-Fire: Análise de Queimadas e Saúde Respiratória no Brasil (2019–2024)

## Descrição do Projeto
Este projeto integra dados de queimadas (INPE) e dados de saúde respiratória (DATASUS) para analisar os impactos ambientais e de saúde pública no Brasil no período de 2019 a 2024.

O objetivo é oferecer insights por meio de análises e visualizações interativas para apoiar decisões em políticas públicas ambientais e de saúde.

## Estrutura do Projeto

### Modelos de Dados
- Diagramas relacionais e tabelas usadas no banco de dados.
- Modelo dimensional para análise OLAP.

### Plano de Carga (ETL)
- Transformações e Jobs desenvolvidos no Pentaho Data Integration para importar, limpar, agregar e carregar os dados no banco.

### Aplicação OLAP (Dashboard Power BI)
- Dashboard interativo desenvolvido no Power BI.
- Visualizações das principais métricas: focos de queimadas, internações, óbitos, taxa de mortalidade, correlações e análises por bioma, estado e tempo.

## Como Rodar o Projeto

### Banco de Dados
- Scripts para criar tabelas e inserir dados disponíveis na pasta `/db-scripts`.

### ETL Pentaho
- Transformações para carregar dados na pasta `/etl`.

### Power BI
- Arquivo Power BI Desktop (`.pbix`) disponível em `/powerbi`.
- Para acessar a versão online publicada, use o link abaixo.

## Dashboard Online

Acesse o dashboard interativo publicado no Power BI Service [indisponível).

## Tecnologias Utilizadas
- PostgreSQL + pgAdmin
- Pentaho Data Integration (Kettle)
- Power BI
- Python (para análises complementares)

## Autor
André Fernandes  
[GitHub](https://github.com/andrefernaandez)



