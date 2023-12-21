from flask import Flask, render_template, request
from dash import Dash, html, Input, Output, callback, callback_context
import dash_bio as dashbio
import requests
import configparser
import numpy as np
from Bio import SeqIO
from io import StringIO
import re
from furl import furl

# Initialize Flask app
server = Flask(__name__)

# Initialize Dash app as a Flask Blueprint
app = Dash(__name__, server=server, url_base_pathname='/dash/')

github_url = 'https://github.com/anneutsabita/Dataset-MSA/raw/main/genes/'

def download_sequence_data(file_name):
    fna_url = github_url + file_name
    response = requests.get(fna_url)

    if response.status_code == 200:
        return response.text
    else:
        print(f"Failed to retrieve file {file_name}. Status code: {response.status_code}")
        return None

def process_sequence_data(data):
    match = re.search(r'\[([^\]]+=[^\]]+)\]', data)
    if not match:
        print(f"Error reading sequences: No match found")
        return None

    organism_name = match.group(1)
    if not organism_name:
        print(f"Error reading sequences: No organism name found")
        return None

    sequences_info = (f">{sequence.id}\n{sequence.seq}\n" for sequence in SeqIO.parse(StringIO(data), 'fasta'))
    return organism_name, sequences_info

def update_alignment_data(organism_name, sequences_info):
    if not organism_name or not sequences_info:
        return None

    alignment_data = ""
    for sequence_info in sequences_info:
        edited_organism_name = re.sub(r'^.{9}', '', organism_name).replace(' ', '-')
        updated_sequence_info = f">{edited_organism_name}\n{sequence_info.splitlines()[1]}\n"
        alignment_data += updated_sequence_info

    return alignment_data

def get_combined_alignment_data(file_list):
    alignment_data = ""
    for file_name in file_list:
        data = download_sequence_data(file_name)

        if data:
            result = process_sequence_data(data)
            if result:
                organism_name, sequences_info = result
                alignment_data += update_alignment_data(organism_name, sequences_info)

    return alignment_data

def create_app_layout(alignment_data):
    return html.Div([
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

@server.route('/list')
def render_index():
   # Retrieve values for param1 to param7 from query parameters
    param1_values = request.args.getlist('param1')
    param2_values = request.args.getlist('param2')
    param3_values = request.args.getlist('param3')
    param4_values = request.args.getlist('param4')
    param5_values = request.args.getlist('param5')
    param6_values = request.args.getlist('param6')
    param7_values = request.args.getlist('param7')

    # Combine the file lists based on the parameters
    combined_file_list = (
       param1_values + param2_values + 
       param3_values + param4_values + 
       param5_values + param6_values + 
       param7_values
    )

    if not combined_file_list:
        combined_file_list = ['gene_Arabidopsis-thaliana.fna']

        
    # Get the combined alignment data
    alignment_data = get_combined_alignment_data(combined_file_list)

    # Set the Dash app layout
    app.layout = create_app_layout(alignment_data)
    return render_template('multiple.html')

@server.route('/')
def index():
   # Retrieve values for param1 to param7 from query parameters
    param1_values = request.args.getlist('param1')
    param2_values = request.args.getlist('param2')
    param3_values = request.args.getlist('param3')
    param4_values = request.args.getlist('param4')
    param5_values = request.args.getlist('param5')
    param6_values = request.args.getlist('param6')
    param7_values = request.args.getlist('param7')

    

    # Combine the file lists based on the parameters
    combined_file_list = (
       param1_values + param2_values + 
       param3_values + param4_values + 
       param5_values + param6_values + 
       param7_values
    )

    if not combined_file_list:
        combined_file_list = ['gene_Arabidopsis-thaliana.fna']

        
    # Get the combined alignment data
    alignment_data = get_combined_alignment_data(combined_file_list)

    # Set the Dash app layout
    app.layout = create_app_layout(alignment_data)
    return render_template('index.html')

@server.route('/about')
def about():
   # Retrieve values for param1 to param7 from query parameters
    param1_values = request.args.getlist('param1')
    param2_values = request.args.getlist('param2')
    param3_values = request.args.getlist('param3')
    param4_values = request.args.getlist('param4')
    param5_values = request.args.getlist('param5')
    param6_values = request.args.getlist('param6')
    param7_values = request.args.getlist('param7')

    

    # Combine the file lists based on the parameters
    combined_file_list = (
       param1_values + param2_values + 
       param3_values + param4_values + 
       param5_values + param6_values + 
       param7_values
    )

    if not combined_file_list:
        combined_file_list = ['gene_Arabidopsis-thaliana.fna']

        
    # Get the combined alignment data
    alignment_data = get_combined_alignment_data(combined_file_list)

    # Set the Dash app layout
    app.layout = create_app_layout(alignment_data)
    return render_template('about.html')

if __name__ == '__main__':
    server.run(debug=True)
