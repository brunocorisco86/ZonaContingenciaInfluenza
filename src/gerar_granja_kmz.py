import csv
import zipfile
import os
import base64

def generate_kml_point(lat, lon, icon_href, icon_scale, name, description_html):
    """Generates a KML Placemark for a point with a custom icon, name, and detailed description, without a label."""
    return f'''
    <Placemark>
      <name>{name}</name>
      <description><![CDATA[{description_html}]]></description>
      <Style>
        <IconStyle>
          <scale>{icon_scale}</scale>
          <Icon>
            <href>{icon_href}</href>
          </Icon>
        </IconStyle>
        <LabelStyle>
          <scale>0</scale> <!-- Hide label -->
        </LabelStyle>
      </Style>
      <Point>
        <coordinates>{lon},{lat},0</coordinates>
      </Point>
    </Placemark>
    '''

def main():
    script_dir = os.path.dirname(__file__)
    project_root = os.path.abspath(os.path.join(script_dir, '..'))

    csv_file_path = os.path.join(project_root, "data", "coordenadas.csv")
    icon_image_path = os.path.join(project_root, "assets", "icone_frango.png")
    output_kml_path = os.path.join(project_root, "output", "granjas.kml")
    output_kmz_path = os.path.join(project_root, "output", "granjas.kmz")

    # Base64 encode the icon image
    try:
        with open(icon_image_path, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode('utf-8')
        icon_data_uri = f"data:image/png;base64,{encoded_image}"
    except FileNotFoundError:
        print(f"Erro: Imagem do ícone não encontrada em {icon_image_path}")
        return

    kml_placemarks = []
    processed_nucleos = set()

    try:
        with open(csv_file_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=';')
            for row in reader:
                nucleo = row.get('nucleo')
                if nucleo and nucleo not in processed_nucleos:
                    processed_nucleos.add(nucleo)
                    coords_str = row.get('coordenadas')
                    if coords_str:
                        try:
                            lat_str, lon_str = coords_str.split(',')
                            lat = float(lat_str.strip())
                            lon = float(lon_str.strip())

                            proprietario = row.get('proprietario', 'Desconhecido')

                            # Create HTML description from all row data
                            description_html_parts = []
                            description_html_parts.append("<table border=\"1\" style=\"width:100%; border-collapse: collapse;\">")
                            for key, value in row.items():
                                description_html_parts.append(f"<tr><td style=\"padding: 5px;\"><b>{key.replace('_', ' ').title()}</b></td><td style=\"padding: 5px;\">{value}</td></tr>")
                            description_html_parts.append("</table>")
                            description_html = "".join(description_html_parts)

                            kml_placemarks.append(generate_kml_point(lat, lon, icon_data_uri, 0.8, proprietario, description_html))
                        except ValueError:
                            print(f"Aviso: Coordenadas inválidas para o núcleo {nucleo}: {coords_str}")
    except FileNotFoundError:
        print(f"Erro: Arquivo CSV não encontrado em {csv_file_path}")
        return

    kml_content = '''<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <name>Pontos das Granjas</name>
    {} 
  </Document>
</kml>
'''.format("\n".join(kml_placemarks))

    # Save KML file
    os.makedirs(os.path.dirname(output_kml_path), exist_ok=True)
    with open(output_kml_path, 'w', encoding='utf-8') as f:
        f.write(kml_content)
    print(f"Arquivo KML gerado com sucesso em: {os.path.abspath(output_kml_path)}")

    # Create KMZ file
    with zipfile.ZipFile(output_kmz_path, 'w') as kmz_file:
        kmz_file.write(output_kml_path, os.path.basename(output_kml_path))
        # Add the icon image to the KMZ archive under a 'files/' directory
        kmz_file.write(icon_image_path, os.path.join('files', os.path.basename(icon_image_path)))
    print(f"Arquivo KMZ gerado com sucesso em: {os.path.abspath(output_kmz_path)}")

if __name__ == "__main__":
    main()