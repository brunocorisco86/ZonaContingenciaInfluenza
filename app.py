import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import math
import os

from math import radians, cos, sin, asin, sqrt

# =============================================================================
# Funções de Carregamento de Dados
# =============================================================================

@st.cache_data
def haversine_distance(lon1, lat1, lon2, lat2):
    """
    Calcula a distância em metros entre dois pontos na Terra.
    """
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    r = 6371000 # Raio da Terra em metros
    return c * r

@st.cache_data
def classify_farms_by_zone(lat_foco, lon_foco, df):
    """Classifica as granjas nas zonas de contingência e agrega os dados por núcleo."""
    print("[INFO] Classificando produtores e agregando por núcleo...")
    
    # Dicionário para armazenar dados brutos por zona
    raw_zone_data = {
        "Perifoco (0-3km)": [],
        "Vigilância (3-10km)": [],
        "Proteção (10-25km)": []
    }

    # 1. Classifica cada aviário em sua zona mais restrita
    for _, row in df.iterrows():
        try:
            coords = row['coordenadas'].split(',')
            lat_granja = float(coords[0].strip())
            lon_granja = float(coords[1].strip())
            
            distance = haversine_distance(lon_foco, lat_foco, lon_granja, lat_granja)
            
            farm_data = row.to_dict()

            if distance <= 3000:
                raw_zone_data["Perifoco (0-3km)"].append(farm_data)
            elif distance <= 10000:
                raw_zone_data["Vigilância (3-10km)"].append(farm_data)
            elif distance <= 25000:
                raw_zone_data["Proteção (10-25km)"].append(farm_data)
        except (ValueError, IndexError, AttributeError):
            continue

    # 2. Agrega os dados por 'núcleo' dentro de cada zona
    aggregated_results = {
        "Perifoco (0-3km)": {},
        "Vigilância (3-10km)": {},
        "Proteção (10-25km)": {}
    }

    for zone_name, farms in raw_zone_data.items():
        for farm in farms:
            nucleo_id = farm.get('nucleo')
            if pd.isna(nucleo_id):
                continue
            
            nucleo_id = int(nucleo_id)
            
            if nucleo_id not in aggregated_results[zone_name]:
                try:
                    coords = farm['coordenadas'].split(',')
                    lat_granja_for_nucleo = float(coords[0].strip())
                    lon_granja_for_nucleo = float(coords[1].strip())
                except (ValueError, IndexError, AttributeError):
                    continue

                aggregated_results[zone_name][nucleo_id] = {
                    'aviarios': [],
                    'tecnico': farm.get('tecnico', 'N/A'),
                    'proprietario': farm.get('proprietario', 'N/A'),
                    'bp_propriedade': set(),
                    'total_aves': 0,
                    'total_area': 0,
                    'latitude': lat_granja_for_nucleo,
                    'longitude': lon_granja_for_nucleo
                }
            
            agg_nucleo = aggregated_results[zone_name][nucleo_id]
            agg_nucleo['aviarios'].append(farm.get('fazenda'))
            agg_nucleo['bp_propriedade'].add(farm.get('bp_propriedade'))
            agg_nucleo['total_aves'] += pd.to_numeric(farm.get('capacidade'), errors='coerce') or 0
            agg_nucleo['total_area'] += pd.to_numeric(farm.get('area'), errors='coerce') or 0

    return aggregated_results


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

@st.cache_data
def generate_full_map(lat, lon, df):
    """Gera o mapa completo com zonas de contingência em formato de anel e granjas."""
    print(f"[INFO] Gerando novo mapa para as coordenadas: Latitude={lat}, Longitude={lon}")
    m = folium.Map(location=[lat, lon], zoom_start=9)

    # Adicionar marcador para o foco
    folium.Marker(
        [lat, lon],
        popup="<b>FOCO</b><br>Ponto central do foco de influenza aviária.",
        icon=folium.Icon(color='red', icon='info-sign')
    ).add_to(m)

    # Helper para gerar coordenadas de um círculo
    def get_circle_coords(center_lat, center_lon, radius_m):
        coords = []
        for i in range(101):
            angle = (i / 100) * 2 * math.pi
            dx = radius_m * math.cos(angle)
            dy = radius_m * math.sin(angle)
            point_lat = center_lat + (dy / 111111)
            point_lon = center_lon + (dx / (111111 * math.cos(math.radians(center_lat))))
            coords.append([point_lat, point_lon])
        return coords

    # Definir zonas com raios e descrições
    zones = [
        {
            "name": "Proteção (10-25km)", "outer_radius": 25000, "inner_radius": 10000, "color": "blue",
            "description": "Zona de controle e monitoramento. Fiscalização do trânsito de veículos e produtos avícolas. Barreiras sanitárias para prevenir a entrada do vírus."
        },
        {
            "name": "Vigilância (3-10km)", "outer_radius": 10000, "inner_radius": 3000, "color": "purple",
            "description": "Zona de vigilância ativa. Restrição no trânsito de aves e produtos. Suspensão de GTAs e monitoramento epidemiológico intensivo."
        },
        {
            "name": "Perifoco (0-3km)", "outer_radius": 3000, "inner_radius": 0, "color": "red",
            "description": "Área de interdição máxima. Sacrifício de aves e controle total de acesso. Medidas rigorosas de desinfecção e vazio sanitário obrigatório."
        }
    ]

    for zone in zones:
        locations = [get_circle_coords(lat, lon, zone["outer_radius"])]
        if zone["inner_radius"] > 0:
            inner_coords = get_circle_coords(lat, lon, zone["inner_radius"])
            inner_coords.reverse()
            locations.append(inner_coords)

        folium.Polygon(
            locations=locations,
            color=zone["color"],
            fill=True,
            fill_color=zone["color"],
            fill_opacity=0.2,
            popup=f"<b>{zone['name']}</b><br>{zone['description']}"
        ).add_to(m)

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




