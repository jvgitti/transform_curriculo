import streamlit as st
import PyPDF2
import io

from transform_document import transform_document

st.title("Conversão de currículo")

arquivo_pdf = st.file_uploader("Faça o upload de um currículo em PDF", type=["pdf"])

if arquivo_pdf:
    pdf_reader = PyPDF2.PdfReader(arquivo_pdf)
    pages = pdf_reader.pages

    text = ""
    for page in pages:
        text += page.extract_text()

    # Exibe o PDF processado
    st.write("Convertendo Currículo...")

    nome_arquivo, doc = transform_document(text)

    bio = io.BytesIO()
    doc.save(bio)

    st.write("Currículo Processado")

    st.download_button(label='Download', data=bio.getvalue(), file_name=nome_arquivo, mime='application/octet-stream')
