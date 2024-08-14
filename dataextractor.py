import os
import json
from bs4 import BeautifulSoup

# Chemin du répertoire contenant les fichiers index.html
base_dir = './data'

# Liste pour stocker les données extraites
data = []

# Parcourir les sous-répertoires

# Parcourir les sous-répertoires
for root, dirs, files in os.walk(base_dir):
    for file in files:
        if file == 'index.html':
            # Construire le chemin complet vers le fichier index.html
            file_path = os.path.join(root, file)
            
            # Lire le contenu du fichier index.html
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Utiliser BeautifulSoup pour parser le contenu HTML
            soup = BeautifulSoup(content, 'html.parser')
            
            # Extraire tous les éléments <tr> avec le style "height: 17px;"
            trs = soup.find_all('tr', style="height: 17px;")
            
            # Liste pour stocker les données extraites pour ce dossier
            folder_data = []

            # Parcourir chaque <tr> et extraire les <td>
            for tr in trs:
                tds = tr.find_all('td')
                td_pairs = []
                
                # Parcourir les <td> par paires
                for i in range(0, len(tds) - 1, 2):
                    td_name = tds[i]
                    td_value = tds[i + 1]
                    
                    # Vérifier si le <td> contient une balise <b> et si la valeur n'est pas vide
                    if td_name.find('b') and td_value.get_text(strip=True):
                        name = td_name.get_text(strip=True)
                        value = td_value.get_text(strip=True)
                        td_pairs.append({"name": name, "value": value})
                
                # Ajouter les paires extraites à la liste de données du dossier
                if td_pairs:
                    folder_data.extend(td_pairs)

            # Nom du répertoire parent
            dir_name = os.path.basename(root)
            
            # Sauvegarder les données dans un fichier JSON spécifique au dossier
            output_file = f'{dir_name}_data.json'
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(folder_data, f, ensure_ascii=False, indent=4)

            print(f"Données extraites et sauvegardées dans {output_file} pour le dossier {dir_name}")