

import requests
from flask import Flask, jsonify
import os

from bs4 import BeautifulSoup

template_dir = os.path.abspath('.')
app = Flask(__name__, template_folder=template_dir)

##############################################################################################################################
def get_stats():
    url = 'https://www.worldometers.info/coronavirus/'
    res = requests.get(url)
    if res.status_code != 200:
        return {}
    
    html = res.text
    soup = BeautifulSoup(html, 'html.parser')
    tables = {}
    for table_id in ['main_table_countries_today', 'main_table_countries_yesterday']:
        data_table = soup.find("table", {"id": table_id})
        
        header_cells = data_table.find('thead').find_all('th')
        rows = data_table.find('tbody').find_all('tr')
        
        header_cells_values = []
        for header_cell in header_cells:
            header_cell_value = header_cell.text.replace('\xa0', ' ')
            header_cells_values.append(header_cell_value)
        
        info_per_country = {}
        for row in rows:
            country_info = {}
            country_name = None
            for i, cell in enumerate(row.find_all('td')):
                cell_value = cell.text.replace(',', '').replace('+', '').strip()
                if i == 0:
                    country_name = cell_value
                    info_per_country[country_name] = {}
                else:
                    if cell_value == '':
                        cell_value = '0'
                    info_per_country[country_name][header_cells_values[i]] = cell_value
        
        tables[table_id] = info_per_country
    
    return tables

##############################################################################################################################

@app.route('/get_stats/', methods=['GET'])
def get_stats_api():
    info_per_country = get_stats()
    
    return jsonify(info_per_country)


@app.route('/get_stats/<country>', methods=['GET'])
def get_stats_country_api(country):
    tables = get_stats()
    
    country_tables = {}
    for table_id in tables:
        info_per_country = tables[table_id]
        country_info = {}
        if country in info_per_country:
            country_info[country] = info_per_country[country]
        country_tables[table_id] = country_info
    
    return jsonify(country_tables)

##############################################################################################################################

if __name__ == '__main__':
    app.run(host='0.0.0.0', port='1111', debug=True)


