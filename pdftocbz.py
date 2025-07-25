#!/usr/bin/env python3
"""
Script de conversion de PDF en CBZ avec images AVIF.

Fonctionnalités :
- Traite un fichier PDF ou un répertoire complet.
- Convertit chaque page (ou image) en format AVIF.
- Archive les images en fichier CBZ.
- Journalise les statistiques dans un fichier daté.

Utilisation :
- Fichier unique : ./pdftocbz_fusion.py 90  1600 2560 monfichier.pdf sortie.cbz [logfile]
- Répertoire     : ./pdftocbz_fusion.py 90  1600 2560 dossier_pdf dossier_cbz [logfile]
"""

import fitz  # PyMuPDF
from wand.image import Image
from wand.color import Color
import os
import zipfile
import argparse
import time
import shutil
from datetime import datetime

def gestion_extension(fichier,ext):
    nom_sans_ext, _ = os.path.splitext(fichier)
    return nom_sans_ext + ext


def convert_avif(file_tempo, page_imp, quality, width, height, tempo, image_avif):
    with Image(filename=file_tempo) as img:
        img.background_color = Color("white")
        img.alpha_channel = "remove"
        img.compression_quality = quality
        img.resize(width, height)
        img_avif = os.path.join(tempo, f"page_{page_imp:03}.avif")
        img.save(filename=img_avif)
        image_avif.append(img_avif)

def pdf_to_cbz(input_pdf, output_cbz, quality, width, height):
    start_time = time.time()
    temp_dir = "temp_images"
    os.makedirs(temp_dir, exist_ok=True)
    img_jpeg = os.path.join(temp_dir, "tempo.jpeg")
    output_cbz = gestion_extension(output_cbz, ".cbz")
    doc = fitz.open(input_pdf)
    image_avif = []
    num_pages = len(doc)

    print(f"Traitement du fichier {input_pdf} avec {num_pages} pages")

    for page_index in range(num_pages):
        page = doc[page_index]
        image_list = page.get_images(full=True)
        page_imp = page_index + 1

        if image_list and len(image_list) == 1:
            xref = image_list[0][0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            with open(img_jpeg, "wb") as img_file:
                img_file.write(image_bytes)
            convert_avif(img_jpeg, page_imp, quality, width, height, temp_dir, image_avif)
        else:
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
            pix.save(img_jpeg)
            convert_avif(img_jpeg, page_imp, quality, width, height, temp_dir, image_avif)

    with zipfile.ZipFile(output_cbz, "w", zipfile.ZIP_DEFLATED) as cbz:
        for img_file in sorted(image_avif):
            cbz.write(img_file, os.path.basename(img_file))
            os.remove(img_file)

    if os.path.exists(img_jpeg):
        os.remove(img_jpeg)
    shutil.rmtree(temp_dir)

    duration = time.time() - start_time
    size_before = os.path.getsize(input_pdf)
    size_after = os.path.getsize(output_cbz)

    return {
        "fichier": os.path.basename(input_pdf),
        "pages": num_pages,
        "taille_init": size_before,
        "taille_finale": size_after,
        "temps": duration
    }

def convert_directory(pdf_dir, output_dir, quality, width, height):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    elif not os.path.isdir(output_dir):
        print("Erreur : Le chemin de sortie doit être un dossier.")
        exit(1)

    stats = []
    for filename in os.listdir(pdf_dir):
        if filename.lower().endswith(".pdf"):
            pdf_path = os.path.join(pdf_dir, filename)
            cbz_name = os.path.splitext(filename)[0] + ".cbz"
            output_cbz = os.path.join(output_dir, cbz_name)
            stat = pdf_to_cbz(pdf_path, output_cbz, quality, width, height)
            stats.append(stat)
    return stats

def afficher_tableau(stats, log_file=None, quality=None, width=None, height=None):
    header = "Fichier\tPages\tTaille_init_Ko\tTaille_finale_Ko\tTemps_s"
    separator = "\n"
    lignes = [header, separator]
    for s in stats:
        ligne = f"{s['fichier']}\t{s['pages']}\t{s['taille_init']/1024:.1f}\t{s['taille_finale']/1024:.1f}\t{s['temps']:.2f}\n"
        lignes.append(ligne)
    lignes.append(separator)

    print("Résumé des conversions :\n" + "".join(lignes))
    log_file= gestion_extension(log_file,".csv")
    if log_file:
        with open(log_file, "a", encoding="utf-8") as f:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"Rapport de conversion - {now}\n")
            if quality is not None and width is not None and height is not None:
                f.write(f"Paramètres du traitement : Qualité={quality}, Largeur={width}, Hauteur={height}\n\n")
            f.writelines(lignes)
        print(f"\nStatistiques enregistrées dans : {log_file}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convertir un ou plusieurs PDF en CBZ (Comic Book Archive)")
    parser.add_argument("quality", type=int, help="Qualité de compression (1-100)")
    parser.add_argument("width", type=int, help="Largeur de redimensionnement")
    parser.add_argument("height", type=int, help="Hauteur de redimensionnement")
    parser.add_argument("input_path", type=str, help="Fichier PDF ou dossier contenant des PDFs")
    parser.add_argument("output_path", type=str, help="Nom du fichier CBZ ou dossier de sortie")
    parser.add_argument("output_log",  nargs='?', type=str, help="Nom du fichier de statistiques")


    args = parser.parse_args()
    stats = []
    if not os.path.exists(args.input_path):
        print("Erreur : L'entrée n'existe pas")
        exit(1)
    if os.path.isdir(args.input_path):
        if not os.path.isdir(args.output_path):
            print("Erreur : lorsque l'entrée est un dossier, la sortie doit être un dossier.")
            exit(2)
        stats = convert_directory(args.input_path, args.output_path, args.quality, args.width, args.height)
    else:
        output_dir = os.path.dirname(args.output_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
        stat = pdf_to_cbz(args.input_path, args.output_path, args.quality, args.width, args.height)
        stats.append(stat)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    if not args.output_log :
        log_filename = f"conversion_stats_{timestamp}.csv"
    else:
        log_dir = os.path.dirname(args.output_log)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
        log_filename = args.output_log

    afficher_tableau(stats, log_filename, quality=args.quality, width=args.width, height=args.height)
