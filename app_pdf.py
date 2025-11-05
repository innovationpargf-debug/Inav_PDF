# =====================================================
# 🧠 Auteur : Inav
# 🌍 Application : PDF Tool - Fusion, Défusion, Compression
# =====================================================

import streamlit as st
from PyPDF2 import PdfReader, PdfWriter, PdfMerger
import tempfile, os, shutil, zipfile, subprocess

# -----------------------------------------------------
# 🏷️ Configuration de la page
# -----------------------------------------------------
st.set_page_config(page_title="🧩 PDF Tool", page_icon="📘", layout="centered")

st.title("🧩 Inav PDF Tool – Fusion, Défusion, Compression")
st.markdown("Inav vous propose cet outil simple et rapide pour manipuler vos fichiers PDF sans crainte 🚀")

# -----------------------------------------------------
# 🔧 Fonctions utilitaires
# -----------------------------------------------------

def save_uploaded_file(uploaded_file):
    """Sauvegarde un fichier uploadé (Streamlit) dans un fichier temporaire sur le disque"""
    temp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    temp.write(uploaded_file.read())
    temp.flush()
    temp.close()
    return temp.name


def fusionner_pdfs(file_paths):
    """Fusionne plusieurs PDF et retourne le chemin du PDF fusionné"""
    merger = PdfMerger()
    for file in file_paths:
        merger.append(file)
    temp_output = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    merger.write(temp_output.name)
    merger.close()
    return temp_output.name


def defusionner_pdf(file_path):
    """Défusionne un PDF et retourne un fichier ZIP avec les pages séparées"""
    reader = PdfReader(file_path)
    temp_dir = tempfile.mkdtemp()

    for i, page in enumerate(reader.pages):
        writer = PdfWriter()
        writer.add_page(page)
        output_page = os.path.join(temp_dir, f"page_{i+1}.pdf")
        with open(output_page, "wb") as f:
            writer.write(f)

    zip_path = os.path.join(temp_dir, "pages_pdf.zip")
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file in os.listdir(temp_dir):
            if file.endswith(".pdf"):
                zipf.write(os.path.join(temp_dir, file), file)

    return zip_path, len(reader.pages)


def compresser_pdf(file_path, niveau):
    """Compresse un PDF avec Ghostscript (si disponible)"""
    temp_output = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    levels = {
        "Petite": "/printer",
        "Moyenne": "/ebook",
        "Grande": "/screen",
        "Extrême": "/screen"
    }

    cmd = (
        f'gs -sDEVICE=pdfwrite -dCompatibilityLevel=1.3 '
        f'-dPDFSETTINGS={levels[niveau]} '
        f'-dNOPAUSE -dQUIET -dBATCH '
        f'-sOutputFile="{temp_output.name}" "{file_path}"'
    )

    # Exécution de Ghostscript si présent
    try:
        subprocess.call(cmd, shell=True)
        return temp_output.name
    except Exception as e:
        st.error("⚠️ Erreur de compression : Ghostscript non disponible.")
        return None


# -----------------------------------------------------
# 🧭 Menu principal
# -----------------------------------------------------

action = st.sidebar.radio(
    "Choisissez une action :",
    ["Fusionner des PDF", "Défusionner un PDF", "Compresser un PDF"]
)

# -----------------------------------------------------
# 🔗 1️⃣ Fusionner
# -----------------------------------------------------
if action == "Fusionner des PDF":
    st.header("🔗 Fusionner des PDF")
    files = st.file_uploader("Choisissez plusieurs fichiers PDF à fusionner :", type="pdf", accept_multiple_files=True)

    if st.button("Fusionner") and files:
        with st.spinner("Fusion en cours..."):
            # Enregistrer tous les fichiers temporairement
            temp_paths = [save_uploaded_file(f) for f in files]

            merged_path = fusionner_pdfs(temp_paths)
            for p in temp_paths:
                os.remove(p)  # Nettoyage

        with open(merged_path, "rb") as f:
            st.success(f"✅ Fusion terminée ({len(files)} fichiers).")
            st.download_button("📥 Télécharger le PDF fusionné", f, file_name="PDF_Fusionne.pdf")

# -----------------------------------------------------
# ✂️ 2️⃣ Défusionner
# -----------------------------------------------------
elif action == "Défusionner un PDF":
    st.header("✂️ Défusionner un PDF")
    file = st.file_uploader("Choisissez un fichier PDF :", type="pdf")

    if st.button("Défusionner") and file:
        with st.spinner("Défusion en cours..."):
            file_path = save_uploaded_file(file)
            zip_path, pages = defusionner_pdf(file_path)
            os.remove(file_path)  # Nettoyage

        with open(zip_path, "rb") as f:
            st.success(f"✅ Le document contient {pages} pages.")
            st.download_button("📦 Télécharger le ZIP", f, file_name="pages_pdf.zip")

# -----------------------------------------------------
# 🗜️ 3️⃣ Compresser
# -----------------------------------------------------
elif action == "Compresser un PDF":
    st.header("🗜️ Compresser un PDF")
    file = st.file_uploader("Choisissez un fichier PDF :", type="pdf")
    niveau = st.selectbox("Niveau de compression :", ["Petite", "Moyenne", "Grande", "Extrême"])

    if st.button("Compresser") and file:
        with st.spinner("Compression en cours..."):
            file_path = save_uploaded_file(file)
            compressed_path = compresser_pdf(file_path, niveau)
            os.remove(file_path)  # Nettoyage

        if compressed_path:
            with open(compressed_path, "rb") as f:
                st.success("✅ Compression terminée.")
                st.download_button("📥 Télécharger le PDF compressé", f, file_name="PDF_compresse.pdf")
        else:
            st.error("❌ Échec de la compression. Ghostscript peut ne pas être disponible sur ce serveur.")

# -----------------------------------------------------
# 🧾 Pied de page
# -----------------------------------------------------
st.markdown("---")
st.caption("🧠 Développé avec ❤️ par Gael FOKA")
