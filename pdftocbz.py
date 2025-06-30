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
#!/usr/bin/env python3
import fitz  # PyMuPDF
from wand.image import Image
from wand.color import Color
import os
import zipfile
import argparse
import time
import shutil
from datetime import datetime
from concurrent.futures import ProcessPoolExecutor, as_completed
import multiprocessing
import tempfile

def gestion_extension(fichier, ext):
    return os.path.splitext(fichier)[0] + ext

def convertir_et_enregistrer_avif(img_jpeg, page_num, quality, width, height, temp_dir):
    with Image(filename=img_jpeg) as img:
        img.background_color = Color("white")
        img.alpha_channel = "remove"
        img.compression_quality = quality
        img.resize(width, height)
        avif_path = os.path.join(temp_dir, f"page_{page_num:03}.avif")
        img.save(filename=avif_path)
        return avif_path

def extraire_image_pdf(page, doc, img_jpeg):
    images = page.get_images(full=True)
    if images and len(images) == 1:
        xref = images[0][0]
        image_data = doc.extract_image(xref)["image"]
        with open(img_jpeg, "wb") as f:
            f.write(image_data)
    else:
        pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
        pix.save(img_jpeg)

def pdf_to_cbz(input_pdf, output_cbz, quality, width, height):
    start_time = time.time()
    temp_dir = tempfile.mkdtemp(prefix="cbz_temp_")
    output_cbz = gestion_extension(output_cbz, ".cbz")
    doc = fitz.open(input_pdf)
    image_avif = []

    for page_index, page in enumerate(doc):
        page_num = page_index + 1
        # Temp JPEG unique pour chaque page
        with tempfile.NamedTemporaryFile(suffix=".jpeg", delete=False, dir=temp_dir) as tmp_jpeg:
            img_jpeg = tmp_jpeg.name

        image_list = page.get_images(full=True)
        if image_list and len(image_list) == 1:
            xref = image_list[0][0]
            image_bytes = doc.extract_image(xref)["image"]
            with open(img_jpeg, "wb") as f:
                f.write(image_bytes)
        else:
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
            pix.save(img_jpeg)

        avif_path = convertir_et_enregistrer_avif(img_jpeg, page_num, quality, width, height, temp_dir)
        image_avif.append(avif_path)
        os.remove(img_jpeg)

    with zipfile.ZipFile(output_cbz, "w", zipfile.ZIP_DEFLATED) as cbz:
        for img in sorted(image_avif):
            cbz.write(img, os.path.basename(img))
            os.remove(img)

    shutil.rmtree(temp_dir)

    return {
        "fichier": os.path.basename(input_pdf),
        "pages": len(doc),
        "taille_init": os.path.getsize(input_pdf),
        "taille_finale": os.path.getsize(output_cbz),
        "temps": time.time() - start_time
    }
def convert_directory(pdf_dir, output_dir, quality, width, height, max_workers=None):
    os.makedirs(output_dir, exist_ok=True)
    stats = []

    def worker(pdf_filename):
        if not pdf_filename.lower().endswith(".pdf"):
            return None
        input_pdf = os.path.join(pdf_dir, pdf_filename)
        output_cbz = os.path.join(output_dir, gestion_extension(pdf_filename, ".cbz"))
        try:
            return pdf_to_cbz(input_pdf, output_cbz, quality, width, height)
        except Exception as e:
            print(f"Erreur sur {pdf_filename} : {e}")
            return None

    pdf_files = [f for f in os.listdir(pdf_dir) if f.lower().endswith(".pdf")]
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(worker, f): f for f in pdf_files}
        for future in as_completed(futures):
            result = future.result()
            if result:
                stats.append(result)

    return stats

def afficher_tableau(stats, log_file=None, quality=None, width=None, height=None):
    lignes = ["Fichier\tPages\tTaille_init_Ko\tTaille_finale_Ko\tTemps_s\n", "\n"]
    for s in stats:
        lignes.append(f"{s['fichier']}\t{s['pages']}\t{s['taille_init']/1024:.1f}\t{s['taille_finale']/1024:.1f}\t{s['temps']:.2f}\n")
    lignes.append("\n")
    print("Résumé des conversions :\n" + "".join(lignes))

    if log_file:
        log_file = gestion_extension(log_file, ".csv")
        with open(log_file, "a", encoding="utf-8") as f:
            now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"Rapport de conversion - {now}\n")
            if quality and width and height:
                f.write(f"Paramètres : Qualité={quality}, Largeur={width}, Hauteur={height}\n\n")
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
    parser.add_argument("--threads", type=int, default=None, help="Nombre de threads pour traiter les PDFs en parallèle")

    args = parser.parse_args()
    stats = []

    if not os.path.exists(args.input_path):
        print("Erreur : L'entrée n'existe pas")
        exit(1)

    if os.path.isdir(args.input_path):
        if not os.path.isdir(args.output_path):
            print("Erreur : si l'entrée est un dossier, la sortie doit l'être aussi.")
            exit(2)
        stats = convert_directory(args.input_path, args.output_path, args.quality, args.width, args.height , max_workers=args.threads)
    else:
        os.makedirs(os.path.dirname(args.output_path), exist_ok=True)
        stats.append(pdf_to_cbz(args.input_path, args.output_path, args.quality, args.width, args.height))

    log_name = args.output_log or f"conversion_stats_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    os.makedirs(os.path.dirname(log_name), exist_ok=True) if os.path.dirname(log_name) else None
    afficher_tableau(stats, log_name, args.quality, args.width, args.height)