# --- Painel Principal ---
tab1, tab2, tab3 = st.tabs(["🗺️ Mapa de Contingência", "📄 Plano de Contingência", "📋 Listas de Produtores"])

# Gerar ou obter o mapa do cache
map_to_display = generate_full_map(lat_foco, lon_foco, df_farms)

with tab1:
    st.header("Mapa Interativo")
    map_html = generate_full_map(lat_foco, lon_foco, df_farms)
    st.components.v1.html(map_html, height=750)

with tab2:
    st.header("Plano de Contingência para Influenza Aviária")
    st.markdown(contingency_plan_text, unsafe_allow_html=True)

with tab3:
    st.header("Lista de Produtores por Zona de Contingência")
    classified_nucleos = classify_farms_by_zone(lat_foco, lon_foco, df_farms)
    
    st.info("As listas mostram os núcleos de produção agrupados pela zona de contingência mais restrita em que se encontram.")

    # A ordem de exibição é da maior para a menor zona
    zone_order = ["Proteção (10-25km)", "Vigilância (3-10km)", "Perifoco (0-3km)"]

    for zone_name in zone_order:
        nucleos = classified_nucleos[zone_name]
        sorted_nucleos = sorted(nucleos.items())

        with st.expander(f"**{zone_name}** - {len(sorted_nucleos)} núcleos"):
            if not sorted_nucleos:
                st.write("Nenhum núcleo encontrado nesta zona.")
                continue
            
            for nucleo_id, data in sorted_nucleos:
                st.subheader(f"Núcleo: {nucleo_id} - {data['proprietario']}")
                col1, col2, col3 = st.columns(3)
                col1.metric("Total de Aves", f"{int(data['total_aves']):,}".replace(",", "."))
                col2.metric("Área Total (m²)", f"{int(data['total_area']):,}".replace(",", "."))
                col3.metric("Nº de Aviários", len(data['aviarios']))
                
                st.markdown(f"**Técnico:** {data['tecnico']}")
                st.markdown(f"**Aviários no núcleo:** {str(sorted(data['aviarios']))[1:-1]}")
                st.markdown(f"**BP da Propriedade:** {str([str(bp) for bp in data['bp_propriedade']])[1:-1]}")
                st.divider()

# =============================================================================
# Funções de Exportação para KML
# =============================================================================

