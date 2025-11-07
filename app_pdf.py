import streamlit as st
from PyPDF2 import PdfReader, PdfWriter, PdfMerger
import tempfile, os, shutil, zipfile, subprocess

# -----------------------------------------------------
# Configuration de la page
# -----------------------------------------------------
st.set_page_config(page_title="🧩 PDF Tool", page_icon="📘", layout="centered")

st.title("🧩 Inav PDF Tool – Fusion, Défusion, Compression")
st.markdown("Un outil simple et rapide d'Inav pour manipuler vos fichiers PDF 🚀")

# -----------------------------------------------------
# Fonctions utilitaires
# -----------------------------------------------------

def save_uploaded_file(uploaded_file, folder="uploads"):
    """Sauvegarde un fichier uploadé dans un dossier temporaire persistant"""
    os.makedirs(folder, exist_ok=True)
    file_path = os.path.join(folder, uploaded_file.name)
    with open(file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    return file_path


def fusionner_pdfs(file_paths):
    """Fusionne plusieurs PDF et retourne le chemin du PDF fusionné"""
    merger = PdfMerger()
    for file in file_paths:
        try:
            merger.append(file)
        except Exception as e:
            st.error(f"Erreur lors de la lecture de {file} : {e}")
    output_path = os.path.join(tempfile.gettempdir(), "PDF_Fusionne.pdf")
    merger.write(output_path)
    merger.close()
    return output_path


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


def ghostscript_disponible():
    """Vérifie si Ghostscript est installé sur le serveur"""
    return shutil.which("gs") is not None


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

    try:
        subprocess.run(cmd, shell=True, check=True)
        return temp_output.name
    except subprocess.CalledProcessError:
        st.error("❌ Erreur : la compression avec Ghostscript a échoué.")
        return None
    except FileNotFoundError:
        st.error("❌ Ghostscript n'est pas installé sur ce serveur.")
        return None


def compresser_pdf_sans_gs(file_path, niveau):
    """Tentative de compression basique sans Ghostscript"""
    reader = PdfReader(file_path)
    writer = PdfWriter()

    for page in reader.pages:
        try:
            page.compress_content_streams()  # compresse les flux de contenu (si possible)
        except Exception:
            pass
        writer.add_page(page)

    output_path = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf").name
    with open(output_path, "wb") as f:
        writer.write(f)

    return output_path


# -----------------------------------------------------
# Menu principal
# -----------------------------------------------------
action = st.sidebar.radio(
    "Choisissez une action :",
    ["Fusionner des PDF", "Défusionner un PDF", "Compresser un PDF"]
)

# -----------------------------------------------------
# 🔗 Fusionner
# -----------------------------------------------------
if action == "Fusionner des PDF":
    st.header("🔗 Fusionner des PDF")
    files = st.file_uploader("Choisissez plusieurs fichiers PDF à fusionner :", type="pdf", accept_multiple_files=True)

    if st.button("Fusionner") and files:
        with st.spinner("Fusion en cours..."):
            folder = tempfile.mkdtemp()
            temp_paths = [save_uploaded_file(f, folder) for f in files]
            merged_path = fusionner_pdfs(temp_paths)

        with open(merged_path, "rb") as f:
            st.success(f"✅ Fusion terminée ({len(files)} fichiers).")
            st.download_button("📥 Télécharger le PDF fusionné", f, file_name="PDF_Fusionne.pdf")

        shutil.rmtree(folder, ignore_errors=True)

# -----------------------------------------------------
# ✂️ Défusionner
# -----------------------------------------------------
elif action == "Défusionner un PDF":
    st.header("✂️ Défusionner un PDF")
    file = st.file_uploader("Choisissez un fichier PDF :", type="pdf")

    if st.button("Défusionner") and file:
        with st.spinner("Défusion en cours..."):
            file_path = save_uploaded_file(file)
            zip_path, pages = defusionner_pdf(file_path)
            os.remove(file_path)

        with open(zip_path, "rb") as f:
            st.success(f"✅ Le document contient {pages} pages.")
            st.download_button("📦 Télécharger le ZIP", f, file_name="pages_pdf.zip")

# -----------------------------------------------------
# 🗜️ Compresser
# -----------------------------------------------------
elif action == "Compresser un PDF":
    st.header("🗜️ Compresser un PDF")
    file = st.file_uploader("Choisissez un fichier PDF :", type="pdf")
    niveau = st.selectbox("Niveau de compression :", ["Petite", "Moyenne", "Grande", "Extrême"])

    if st.button("Compresser") and file:
        with st.spinner("Compression en cours..."):
            file_path = save_uploaded_file(file)

            if ghostscript_disponible():
                st.info("🔍 Ghostscript détecté – compression optimale.")
                compressed_path = compresser_pdf(file_path, niveau)
            else:
                st.warning("⚠️ Ghostscript non disponible – compression simplifiée utilisée.")
                compressed_path = compresser_pdf_sans_gs(file_path, niveau)

            os.remove(file_path)

        if compressed_path and os.path.exists(compressed_path):
            with open(compressed_path, "rb") as f:
                st.success("✅ Compression terminée.")
                st.download_button("📥 Télécharger le PDF compressé", f, file_name="PDF_compresse.pdf")
        else:
            st.error("❌ Échec de la compression. Aucune sortie générée.")

# -----------------------------------------------------
# Pied de page
# -----------------------------------------------------
st.markdown("---")
st.caption("🧠 Développé avec ❤️ par Inav Gael FOKA")
