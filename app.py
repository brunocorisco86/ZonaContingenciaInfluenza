import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import math
import os

# =============================================================================
# Funções de Carregamento de Dados
# =============================================================================

@st.cache_data
def load_farm_data():
    """Carrega e limpa os dados das granjas a partir do arquivo CSV."""
    print("[INFO] Carregando dados das granjas de data/coordenadas.csv...")
    file_path = os.path.join("data", "coordenadas.csv")
    try:
        df = pd.read_csv(file_path, sep=';')
        # Limpeza básica dos dados de coordenadas
        df.dropna(subset=['coordenadas'], inplace=True)
        df = df[df['coordenadas'].str.contains(',', na=False)]
        return df
    except FileNotFoundError:
        st.error(f"Arquivo de dados não encontrado em: {file_path}")
        return pd.DataFrame()

@st.cache_data
def load_contingency_plan():
    """Carrega o conteúdo do plano de contingência."""
    print("[INFO] Carregando plano de contingência de docs/plano de contingencia.md...")
    file_path = os.path.join("docs", "plano de contingencia.md")
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return "Arquivo 'plano de contingencia.md' não encontrado."

# =============================================================================
# Funções de Geração de Mapa
# =============================================================================

def create_circle(map_obj, lat, lon, radius, color, text):
    """Desenha um círculo de contingência no mapa."""
    folium.Circle(
        location=[lat, lon],
        radius=radius,
        color=color,
        fill=True,
        fill_color=color,
        fill_opacity=0.2,
        popup=text
    ).add_to(map_obj)

def create_circle(map_obj, lat, lon, radius, color, text):
    """Desenha um círculo de contingência no mapa."""
    folium.Circle(
        location=[lat, lon],
        radius=radius,
        color=color,
        fill=True,
        fill_color=color,
        fill_opacity=0.2,
        popup=text
    ).add_to(map_obj)

@st.cache_data
def generate_full_map(lat, lon, df):
    """Gera o mapa completo com zonas e granjas, e armazena o resultado em cache."""
    print(f"[INFO] Gerando novo mapa para as coordenadas: Latitude={lat}, Longitude={lon}")
    m = folium.Map(location=[lat, lon], zoom_start=10)

    # Adicionar marcador para o foco
    folium.Marker(
        [lat, lon],
        popup="FOCO",
        icon=folium.Icon(color='red', icon='info-sign')
    ).add_to(m)

    # Definir e desenhar as zonas de contingência
    zones = [
        {"name": "Perifoco (3km)", "radius": 3000, "color": "red"},
        {"name": "Vigilância (7km)", "radius": 7000, "color": "purple"},
        {"name": "Proteção (15km)", "radius": 15000, "color": "blue"}
    ]

    for zone in zones:
        create_circle(m, lat, lon, zone["radius"], zone["color"], zone["name"])

    # Adicionar marcadores para as granjas
    if not df.empty:
        for _, row in df.iterrows():
            try:
                coords = row['coordenadas'].split(',')
                lat_granja = float(coords[0].strip())
                lon_granja = float(coords[1].strip())
                
                popup_html = f"""
                <b>Proprietário:</b> {row.get('proprietario', 'N/A')}<br>
                <b>Cidade:</b> {row.get('cidade', 'N/A')}<br>
                <b>Capacidade:</b> {row.get('capacidade', 'N/A')} aves<br>
                """
                
                folium.CircleMarker(
                    location=[lat_granja, lon_granja],
                    radius=2,
                    color='darkgreen',
                    fill=True,
                    fill_color='darkgreen',
                    fill_opacity=0.7,
                    popup=folium.Popup(popup_html, max_width=300)
                ).add_to(m)
            except (ValueError, IndexError):
                continue
    return m._repr_html_()

# =============================================================================
# Configuração da Página e UI
# =============================================================================

st.set_page_config(layout="wide", page_title="Zonas de Contingência de Influenza Aviária")

st.title("Visualizador de Zonas de Contingência de Influenza Aviária")

# Carregar dados
df_farms = load_farm_data()
contingency_plan_text = load_contingency_plan()

# --- Barra Lateral ---
st.sidebar.header("Configurações do Foco")

lat_foco = st.sidebar.number_input(
    'Latitude do Foco',
    value=-24.33135069928127,
    format="%.15f"
)

lon_foco = st.sidebar.number_input(
    'Longitude do Foco',
    value=-53.85542105733513,
    format="%.15f"
)

st.sidebar.info("O mapa é atualizado automaticamente ao alterar as coordenadas.")

with st.sidebar.expander("Ver Plano de Contingência"):
    st.markdown(contingency_plan_text, unsafe_allow_html=True)


# --- Painel Principal ---
tab1, tab2 = st.tabs(["🗺️ Mapa de Contingência", "📄 Plano de Contingência"])

# Gerar ou obter o mapa do cache
map_to_display = generate_full_map(lat_foco, lon_foco, df_farms)

with tab1:
    st.header("Mapa Interativo")
    map_html = generate_full_map(lat_foco, lon_foco, df_farms)
    st.components.v1.html(map_html, height=750)

with tab2:
    st.header("Plano de Contingência para Influenza Aviária")
    st.markdown(contingency_plan_text, unsafe_allow_html=True)

