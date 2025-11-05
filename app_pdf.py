# =====================================================
# 🧠 Auteur :Inav GF
# 🌍 Application : PDF Tool - Fusion, Défusion, Compression
# =====================================================

import streamlit as st
from PyPDF2 import PdfReader, PdfWriter, PdfMerger
import tempfile, os, shutil, zipfile, subprocess

st.set_page_config(page_title="🧩 PDF Tool", page_icon="📘", layout="centered")

st.title("🧩 PDF Tool – Fusion, Défusion, Compression")
st.markdown("Un outil simple et rapide pour manipuler vos fichiers PDF 🚀")

# --- Choix de l’action ---
action = st.sidebar.radio(
    "Choisissez une action :", 
    ["Fusionner des PDF", "Défusionner un PDF", "Compresser un PDF"]
)

# --- Fonction : Fusion ---
def fusionner_pdfs(files):
    merger = PdfMerger()
    for file in files:
        merger.append(file)
    temp_output = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    merger.write(temp_output.name)
    merger.close()
    return temp_output.name

# --- Fonction : Défusion ---
def defusionner_pdf(file):
    reader = PdfReader(file)
    temp_dir = tempfile.mkdtemp()
    for i in range(len(reader.pages)):
        writer = PdfWriter()
        writer.add_page(reader.pages[i])
        output_path = os.path.join(temp_dir, f"page_{i+1}.pdf")
        with open(output_path, "wb") as f:
            writer.write(f)
    zip_path = os.path.join(temp_dir, "pages_pdf.zip")
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for file in os.listdir(temp_dir):
            if file.endswith(".pdf"):
                zipf.write(os.path.join(temp_dir, file), file)
    return zip_path, len(reader.pages)

# --- Fonction : Compression ---
def compresser_pdf(file, niveau):
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
        f'-sOutputFile="{temp_output.name}" "{file}"'
    )
    subprocess.call(cmd, shell=True)
    return temp_output.name

# --- Action : Fusion ---
if action == "Fusionner des PDF":
    st.header("🔗 Fusionner des PDF")
    files = st.file_uploader("Choisissez plusieurs fichiers PDF à fusionner :", type="pdf", accept_multiple_files=True)
    if st.button("Fusionner") and files:
        with st.spinner("Fusion en cours..."):
            temp_files = [f.name for f in files]
            merged_path = fusionner_pdfs([f for f in [temp.name for temp in files]])
        with open(merged_path, "rb") as f:
            st.download_button("📥 Télécharger le PDF fusionné", f, file_name="PDF_Fusionne.pdf")

# --- Action : Défusion ---
elif action == "Défusionner un PDF":
    st.header("✂️ Défusionner un PDF")
    file = st.file_uploader("Choisissez un fichier PDF :", type="pdf")
    if st.button("Défusionner") and file:
        with st.spinner("Défusion en cours..."):
            temp_path = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
            temp_path.write(file.read())
            zip_path, pages = defusionner_pdf(temp_path.name)
        with open(zip_path, "rb") as f:
            st.success(f"✅ Le document contient {pages} pages.")
            st.download_button("📦 Télécharger le ZIP", f, file_name="pages_pdf.zip")

# --- Action : Compression ---
elif action == "Compresser un PDF":
    st.header("🗜️ Compresser un PDF")
    file = st.file_uploader("Choisissez un fichier PDF :", type="pdf")
    niveau = st.selectbox("Niveau de compression :", ["Petite", "Moyenne", "Grande", "Extrême"])
    if st.button("Compresser") and file:
        with st.spinner("Compression en cours..."):
            temp_path = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
            temp_path.write(file.read())
            compressed = compresser_pdf(temp_path.name, niveau)
        with open(compressed, "rb") as f:
            st.download_button("📥 Télécharger le PDF compressé", f, file_name="PDF_compresse.pdf")

st.markdown("---")
st.caption("Développé avec ❤️ par GF")
