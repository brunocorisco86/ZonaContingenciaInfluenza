# Próximos Passos: Criação de um Aplicativo Web com Streamlit

Este documento descreve o plano para converter os scripts de geração de KML existentes em um aplicativo web interativo usando Streamlit, para visualização e gerenciamento de zonas de contingência para influenza aviária.

## 1. Configuração do Projeto e Dependências

- **Criar um novo script Python para o aplicativo Streamlit:** `app.py`.
- **Instalar as bibliotecas necessárias:** Criar ou atualizar o arquivo `requirements.txt` com as seguintes dependências:
  - `streamlit`
  - `pandas`
  - `geopandas`
  - `folium`
  - `streamlit-folium`
  - `pyproj`

## 2. Estrutura e Interface do Usuário (UI)

- **Layout Principal:** Utilizar um layout de duas colunas.
  - **Barra Lateral (`st.sidebar`):** Conterá as entradas do usuário e os controles da aplicação.
  - **Painel Principal:** Exibirá o mapa interativo e informações contextuais.

- **Componentes da Barra Lateral:**
  - **Entrada de Coordenadas:**
    - Dois campos `st.number_input` para Latitude e Longitude.
    - Definir os valores padrão como `-24.33135069928127` (Latitude) e `-53.85542105733513` (Longitude).
  - **Exibição de Contexto:**
    - Um botão ou `st.expander` para exibir os detalhes do plano de contingência, lidos de `docs/plano de contingencia.md`.
  - **Botão de Exportação:**
    - Um `st.download_button` para permitir que os usuários baixem o arquivo KML/KMZ gerado.

- **Componentes do Painel Principal:**
  - **Abas (`st.tabs`):**
    - **Aba 1: "Mapa de Contingência"**: Exibirá o mapa interativo gerado com Folium.
    - **Aba 2: "Plano de Contingência"**: Exibirá o texto completo do arquivo `docs/plano de contingencia.md`.

## 3. Implementação da Funcionalidade Principal

### 3.1. Carregamento de Dados
- Criar uma função para carregar e armazenar em cache os dados das granjas a partir de `data/coordenadas.csv` usando `pandas.read_csv`.
- Utilizar o decorador `@st.cache_data` para otimizar o carregamento dos dados, evitando recarregamentos a cada interação.
- Realizar a limpeza e o tratamento das coordenadas, garantindo que valores ausentes ou mal formatados sejam tratados.

### 3.2. Geração do Mapa (com Folium)
- **Inicializar o Mapa:** Criar um objeto `folium.Map` centrado nas coordenadas padrão.
- **Marcar os Pontos das Granjas:**
  - Iterar sobre o DataFrame do pandas com os dados das granjas.
  - Para cada granja, adicionar um `folium.Marker` ou `folium.CircleMarker` ao mapa.
  - Utilizar os detalhes da granja (proprietário, cidade, etc.) para criar um popup informativo para cada marcador.
- **Desenhar os Círculos de Contingência:**
  - Reutilizar a lógica de geração de círculos do script `src/gerar_kml.py`.
  - Criar uma função que, a partir de uma coordenada central e um raio em metros, desenhe um `folium.Circle` no mapa.
  - Desenhar os três círculos (Perifoco, Vigilância e Proteção) com os raios e cores corretos (vermelho, roxo e azul, com transparência).
- **Exibir o Mapa:** Renderizar o mapa no aplicativo Streamlit usando a função `st_folium` da biblioteca `streamlit-folium`.

### 3.3. Funcionalidade de Exportação (KML/KMZ)
- **Adaptar os Scripts Existentes:** Converter a lógica dos scripts `gerar_kml.py` e `gerar_granja_kmz.py` em funções que possam ser chamadas pelo aplicativo Streamlit.
- **Gerar Arquivos em Memória:** Quando o usuário clicar no botão de download:
  1. Chamar as funções adaptadas para gerar o conteúdo KML das zonas e das granjas como strings.
  2. Utilizar a lógica do `merge_kml.py` para combinar as strings em um único conteúdo KML.
  3. Disponibilizar a string KML final para download através do `st.download_button`.
  4. Como alternativa para KMZ, criar o arquivo em memória usando `zipfile` e `io.BytesIO`, empacotando os KMLs e o ícone, e disponibilizá-lo para download.

## 4. Informações Contextuais
- Criar uma função para ler o conteúdo do arquivo `docs/plano de contingencia.md`.
- Exibir o conteúdo lido na aba "Plano de Contingência" e/ou em um `st.expander` na barra lateral, utilizando `st.markdown()` para uma formatação adequada.

## 5. Refinamento e Implantação
- Refinar a interface para melhorar a experiência do usuário.
- Adicionar tratamento de erros para o carregamento de arquivos e a entrada de coordenadas.
- Escrever instruções claras sobre como executar o aplicativo (`streamlit run app.py`).
- Considerar opções de implantação, como o Streamlit Community Cloud.
