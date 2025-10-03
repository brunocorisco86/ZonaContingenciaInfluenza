# Zonas de Contingência de Influenza

Este repositório contém scripts para gerar e empacotar arquivos KML/KMZ para visualização de zonas de contingência relacionadas à influenza aviária, centradas em um ponto de foco (por exemplo, um abatedouro).

## Conteúdo

*   `gerar_kml.py`: Script Python para gerar o arquivo KML com as zonas de contingência.
*   `package_kmz.sh`: Script Shell para empacotar o arquivo KML em um arquivo KMZ.
*   `zonas_contingencia.kml`: Arquivo KML gerado pelo script Python (saída).
*   `zonas_contingencia.kmz`: Arquivo KMZ empacotado pelo script Shell (saída).
*   `coordenadas_abatedouro.txt`: (Assumido) Arquivo de texto contendo as coordenadas padrão do abatedouro.
*   `coordenadas.csv`: (Assumido) Arquivo CSV com coordenadas adicionais.
*   `contexto_cvale.txt`: (Assumido) Arquivo de texto com contexto sobre a C.Vale.
*   `Manual_de_Identidade_Logo_CVale_Jul22.pdf`: (Assumido) Manual de identidade da C.Vale.
*   `plano de contingencia.md`: (Assumido) Documento Markdown com o plano de contingência.
*   `zonas de contencao_influenza.pdf`: (Assumido) Documento PDF sobre zonas de contenção.
*   `2002611.png`: (Assumido) Imagem relacionada.

## `gerar_kml.py` - Gerador de KML

Este script Python é responsável por criar um arquivo KML (`zonas_contingencia.kml`) que define três zonas circulares de contingência ao redor de um ponto central.

### Funcionalidades:

*   **Geração de Zonas:** Cria três zonas concêntricas com base em raios predefinidos:
    *   **PROTEÇÃO:** 15 km de raio.
    *   **VIGILANCIA:** 7 km de raio.
    *   **PERIFOCO:** 3 km de raio.
*   **Estilização:** Cada zona possui uma descrição específica e é estilizada com cores distintas (azul C.Vale, azul claro C.Vale e amarelo) para linhas e preenchimento.
*   **Ponto de Foco:**
    *   Por padrão, o ponto central (foco) é definido pelas coordenadas do "Complexo Agroindustrial Abatedouro de Aves C.Vale".
    *   **Personalização:** Permite que o usuário forneça coordenadas de latitude e longitude via argumentos de linha de comando para definir um ponto de foco personalizado.
*   **Placemark de Foco:** Adiciona um marcador visual para o ponto de foco no KML, utilizando um ícone de "atenção".
*   **Saída:** Gera o arquivo `zonas_contingencia.kml`, que pode ser visualizado em softwares como o Google Earth.

### Como usar:

```bash
python gerar_kml.py
# Ou com coordenadas personalizadas:
python gerar_kml.py <latitude> <longitude>
```

Exemplo:
```bash
python gerar_kml.py -24.33160375868075 -53.85489414802796
```

## `package_kmz.sh` - Empacotador de KMZ

Este script Shell é usado para compactar o arquivo KML gerado em um formato KMZ, que é um arquivo KML compactado e mais fácil de distribuir.

### Funcionalidades:

*   **Verificação de KML:** Garante que o arquivo `zonas_contingencia.kml` exista antes de tentar empacotá-lo.
*   **Remoção de KMZ Antigo:** Remove qualquer arquivo `zonas_contingencia.kmz` existente para evitar conflitos e garantir que um novo seja criado.
*   **Compactação:** Utiliza o comando `zip` para criar o arquivo `zonas_contingencia.kmz` a partir do `zonas_contingencia.kml`.
*   **Feedback:** Informa o usuário sobre o sucesso ou falha do processo de empacotamento.

### Como usar:

```bash
bash package_kmz.sh
```
