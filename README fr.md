# Convertisseur de PDF en CBZ (AVIF)

Ce script Python convertit un ou plusieurs fichiers PDF en archives CBZ en utilisant le format d'image AVIF afin d'optimiser la taille des fichiers de bandes dessinées.

## Caractéristiques

- Prise en charge d'un seul fichier PDF ou d'un répertoire de PDF
- Conversion des pages/images en AVIF
- Génération d'archives CBZ
- Suivi du temps d'exécution
- Rapport sur la taille des entrées/sorties
- Analyse du nombre de pages
- Tableau récapitulatif affiché dans le terminal
- Génération d'un fichier journal avec horodatage

## Exigences

- Python 3
- Dépendances (voir `requirements.txt`)
- ImageMagick installé (requis pour `wand`)

## Installation

```bash
pip install -r requirements.txt
pipenv install -r requirements.txt
```

Assurez-vous que ImageMagick est installé et accessible en ligne de commande (par exemple, `convert`, `magick`).

## Utilisation

### Fichier PDF unique

```bash
./pdftocbz <qualité> <largeur> <hauteur> <entrée.pdf> <sortie.cbz>
```

### Répertoire des PDF

```bash
./pdftocbz <qualité> <largeur> <hauteur> <dossier_d'entrée> <dossier_de_sortie>
```

### Exemple

```bash
./pdftocbz 50 1600 2560 book.pdf output.cbz
./pdftocbz 60 1024 1600 livres/ cbz_sortie/
```

## Sortie

- Un fichier `.cbz` pour chaque PDF
- Un fichier journal `conversion_stats_YYYYMMDD_HHMMSS.txt` avec :
  - Nom du fichier
  - Nombre de pages
  - Taille de l'entrée/sortie
  - Temps de conversion

## Licence

Licence MIT
