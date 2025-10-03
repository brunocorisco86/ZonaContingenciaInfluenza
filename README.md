# ZonaContingenciaInfluenza

Este repositório contém scripts para gerar e empacotar arquivos KML/KMZ para visualização de zonas de contingência relacionadas à influenza aviária e pontos de granjas, centrados em um ponto de foco (por exemplo, um abatedouro).

## Estrutura do Projeto

O projeto está organizado nas seguintes pastas:

*   `src/`: Contém os scripts Python principais para geração de KML.
*   `scripts/`: Contém scripts shell para automação de tarefas.
*   `data/`: Armazena arquivos de dados, como `coordenadas.csv`.
*   `assets/`: Contém recursos visuais, como ícones.
*   `docs/`: Documentação do projeto.
*   `output/`: Diretório para os arquivos KML/KMZ gerados.
*   `.gitignore`: Define arquivos e diretórios a serem ignorados pelo Git.
*   `requirements.txt`: Lista as dependências do Python.

## Scripts

### `src/gerar_kml.py` - Gerador de Zonas de Contingência KML

Este script Python é responsável por criar um arquivo KML (`zonas_contingencia.kml`) que define três zonas circulares de contingência ao redor de um ponto central.

#### Funcionalidades:

*   **Geração de Zonas:** Cria três zonas concêntricas com base em raios predefinidos:
    *   **PROTEÇÃO:** 15 km de raio.
    *   **VIGILANCIA:** 7 km de raio.
    *   **PERIFOCO:** 3 km de raio.
*   **Estilização:** Cada zona possui uma descrição específica e é estilizada com cores distintas (azul C.Vale, azul claro C.Vale e amarelo) para linhas e preenchimento.
*   **Ponto de Foco:**
    *   Por padrão, o ponto central (foco) é definido pelas coordenadas do "Complexo Agroindustrial Abatedouro de Aves C.Vale".
    *   **Personalização:** Permite que o usuário forneça coordenadas de latitude e longitude via argumentos de linha de comando (como uma string "latitude,longitude" ou dois argumentos separados) para definir um ponto de foco personalizado.
*   **Placemark de Foco:** Adiciona um marcador visual para o ponto de foco no KML, utilizando um ícone de "atenção".
*   **Saída:** Gera o arquivo `zonas_contingencia.kml` no diretório `output/`, que pode ser visualizado em softwares como o Google Earth.

### `src/gerar_granja_kmz.py` - Gerador de Pontos de Granjas KMZ

Este script Python lê o arquivo `data/coordenadas.csv` e gera um arquivo KMZ (`granjas.kmz`) contendo pontos para cada granja.

#### Funcionalidades:

*   **Leitura de Dados:** Lê as informações das granjas do arquivo `data/coordenadas.csv`.
*   **Remoção de Duplicatas:** Remove entradas duplicadas com base na coluna 'nucleo'.
*   **Geração de Pontos:** Para cada granja única, um Placemark é criado no KML.
*   **Informações Detalhadas:** Cada Placemark inclui uma descrição detalhada em formato de tabela HTML, contendo todas as informações da linha correspondente do CSV.
*   **Ícone Personalizado:** Utiliza o ícone `assets/icone_frango.png` para representar as granjas no mapa, com escala de 0.8. O ícone é empacotado diretamente no KMZ para garantir a visualização.
*   **Rótulos Ocultos:** Os pontos são exibidos sem rótulos visíveis no mapa, mas o nome do Placemark (visível na lista de itens do Google Earth) é definido como o 'Proprietario' da granja.
*   **Saída:** Gera o arquivo `granjas.kml` e o empacota junto com o ícone `icone_frango.png` em `granjas.kmz`, ambos no diretório `output/`.

### `scripts/package_kmz.sh` - Orquestrador de Geração de KMZ

Este script shell automatiza a execução dos scripts Python para gerar os arquivos KML/KMZ.

#### Funcionalidades:

*   **Geração de Zonas:** Executa `src/gerar_kml.py` para criar o `zonas_contingencia.kml`.
*   **Geração de Granjas:** Executa `src/gerar_granja_kmz.py` para criar `granjas.kml` e `granjas.kmz`.
*   **Empacotamento:** Compacta o `zonas_contingencia.kml` em `zonas_contingencia.kmz`. O `granjas.kmz` é gerado diretamente pelo script Python correspondente.
*   **Entrada de Coordenadas:** Permite a entrada de coordenadas para `gerar_kml.py` via linha de comando ou interativamente.
*   **Feedback:** Fornece mensagens detalhadas sobre o progresso e o local de salvamento dos arquivos gerados.

## Como Usar

### Pré-requisitos

*   Python 3 instalado.
*   Comando `zip` disponível no sistema.

### Geração de Zonas de Contingência e Pontos de Granjas

Para gerar os arquivos KMZ, execute o script `package_kmz.sh` a partir do diretório `scripts/`:

```bash
cd scripts/
./package_kmz.sh
```

Você pode fornecer coordenadas para o script `gerar_kml.py` (que é chamado por `package_kmz.sh`) de três maneiras:

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