def generate_zones_kml_parts(lat, lon):
    """Gera as partes KML (estilos e polígonos) para as zonas de contingência."""
    zones = [
        {
            "name": "PROTEÇÃO", 
            "radius": 25000, 
            "poly_color": "80FF0000", 
            "line_color": "ffff0000",
            "description": "Zona de controle e monitoramento. Fiscalização do trânsito de veículos e produtos avícolas. Barreiras sanitárias para prevenir a entrada do vírus."
        },
        {
            "name": "VIGILANCIA", 
            "radius": 10000, 
            "poly_color": "80C800C8", 
            "line_color": "ffC800C8",
            "description": "Zona de vigilância ativa. Restrição no trânsito de aves e produtos. Suspensão de GTAs e monitoramento epidemiológico intensivo em todas as propriedades."
        },
        {
            "name": "PERIFOCO", 
            "radius": 3000, 
            "poly_color": "800000FF", 
            "line_color": "ff0000FF",
            "description": "Área de interdição máxima. Sacrifício de aves e controle total de acesso. Medidas rigorosas de desinfecção e vazio sanitário obrigatório."
        }
    ]
    
    styles_kml = ""
    polygons_kml = ""

    for zone in zones:
        style_id = f"style_{zone['name'].lower().replace('ç', 'c').replace('ã', 'a')}"
        styles_kml += f'''
        <Style id="{style_id}">
          <LineStyle><color>{zone["line_color"]}</color><width>2</width></LineStyle>
          <PolyStyle><color>{zone["poly_color"]}</color></PolyStyle>
        </Style>'''
        
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
          <description><![CDATA[{zone["description"]}]]></description>
          <styleUrl>#{style_id}</styleUrl>
          <Polygon>
            <outerBoundaryIs><LinearRing><coordinates>{polygon_coords}</coordinates></LinearRing></outerBoundaryIs>
          </Polygon>
        </Placemark>'''
    return styles_kml, polygons_kml

def generate_foco_kml_parts(lat, lon):
    """Gera as partes KML (estilo e placemark) para o ponto de foco."""
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
    return foco_style, foco_placemark

def generate_farms_kml_parts(df):
    """Gera as partes KML (estilo e placemarks) para os pontos das granjas."""
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
    
    return icon_style, "\n".join(kml_placemarks)

def merge_kml_contents(zone_styles, zone_polygons, foco_style, foco_placemark, farm_style, farm_placemarks):
    """Combina múltiplos conteúdos KML em um único documento com pastas."""
    
    final_kml = f'''<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <name>Zonas de Contingência e Granjas</name>
    
    <!-- Estilos -->
    {zone_styles}
    {foco_style}
    {farm_style}

    <!-- Pastas com os dados -->
    <Folder>
        <name>Zonas de Contenção</name>
        {zone_polygons}
    </Folder>
    <Folder>
        <name>Foco</name>
        {foco_placemark}
    </Folder>
    <Folder>
        <name>Produtores</name>
        {farm_placemarks}
    </Folder>
  </Document>
