#!/bin/bash
# Script to generate a KML file and then package it into a KMZ archive.

# Define file paths relative to the project root
KML_FILE="../output/zonas_contingencia.kml"
KMZ_FILE="../output/zonas_contingencia.kmz"

# Default coordinates (if not provided by user)
DEFAULT_LAT="-24.33160375868075"
DEFAULT_LON="-53.85489414802796"

LAT_LON_ARG=""

# Check for command-line arguments
if [ "$#" -eq 1 ]; then
    # Assume it's a single "lat,lon" string
    LAT_LON_ARG="$1"
    echo "Usando coordenadas fornecidas via linha de comando: $LAT_LON_ARG"
elif [ "$#" -eq 2 ]; then
    # Assume it's separate lat and lon
    LAT_LON_ARG="$1,$2"
    echo "Usando coordenadas fornecidas via linha de comando: $LAT_LON_ARG"
elif [ "$#" -gt 2 ]; then
    echo "Uso: $0 [latitude,longitude] ou $0 [latitude] [longitude]"
    echo "Exemplo: $0 -24.331062507879754,-53.85689460743224"
    echo "Exemplo: $0 -24.331062507879754 -53.85689414802796"
    echo "Ou execute sem argumentos para usar as coordenadas padrão ou inserir manualmente."
    exit 1
else
    echo "Nenhuma coordenada fornecida via linha de comando."
    read -p "Por favor, insira a Latitude (deixe em branco para usar a padrão: $DEFAULT_LAT): " USER_LAT
    read -p "Por favor, insira a Longitude (deixe em branco para usar a padrão: $DEFAULT_LON): " USER_LON

    if [ -n "$USER_LAT" ] && [ -n "$USER_LON" ]; then
        LAT_LON_ARG="$USER_LAT,$USER_LON"
        echo "Usando coordenadas inseridas: $LAT_LON_ARG"
    elif [ -n "$USER_LAT" ]; then
        LAT_LON_ARG="$USER_LAT,$DEFAULT_LON"
        echo "Usando Latitude inserida: $USER_LAT, Longitude padrão: $DEFAULT_LON"
    elif [ -n "$USER_LON" ]; then
        LAT_LON_ARG="$DEFAULT_LAT,$USER_LON"
        echo "Usando Latitude padrão: $DEFAULT_LAT, Longitude inserida: $USER_LON"
    else
        LAT_LON_ARG="$DEFAULT_LAT,$DEFAULT_LON"
        echo "Usando coordenadas padrão: $LAT_LON_ARG"
    fi
fi

echo "\n--- Iniciando Geração do KML e KMZ ---"

# Ensure the output directory exists
mkdir -p "$(dirname "$KML_FILE")"

echo "Gerando arquivo KML com src/gerar_kml.py..."
python3 "$(dirname "$0")/../src/gerar_kml.py" "$LAT_LON_ARG"

# Check if KML generation was successful
if [ $? -ne 0 ]; then
    echo "Erro: Falha ao gerar o arquivo KML. Verifique a saída do script Python acima."
    exit 1
fi

echo "KML gerado com sucesso em: $(realpath "$KML_FILE")"

# --- Gerando Pontos das Granjas (KMZ) ---
echo "\n--- Gerando Pontos das Granjas (KMZ) ---"
python3 "$(dirname "$0")/../src/gerar_granja_kmz.py"
if [ $? -ne 0 ]; then
    echo "Erro: Falha ao gerar o KMZ dos pontos das granjas. Verifique a saída do script Python acima."
    exit 1
fi

# Remove old kmz file if it exists
if [ -f "$KMZ_FILE" ]; then
    echo "Removendo arquivo KMZ existente: $(realpath "$KMZ_FILE")"
    rm "$KMZ_FILE"
fi

echo "Empacotando '$KML_FILE' em '$KMZ_FILE'..."
zip -j "$KMZ_FILE" "$KML_FILE"

if [ $? -eq 0 ]; then
    echo "\n--- Processo Concluído com Sucesso ---"
    echo "Arquivo KMZ criado com sucesso em: $(realpath "$KMZ_FILE")"
else
    echo "Erro ao criar o arquivo KMZ."
    exit 1
fi
