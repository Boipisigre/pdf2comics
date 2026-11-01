# Spécification Technique : Script de Conversion PDF vers CBZ (AVIF)

## Objectif

Ce script permet de convertir un ou plusieurs fichiers PDF en fichiers CBZ, en convertissant chaque page (ou image) en format AVIF, avec journalisation des statistiques de conversion.

## Fonctionnalités

- Prise en charge d'un fichier PDF unique ou d'un répertoire contenant plusieurs PDF.
- Conversion des pages en images AVIF.
- Archivage des images AVIF en fichier CBZ.
- Mesure du temps de traitement pour chaque fichier.
- Calcul de la taille avant et après traitement.
- Comptage du nombre de pages par document.
- Affichage d'un tableau récapitulatif dans la console.
- Génération d'un fichier de log contenant les statistiques (date, taille, temps, etc.).

## Utilisation

```bash
./pdftocbz <qualité> < <largeur> <hauteur> chemin_entrée> <chemin_sortie>
```

### Paramètres

1. **qualité** : Entier de 1 à 100, définit la qualité de compression AVIF.
4. **largeur** : Largeur cible des images.
5. **hauteur** : Hauteur cible des images.
2. **chemin\_entrée** :
   - Fichier PDF unique.
   - Ou répertoire contenant des fichiers PDF.
3. **chemin\_sortie** :
   - Fichier `.cbz` si entrée est un fichier.
   - Répertoire si entrée est un dossier.


## Détails de traitement

- Les pages contenant une seule image sont extraites directement.
- Les autres pages sont rendues sous forme d'image (via PyMuPDF).
- Redimensionnement et conversion en AVIF via Wand (ImageMagick).
- Les images AVIF sont ajoutées à un fichier ZIP renommé en `.cbz`.

## Récapitulatif de sortie

Un tableau affiché en fin de script contient :

| Fichier | Pages | Taille initiale (Ko) | Taille finale (Ko) | Temps (s) |
| ------- | ----- | -------------------- | ------------------ | --------- |

## Fichier de log

- Nom : `conversion_stats_YYYYMMDD_HHMMSS.txt`
- Contenu : identique au tableau affiché, avec horodatage en tête.
- Format texte simple, encodage UTF-8.

## Prérequis techniques

- Python 3
- Bibliothèques :
  - `fitz` (PyMuPDF)
  - `wand` (ImageMagick bindings)
  - `argparse`, `os`, `time`, `zipfile`, `shutil`, `datetime`

## Gestion des erreurs

- Vérification de l'existence des répertoires.
- Vérification que le chemin de sortie est un fichier ou un dossier selon le contexte.
- Arrêt avec message explicite en cas de problème de chemin ou de type de fichier.

## Exemple

```bash
./pdftocbz 90  1600 2560 livre.pdf sortie.cbz
./pdftocbz 85 1024 1600  docs/ cbz_output/
```
