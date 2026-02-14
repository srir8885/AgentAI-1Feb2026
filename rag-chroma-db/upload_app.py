from typing import List

import streamlit as st
from langchain_core.documents import Document
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pypdf import PdfReader

st.set_page_config(page_title="Chroma Cloud Ingest", layout="wide")

st.title("Chroma Cloud Ingest")
st.caption("Upload or paste content to build a RAG index.")