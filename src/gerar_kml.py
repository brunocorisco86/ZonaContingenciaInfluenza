import math
import sys

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
    foco_desc = "Complexo Agroindustrial Abatedouro de Aves C.Vale"

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

    zones = [
        ("PROTEÇÃO", 15000, "80b1314b"), # C.Vale Blue
        ("VIGILANCIA", 7000, "80d1cf4d"), # C.Vale Light Blue
        ("PERIFOCO", 3000, "8000ffff")   # Yellow
    ]
    
    desc_protecao = "Zona de Proteção (15km): Restrição e controle rigoroso do trânsito de pessoas, veículos, aves e produtos avícolas."
    desc_vigilancia = "Zona de Vigilância (7km): Monitoramento epidemiológico intensivo nas propriedades e controle de trânsito."
    desc_perifoco = "Perifoco (3km): Interdição do estabelecimento, proibindo entrada e saída de aves, rações, e outros materiais."
    
    zone_descriptions = {
        "PROTEÇÃO": desc_protecao,
        "VIGILANCIA": desc_vigilancia,
        "PERIFOCO": desc_perifoco
    }

    polygons_kml = ""
    # Generate polygons from largest to smallest so they stack correctly
    for name, radius, color in sorted(zones, key=lambda x: x[1], reverse=True):
        style_id = f"style_{name.lower()}"
        description = zone_descriptions[name]
        polygons_kml += generate_kml_circle(center_lat, center_lon, radius, name, description, style_id)

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

    final_kml = kml_template.format(
        lat=center_lat,
        lon=center_lon,
        foco_description=foco_desc,
        protecao_poly_color=zones[0][2],
        protecao_line_color="ff" + zones[0][2][2:],
        vigilancia_poly_color=zones[1][2],
        vigilancia_line_color="ff" + zones[1][2][2:],
        perifoco_poly_color=zones[2][2],
        perifoco_line_color="ff" + zones[2][2][2:],
        polygons=polygons_kml
    )

    with open("../output/zonas_contingencia.kml", "w", encoding="utf-8") as f:
        f.write(final_kml)

    print("Arquivo 'zonas_contingencia.kml' gerado com sucesso.")

if __name__ == "__main__":
    main()
