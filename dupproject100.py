import os
import sys
import requests
from bs4 import BeautifulSoup
from flask import Flask, send_from_directory
from urllib.parse import urljoin
print ("Script made by 0led22 on github")
app = Flask(__name__)

def download_resource(url, base_url, save_dir):
    if not url.startswith(('http://', 'https://')):
        
        url = urljoin(base_url, url)
    
    
    filename = os.path.basename(url).split('?')[0].split('#')[0]
    filename = "".join(x for x in filename if x.isalnum() or x in ('_', '-', '.'))
    if not filename:
        
        filename = 'resource'
    
    filename = os.path.join(save_dir, filename)
    
    
    count = 1
    while os.path.exists(filename):
        count += 1
        name, extension = os.path.splitext(filename)
        filename = f"{name}_{count}{extension}"

    with open(filename, 'wb') as f:
        response = requests.get(url)
        f.write(response.content)
    
    return os.path.basename(filename)

def download_webpage(url):
    response = requests.get(url)
    if response.status_code == 200:
        html_content = response.text
        soup = BeautifulSoup(html_content, 'html.parser')

        
        templates_dir = 'templates'
        os.makedirs(templates_dir, exist_ok=True)

        
        resource_dir = os.path.join('static', 'resources')
        os.makedirs(resource_dir, exist_ok=True)

        
        base_url = response.url
        for tag in soup.find_all(['img', 'link', 'script']):
            if 'src' in tag.attrs:
                resource_url = tag.attrs['src']
                filename = download_resource(resource_url, base_url, resource_dir)
                tag.attrs['src'] = f'/static/resources/{filename}'
            elif 'href' in tag.attrs:
                resource_url = tag.attrs['href']
                filename = download_resource(resource_url, base_url, resource_dir)
                tag.attrs['href'] = f'/static/resources/{filename}'

        
        with open(os.path.join(templates_dir, 'page.html'), 'w', encoding='utf-8') as f:
            f.write(str(soup))

        print("Parsisiuntimas pavyko.(success)")
    else:
        print("Parsisiuntimas nepavyko.(failed)")

@app.route('/')
def serve_webpage():
    return send_from_directory('templates', 'page.html')

@app.route('/static/resources/<path:filename>')
def serve_static(filename):
    return send_from_directory('static/resources', filename)

if __name__ == '__main__':
    if len(sys.argv) != 2:
        url = input("Iveskite puslapio URL(Insert URL): ")
    else:
        url = sys.argv[1]
    
    download_webpage(url)
    app.run(port=8000, debug=False)
