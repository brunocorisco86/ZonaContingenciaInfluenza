import math
import sys
import os

def generate_kml_circle(lat, lon, radius_m, name, description, style_id):
    """Generates a KML Polygon for a circle."""
    coords = []
    # 64 segments for a smooth circle
    for i in range(65):
        angle = (i / 64) * 2 * math.pi
        dx = radius_m * math.cos(angle)
        dy = radius_m * math.sin(angle)
        
        point_lat = lat + (dy / 111111)
        point_lon = lon + (dx / (111111 * math.cos(math.radians(lat))))
        
        coords.append(f"{point_lon},{point_lat},0")
        
    polygon_coords = " ".join(coords)
    
    return f'''
    <Placemark>
      <name>{name}</name>
      <description>{description}</description>
      <styleUrl>#{style_id}</styleUrl>
      <Polygon>
        <outerBoundaryIs>
          <LinearRing>
            <coordinates>{polygon_coords}</coordinates>
          </LinearRing>
        </outerBoundaryIs>
      </Polygon>
    </Placemark>
    '''

def main():
    """Main function to generate KML file."""
    center_lat = -24.33160375868075
    center_lon = -53.85489414802796
    foco_desc = "Local de um designado como foco de influenza aviária, área isolada com medidas de contenção, vigilância intensificada e controle de movimentação."

    # Check for command-line arguments for coordinates
    if len(sys.argv) == 2:
        try:
            # sys.argv[1] is a string like "lat,lon"
            coords_str = sys.argv[1]
            lat_str, lon_str = coords_str.split(',')
            center_lat = float(lat_str.strip())
            center_lon = float(lon_str.strip())
            foco_desc = "Foco definido por coordenadas manuais"
            print(f"Usando coordenadas da linha de comando: {center_lat}, {center_lon}")
        except (ValueError, IndexError):
            print("Argumentos de coordenadas inválidos. Formato esperado: 'latitude,longitude'. Usando coordenadas padrão do arquivo.")
    else:
        print("Nenhuma coordenada fornecida ou formato inválido. Usando coordenadas padrão do abatedouro.")

    # Colors are in aabbggrr format (alpha, blue, green, red)
    # Red -> Purple -> Blue gradient for critical to less critical
    zones = [
        {
            "name": "PROTEÇÃO",
            "radius": 15000,
            "poly_color": "80FF0000",  # Transparent Blue
            "line_color": "ffff0000",  # Solid Blue
        },
        {
            "name": "VIGILANCIA",
            "radius": 7000,
            "poly_color": "80C800C8",  # Transparent Purple
            "line_color": "ffC800C8",  # Solid Purple
        },
        {
            "name": "PERIFOCO",
            "radius": 3000,
            "poly_color": "800000FF",  # Transparent Red
            "line_color": "ff0000FF",  # Solid Red
        },
    ]

    desc_protecao = "Zona de Proteção (15km): Restrição e controle rigoroso do trânsito de pessoas, veículos, aves e produtos avícolas."
    desc_vigilancia = "Zona de Vigilância (7km): Monitoramento epidemiológico intensivo nas propriedades e controle de trânsito."
    desc_perifoco = "Perifoco (3km): Interdição do estabelecimento, proibindo entrada e saída de aves, rações, e outros materiais."

    zone_descriptions = {
        "PROTEÇÃO": desc_protecao,
        "VIGILANCIA": desc_vigilancia,
        "PERIFOCO": desc_perifoco,
    }

    polygons_kml = ""
    # Generate polygons from largest to smallest so they stack correctly
    for zone in sorted(zones, key=lambda x: x["radius"], reverse=True):
        style_id = f"style_{zone['name'].lower().replace('ç', 'c').replace('ã', 'a')}"
        description = zone_descriptions[zone["name"]]
        polygons_kml += generate_kml_circle(
            center_lat, center_lon, zone["radius"], zone["name"], description, style_id
        )

    kml_template = '''<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <name>Zonas de Contingência C.Vale - Salmonella</name>
    
    <Style id="style_protecao">
      <LineStyle><color>{protecao_line_color}</color><width>2</width></LineStyle>
      <PolyStyle><color>{protecao_poly_color}</color></PolyStyle>
    </Style>
    <Style id="style_vigilancia">
      <LineStyle><color>{vigilancia_line_color}</color><width>2</width></LineStyle>
      <PolyStyle><color>{vigilancia_poly_color}</color></PolyStyle>
    </Style>
    <Style id="style_perifoco">
      <LineStyle><color>{perifoco_line_color}</color><width>2</width></LineStyle>
      <PolyStyle><color>{perifoco_poly_color}</color></PolyStyle>
    </Style>
    <Style id="style_foco">
        <IconStyle>
            <Icon><href>http://maps.google.com/mapfiles/kml/shapes/caution.png</href></Icon>
            <scale>1.5</scale>
        </IconStyle>
    </Style>

    <Placemark>
      <name>FOCO</name>
      <description>{foco_description}</description>
      <styleUrl>#style_foco</styleUrl>
      <Point><coordinates>{lon},{lat},0</coordinates></Point>
    </Placemark>

    {polygons}
    
  </Document>
</kml>
'''

    style_colors = {}
    for zone in zones:
        key_name = zone['name'].lower().replace('ç', 'c').replace('ã', 'a')
        style_colors[f"{key_name}_poly_color"] = zone["poly_color"]
        style_colors[f"{key_name}_line_color"] = zone["line_color"]

    final_kml = kml_template.format(
        lat=center_lat,
        lon=center_lon,
        foco_description=foco_desc,
        polygons=polygons_kml,
        **style_colors,
    )

    script_dir = os.path.dirname(__file__)
    project_root = os.path.abspath(os.path.join(script_dir, '..'))
    output_kml_path = os.path.join(project_root, "output", "zonas_contingencia.kml")
    os.makedirs(os.path.dirname(output_kml_path), exist_ok=True)

    with open(output_kml_path, "w", encoding="utf-8") as f:
        f.write(final_kml)

    print("Arquivo 'zonas_contingencia.kml' gerado com sucesso.")

if __name__ == "__main__":
    main()