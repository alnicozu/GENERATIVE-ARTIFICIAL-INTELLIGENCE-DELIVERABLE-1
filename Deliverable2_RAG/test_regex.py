import re

textos = ["Artículo 9° de la regla", "ARTÍCULO 11 algo", "Art. 12", "artículo 13°", "Párrafo sin artículo"]

for p in textos:
    match_art = re.search(r'(?i)(art[íi]culo\s+\d+°?|art\.\s*\d+°?)', p)
    if match_art:
        print(f"Encontrado: {match_art.group(0)}")
    else:
        print("No encontrado")
