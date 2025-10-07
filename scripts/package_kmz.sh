#!/bin/bash
# Script to generate KML files and package them into a single KMZ archive.

PROJECT_ROOT=$(cd "$(dirname "$0")/.." && pwd)
OUTPUT_DIR="$PROJECT_ROOT/output"
ASSETS_DIR="$PROJECT_ROOT/assets"
SRC_DIR="$PROJECT_ROOT/src"

ZONAS_KML_FILE="$OUTPUT_DIR/zonas_contingencia.kml"
GRANJAS_KML_FILE="$OUTPUT_DIR/granjas.kml"
FINAL_KMZ_FILE="$OUTPUT_DIR/zonas_contingencia_completo.kmz"
ICON_FILE="$ASSETS_DIR/icone_frango.png"

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
    echo "Exemplo: $0 -24.331062507879754 -53.85489414802796"
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

echo "\n--- Iniciando Geração dos Arquivos KML ---"

# Ensure the output directory exists
mkdir -p "$OUTPUT_DIR"

# --- Gerando KML das Zonas de Contingência ---
echo "Gerando KML das zonas com src/gerar_kml.py..."
python3 "$SRC_DIR/gerar_kml.py" "$LAT_LON_ARG"
if [ $? -ne 0 ]; then
    echo "Erro: Falha ao gerar o KML das zonas. Verifique a saída do script Python."
    exit 1
fi

# --- Gerando KML dos Pontos das Granjas ---
echo "\nGerando KML das granjas com src/gerar_granja_kmz.py..."
python3 "$SRC_DIR/gerar_granja_kmz.py"
if [ $? -ne 0 ]; then
    echo "Erro: Falha ao gerar o KML das granjas. Verifique a saída do script Python."
    exit 1
fi

# --- Empacotando tudo em um único KMZ ---
echo "\n--- Empacotando Arquivos em um KMZ ---"

if [ -f "$FINAL_KMZ_FILE" ]; then
    echo "Removendo arquivo KMZ anterior: $FINAL_KMZ_FILE"
    rm "$FINAL_KMZ_FILE"
fi

# Create a temporary directory for staging files for the KMZ
TMP_DIR=$(mktemp -d)
mkdir -p "$TMP_DIR/files"

# Copy the KML files and the icon to the staging directory
cp "$ZONAS_KML_FILE" "$TMP_DIR/"
cp "$GRANJAS_KML_FILE" "$TMP_DIR/"
cp "$ICON_FILE" "$TMP_DIR/files/"

echo "Criando arquivo KMZ: $FINAL_KMZ_FILE"
( cd "$TMP_DIR" && zip -r "$FINAL_KMZ_FILE" . )

# Cleanup the temporary directory
rm -rf "$TMP_DIR"

if [ $? -eq 0 ]; then
    echo "\n--- Processo Concluído com Sucesso ---"
    echo "Arquivo KMZ final criado em: $FINAL_KMZ_FILE"
else
    echo "Erro ao criar o arquivo KMZ."
    exit 1
fi