# =============================================================================
# Funções de Exportação para KML
# =============================================================================

def generate_zones_kml_content(lat, lon):
    """Gera o conteúdo KML para as zonas de contingência."""
    # Lógica adaptada de gerar_kml.py
    zones = [
        {"name": "PROTEÇÃO", "radius": 15000, "poly_color": "80FF0000", "line_color": "ffff0000"},
        {"name": "VIGILANCIA", "radius": 7000, "poly_color": "80C800C8", "line_color": "ffC800C8"},
        {"name": "PERIFOCO", "radius": 3000, "poly_color": "800000FF", "line_color": "ff0000FF"}
    ]
    
    styles_kml = ""
    polygons_kml = ""

    for zone in zones:
        style_id = f"style_{zone['name'].lower().replace('ç', 'c').replace('ã', 'a')}"
        styles_kml += f'''
        <Style id="{style_id}">
          <LineStyle><color>{zone["line_color"]}</color><width>2</width></LineStyle>
          <PolyStyle><color>{zone["poly_color"]}</color></PolyStyle>
        </Style> '''
        
        coords = []
        for i in range(65):
            angle = (i / 64) * 2 * math.pi
            dx = zone["radius"] * math.cos(angle)
            dy = zone["radius"] * math.sin(angle)
            point_lat = lat + (dy / 111111)
            point_lon = lon + (dx / (111111 * math.cos(math.radians(lat))))
            coords.append(f"{point_lon},{point_lat},0")
        polygon_coords = " ".join(coords)

        polygons_kml += f'''
        <Placemark>
          <name>{zone["name"]}</name>
          <styleUrl>#{style_id}</styleUrl>
          <Polygon>
            <outerBoundaryIs><LinearRing><coordinates>{polygon_coords}</coordinates></LinearRing></outerBoundaryIs>
          </Polygon>
        </Placemark>'''

    foco_placemark = f'''
    <Placemark>
      <name>FOCO</name>
      <styleUrl>#style_foco</styleUrl>
      <Point><coordinates>{lon},{lat},0</coordinates></Point>
    </Placemark>'''
    
    foco_style = '''
    <Style id="style_foco">
        <IconStyle>
            <Icon><href>http://maps.google.com/mapfiles/kml/shapes/caution.png</href></Icon>
            <scale>1.5</scale>
        </IconStyle>
    </Style>'''

    return styles_kml + foco_style + foco_placemark + polygons_kml

def generate_farms_kml_content(df):
    """Gera o conteúdo KML para os pontos das granjas."""
    # Lógica adaptada de gerar_granja_kmz.py
    kml_placemarks = []
    if not df.empty:
        for _, row in df.iterrows():
            try:
                coords = row['coordenadas'].split(',')
                lat, lon = float(coords[0].strip()), float(coords[1].strip())
                
                description_html = "<table border='1' style='width:100%; border-collapse: collapse;'>"
                for key, value in row.items():
                    description_html += f"<tr><td style='padding: 5px;'><b>{key.replace('_', ' ').title()}</b></td><td style='padding: 5px;'>{value}</td></tr>"
                description_html += "</table>"

                kml_placemarks.append(f'''
                <Placemark>
                  <name>{row.get("proprietario", "N/A")}</name>
                  <description><![CDATA[{description_html}]]></description>
                  <styleUrl>#chickenIcon</styleUrl>
                  <Point><coordinates>{lon},{lat},0</coordinates></Point>
                </Placemark>''')
            except (ValueError, IndexError):
                continue
    
    icon_style = '''
    <Style id="chickenIcon">
        <IconStyle>
            <scale>0.8</scale>
            <Icon><href>https://maps.google.com/mapfiles/kml/paddle/grn-circle.png</href></Icon>
        </IconStyle>
        <LabelStyle><scale>0</scale></LabelStyle>
    </Style>'''
    
    return icon_style + "\n".join(kml_placemarks)

def merge_kml_contents(zones_content, farms_content):
    """Combina múltiplos conteúdos KML em um único documento."""
    
    final_kml = f'''<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <name>Zonas de Contingência e Granjas</name>
    {zones_content}
    {farms_content}
  </Document>
</kml>'''
    return final_kml

# =============================================================================
# Lógica de Exportação na Barra Lateral
# =============================================================================

st.sidebar.header("Exportar Mapa")

if st.sidebar.button("Preparar KML para Download"):
    print("\n[INFO] Iniciando geração de KML para download...")
    # Gerar conteúdo KML em memória
    print("[INFO] Gerando conteúdo KML para as zonas...")
    zones_kml = generate_zones_kml_content(lat_foco, lon_foco)
    print("[INFO] Gerando conteúdo KML para as granjas...")
    farms_kml = generate_farms_kml_content(df_farms)
    
    # Mesclar os conteúdos
    print("[INFO] Mesclando conteúdos KML...")
    final_kml_data = merge_kml_contents(zones_kml, farms_kml)
    
    # Disponibilizar para download
    st.sidebar.download_button(
        label="📥 Baixar Arquivo KML",
        data=final_kml_data,
        file_name="zonas_contingencia_completo.kml",
        mime="application/vnd.google-earth.kml+xml"
    )
