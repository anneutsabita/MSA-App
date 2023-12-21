import dash_bio as dashbio
from dash import Dash, html, Input, Output, callback, callback_context
import requests
from Bio import SeqIO
from io import StringIO
import re

app = Dash(__name__)

# URL repositori GitHub
github_url = 'https://github.com/anneutsabita/Dataset-MSA/raw/main/genes/'

# List file FNA
file_list = ['gene_Arabidopsis-thaliana.fna', 
             'gene_Aspergillus-niger.fna', 
             'gene_Dictyostelium-discoideum-AX4.fna', 
             'gene_Glycine-max.fna', 
             'gene_Penicillium-chrysogenum-Wisconsin-54-1255.fna', 
             'gene_Solanum-lycopersicum.fna', 
             'gene_Vitis-vinifera.fna']

# String untuk menyimpan data sekuens dari semua file FNA
alignment_data = ""

# Loop melalui setiap file FNA dan baca data sekuensnya
for file_name in file_list:
    fna_url = github_url + file_name
    response = requests.get(fna_url) # Mengunduh file FNA dari GitHub dan menyimpannya secara lokal

    if response.status_code == 200:  # Check if the request was successful
        data = response.text
        fna_content = StringIO(data)
        # Print alignment_data setelah semua file FNA terbaca
        # print("data:", data)

        try:
            # Menggunakan ekspresi reguler untuk mencari semua kecocokan teks antara 'organism=' dan ']'
            match = re.search(r'\[([^\]]+=[^\]]+)\]', data)
            # print("match groups:", match.group(1))

            # Memeriksa apakah ada kecocokan
            if match:
                # Menggunakan generator expression untuk membaca semua informasi dari objek generator
                sequences_info = (f">{sequence.id}\n{sequence.seq}\n" for sequence in SeqIO.parse(fna_content, 'fasta'))
                # Mengambil hasil pertama (bisa disesuaikan sesuai kebutuhan)
                organism_name = match.group(1)

                if organism_name:
                    for sequence_info in sequences_info:
                        edited_organism_name = re.sub(r'^.{9}', '', organism_name).replace(' ', '-')
                        # Mengganti sequence.id dengan organism_name
                        updated_sequence_info = f">{edited_organism_name}\n{sequence_info.splitlines()[1]}\n"
                        # print("update:", updated_sequence_info)
                        alignment_data += updated_sequence_info
                        # print("Alignment Data:", alignment_data)
                else:
                    print(f"Error reading sequences: No match found for 'organism=' in {file_name}")
            else:
                print(f"Error reading sequences: No match found for 'organism=' in {file_name}")

        except Exception as e:
            print(f"Error reading sequences from {file_name}: {str(e)}")

    else:
        print(f"Failed to retrieve file {file_name}. Status code: {response.status_code}")

# Print alignment_data setelah semua file FNA terbaca
# print("Alignment Data:", alignment_data)

app.layout = html.Div([
    dashbio.AlignmentChart(
        id='my-default-alignment-viewer',
        data=alignment_data,
        height=900,
        tilewidth=30,
    ),
    html.Div(id='default-alignment-viewer-output')
])

@app.callback(
    Output('default-alignment-viewer-output', 'children'),
    Input('my-default-alignment-viewer', 'eventDatum')
)
def update_output(value):
    ctx = callback_context
    if not ctx.triggered:
        return 'No data.'
    
    trigger_id = ctx.triggered[0]['prop_id'].split('.')[0]

    if trigger_id == 'my-default-alignment-viewer':
        return str(value)
    elif trigger_id == 'some-other-trigger':
        # Handle other trigger logic
        return 'Other data.'

if __name__ == '__main__':
    app.run(debug=True)