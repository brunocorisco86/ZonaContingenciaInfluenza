import csv
import os

def generate_kml_point(lat, lon, name, description_html):
    """Generates a KML Placemark for a point that uses a shared style."""
    return f'''
    <Placemark>
      <name>{name}</name>
      <description><![CDATA[{description_html}]]></description>
      <styleUrl>#chickenIcon</styleUrl>
      <Point>
        <coordinates>{lon},{lat},0</coordinates>
      </Point>
    </Placemark>
    '''

def main():
    script_dir = os.path.dirname(__file__)
    project_root = os.path.abspath(os.path.join(script_dir, '..'))

    csv_file_path = os.path.join(project_root, "data", "coordenadas.csv")
    output_kml_path = os.path.join(project_root, "output", "granjas.kml")

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

                            kml_placemarks.append(generate_kml_point(lat, lon, proprietario, description_html))
                        except ValueError:
                            print(f"Aviso: Coordenadas inválidas para o núcleo {nucleo}: {coords_str}")
    except FileNotFoundError:
        print(f"Erro: Arquivo CSV não encontrado em {csv_file_path}")
        return

    # Define the shared style for the icon
    shared_style = '''
    <Style id="chickenIcon">
      <IconStyle>
        <scale>0.8</scale>
        <Icon>
          <href>files/icone_frango.png</href>
        </Icon>
      </IconStyle>
      <LabelStyle>
        <scale>0</scale> <!-- Hide label -->
      </LabelStyle>
    </Style>
    '''

    kml_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<kml xmlns="http://www.opengis.net/kml/2.2">
  <Document>
    <name>Pontos das Granjas</name>
    {shared_style}
    {"\n".join(kml_placemarks)} 
  </Document>
</kml>
'''

    # Save KML file
    os.makedirs(os.path.dirname(output_kml_path), exist_ok=True)
    with open(output_kml_path, 'w', encoding='utf-8') as f:
        f.write(kml_content)
    print(f"Arquivo KML das granjas gerado com sucesso em: {os.path.abspath(output_kml_path)}")

if __name__ == "__main__":
    main()
