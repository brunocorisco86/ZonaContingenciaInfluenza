# ZonaContingenciaInfluenza

Este repositório oferece ferramentas para a visualização e análise de zonas de contingência relacionadas à influenza aviária e a localização de granjas. O projeto inclui scripts para gerar arquivos KML/KMZ para uso em softwares como o Google Earth, e um aplicativo web interativo construído com Streamlit para análise em tempo real.

## Funcionalidades Principais

*   **Geração de Zonas de Contingência:** Cria zonas concêntricas (Perifoco, Vigilância, Proteção) ao redor de um ponto de foco definido.
*   **Mapeamento de Granjas:** Visualiza a localização de granjas a partir de dados CSV, com informações detalhadas para cada ponto.
*   **Aplicativo Web Interativo (Streamlit):**
    *   Mapa dinâmico com zonas de contingência e granjas.
    *   Entrada de coordenadas para definir o ponto de foco.
    *   Visualização do plano de contingência.
    *   Listagem e classificação de granjas por zona de contingência.
    *   Opções de exportação para HTML do mapa, relatórios em PDF e arquivos KML.
*   **Exportação de Dados:** Geração de arquivos KML/KMZ para visualização offline e relatórios detalhados.

## Estrutura do Projeto

*   `app.py`: O script principal do aplicativo web Streamlit.
*   `src/`: Contém os scripts Python para geração de KML/KMZ.
    *   `gerar_kml.py`: Gera o arquivo KML das zonas de contingência.
    *   `gerar_granja_kmz.py`: Gera o arquivo KMZ com os pontos das granjas.
*   `scripts/`: Contém scripts shell para automação.
    *   `package_kmz.sh`: Orquestra a execução dos scripts Python e empacota os KMLs em KMZs.
*   `data/`: Armazena arquivos de dados.
    *   `coordenadas.csv`: Dados das granjas.
    *   `coordenadas_abatedouro.txt`: Coordenadas padrão para o ponto de foco.
    *   `contexto_cvale.txt`: Informações de contexto.
*   `assets/`: Contém recursos visuais.
    *   `icone_frango.png`: Ícone personalizado para as granjas.
*   `docs/`: Documentação do projeto.
    *   `plano de contingencia.md`: Conteúdo do plano de contingência exibido no aplicativo web.
*   `output/`: Diretório para os arquivos KML/KMZ e relatórios gerados.
*   `requirements.txt`: Lista as dependências do Python.

## Como Usar

### Pré-requisitos

*   Python 3.x instalado.
*   Comando `zip` disponível no sistema (para empacotamento KMZ).

### Instalação das Dependências

É altamente recomendável criar um ambiente virtual antes de instalar as dependências:

```bash
python -m venv venv
source venv/bin/activate  # No Linux/macOS
# venv\Scripts\activate  # No Windows
pip install -r requirements.txt
```

### 1. Usando o Aplicativo Web Interativo (Streamlit)

Para iniciar o aplicativo web, execute o seguinte comando na raiz do projeto:

```bash
streamlit run app.py
```

Após a execução, o aplicativo será aberto automaticamente no seu navegador padrão. Você poderá:

*   **Definir o Foco:** Insira as coordenadas de latitude e longitude na barra lateral para centralizar as zonas de contingência.
*   **Navegar entre Abas:**
    *   **Mapa de Contingência:** Visualize o mapa interativo com as zonas e granjas.
    *   **Plano de Contingência:** Leia o plano de contingência detalhado.
    *   **Listas de Produtores:** Veja as granjas classificadas por zona, com dados agregados.
*   **Exportar:** Utilize os botões na barra lateral para baixar o mapa em HTML, relatórios em PDF ou HTML para impressão, e um arquivo KML completo.

### 2. Gerando Arquivos KML/KMZ via Scripts (Linha de Comando)

Para gerar os arquivos KML/KMZ diretamente, utilize o script `package_kmz.sh`. Este script orquestra a execução dos scripts Python e empacota os resultados.

Navegue até o diretório `scripts/` e execute o script:

```bash
cd scripts/
./package_kmz.sh
```

Você pode fornecer coordenadas para o ponto de foco de três maneiras:

1.  **Sem argumentos (usar padrão ou interativo):**
    ```bash
    ./package_kmz.sh
    ```
    O script perguntará pelas coordenadas ou usará as padrão se você deixar em branco.

2.  **Com um único argumento "latitude,longitude":**
    ```bash
    ./package_kmz.sh "-24.331062507879754,-53.85689460743224"
    ```

3.  **Com dois argumentos separados (latitude e longitude):**
    ```bash
    ./package_kmz.sh -24.331062507879754 -53.85689460743224
    ```

Os arquivos KMZ gerados (`zonas_contingencia.kmz` e `granjas.kmz`) serão salvos no diretório `output/`.