</kml>'''
    return final_kml

from fpdf import FPDF
import datetime

# =============================================================================
# Funções de Relatório
# =============================================================================

def generate_report_html(classified_data, lat, lon):
    """Gera uma string HTML formatada para impressão."""
    now = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    
    html = f"""
    <html>
    <head>
        <style>
            body {{ font-family: sans-serif; }}
            h1, h2, h3 {{ color: #333; }}
            table {{ width: 100%; border-collapse: collapse; margin-bottom: 20px; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #f2f2f2; }}
            .header {{ margin-bottom: 30px; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>Relatório de Zonas de Contingência</h1>
            <p>Gerado em: {now}</p>
            <p>Coordenadas do Foco: Latitude={lat}, Longitude={lon}</p>
        </div>
    """

    zone_order = ["Perifoco (0-3km)", "Vigilância (3-10km)", "Proteção (10-25km)"]
    for zone_name in zone_order:
        nucleos = classified_data[zone_name]
        sorted_nucleos = sorted(nucleos.items())
        
        html += f"<h2>{zone_name} ({len(sorted_nucleos)} núcleos)</h2>"
        
        if not sorted_nucleos:
            html += "<p>Nenhum núcleo encontrado nesta zona.</p>"
            continue

        html += "<table><tr><th>Núcleo</th><th>Proprietário</th><th>Técnico</th><th>Aviários</th><th>Total Aves</th><th>Área Total (m²)</th><th>BP Propriedade</th></tr>"
        for nucleo_id, data in sorted_nucleos:
            html += f"""<tr>
                <td>{nucleo_id}</td>
                <td>{data['proprietario']}</td>
                <td>{data['tecnico']}</td>
                <td>{str(sorted(data['aviarios']))[1:-1]}</td>
                <td>{int(data['total_aves'])}</td>
                <td>{int(data['total_area'])}</td>
                <td>{str([str(bp) for bp in data['bp_propriedade']])[1:-1]}</td>
            </tr>"""
        html += "</table>"

    html += """</body></html>"""
    return html

def generate_pdf_report(classified_data, lat, lon):
    """Gera um relatório em PDF a partir dos dados classificados."""
    print("[INFO] Gerando relatório PDF...")
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    
    pdf.cell(0, 10, "Relatório de Zonas de Contingência", 0, 1, "C")
    pdf.ln(10)
    
    now = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    pdf.set_font("Arial", "", 12)
    pdf.cell(0, 8, f"Gerado em: {now}", 0, 1)
    pdf.cell(0, 8, f"Coordenadas do Foco: Latitude={lat}, Longitude={lon}", 0, 1)
    pdf.ln(10)

    zone_order = ["Perifoco (0-3km)", "Vigilância (3-10km)", "Proteção (10-25km)"]
    for zone_name in zone_order:
        nucleos = classified_data[zone_name]
        sorted_nucleos = sorted(nucleos.items())
        
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, f"{zone_name} ({len(sorted_nucleos)} núcleos)", 0, 1)
        
        if not sorted_nucleos:
            pdf.set_font("Arial", "I", 10)
            pdf.cell(0, 10, " Nenhum núcleo encontrado nesta zona.", 0, 1)
            pdf.ln(5)
            continue

        for nucleo_id, data in sorted_nucleos:
            pdf.ln(5)
            pdf.set_font("Arial", "B", 11)
            pdf.cell(0, 7, f"Núcleo: {nucleo_id} - {data['proprietario']}", 0, 1)
            pdf.set_font("Arial", "", 10)
            pdf.multi_cell(0, 6, f"  Técnico: {data['tecnico']}", ln=1)
            pdf.multi_cell(0, 6, f"  Total de Aves: {int(data['total_aves']):,}".replace(",", "."), ln=1)
            pdf.multi_cell(0, 6, f"  Área Total (m²): {int(data['total_area']):,}".replace(",", "."), ln=1)
            pdf.multi_cell(0, 6, f"  Nº de Aviários: {len(data['aviarios'])}", ln=1)
            pdf.multi_cell(0, 6, f"  Aviários no núcleo: {str(sorted(data['aviarios']))[1:-1]}", ln=1)
            pdf.multi_cell(0, 6, f"  BP da Propriedade: {str([str(bp) for bp in data['bp_propriedade']])[1:-1]}", ln=1)

            # Adicionar coordenadas e link do Google Maps
            lat, lon = data['latitude'], data['longitude']
            maps_link = f"https://www.google.com/maps/search/?api=1&query={lat},{lon}"
            pdf.multi_cell(0, 6, f"  Coordenadas: {lat}, {lon}", ln=1)
            pdf.set_text_color(0, 0, 255)
            pdf.set_font("Arial", "U", 10)
            pdf.multi_cell(0, 6, f"  Abrir no Google Maps", ln=1, link=maps_link)
            pdf.set_font("Arial", "", 10)
            pdf.set_text_color(0, 0, 0)
        pdf.ln(10)
        
    return bytes(pdf.output())


# =============================================================================
# Lógica de Exportação na Barra Lateral
# =============================================================================

st.sidebar.header("Relatório e Exportação")

# Botão para baixar o mapa HTML
map_html_for_download = generate_full_map(lat_foco, lon_foco, df_farms)
st.sidebar.download_button(
    label="📥 Baixar Mapa (HTML)",
    data=map_html_for_download,
    file_name="mapa_contingencia.html",
    mime="text/html"
)

# Botão para gerar o relatório de impressão
if st.sidebar.button("Gerar Relatório para Impressão"):
    classified_data = classify_farms_by_zone(lat_foco, lon_foco, df_farms)
    report_html = generate_report_html(classified_data, lat_foco, lon_foco)
    st.session_state.report_html = report_html

# Botão para baixar o relatório em PDF
classified_data_for_pdf = classify_farms_by_zone(lat_foco, lon_foco, df_farms)
_pdf_data = generate_pdf_report(classified_data_for_pdf, lat_foco, lon_foco)
st.sidebar.download_button(
    label="📄 Baixar Relatório (PDF)",
    data=_pdf_data,
    file_name="relatorio_contingencia.pdf",
    mime="application/pdf"
)

# Lógica para o botão de download KML
if st.sidebar.button("Preparar KML para Download"):
    print("\n[INFO] Iniciando geração de KML para download...")
    
    # Gerar partes KML separadamente
    zone_styles, zone_polygons = generate_zones_kml_parts(lat_foco, lon_foco)
    foco_style, foco_placemark = generate_foco_kml_parts(lat_foco, lon_foco)
    farm_style, farm_placemarks = generate_farms_kml_parts(df_farms)
    
    # Combinar em um único KML com pastas
    final_kml_data = merge_kml_contents(
        zone_styles, zone_polygons, 
        foco_style, foco_placemark, 
        farm_style, farm_placemarks
    )
    
    st.session_state.kml_data = final_kml_data
    print("[INFO] Dados KML prontos para download.")

if 'kml_data' in st.session_state and st.session_state.kml_data:
    st.sidebar.download_button(
        label="📥 Baixar Arquivo KML",
        data=st.session_state.kml_data,
        file_name="zonas_contingencia_completo.kml",
        mime="application/vnd.google-earth.kml+xml"
    )

if 'report_html' in st.session_state and st.session_state.report_html:
    with st.expander("Visualizar Relatório para Impressão", expanded=True):
        st.info("Use a função 'Imprimir' do seu navegador (Ctrl+P) e 'Salvar como PDF' para gerar o documento.")
        st.components.v1.html(st.session_state.report_html, height=800, scrolling=True)
