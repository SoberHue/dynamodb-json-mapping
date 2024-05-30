import sys
from pathlib import Path

tools_path = Path(__file__).parent / 'tools'
if tools_path not in sys.path:
    sys.path.append(str(tools_path))

import streamlit as st



def show_home():
    st.set_page_config(page_title="JsonMapper", page_icon="🌞", layout="wide")
    st.page_link("Home.py", label="Home", icon="🏠")
    st.page_link("pages/S3toRS_Mapping.py", label="S3toRS_Mapping", icon="1️⃣")
    st.page_link("pages/Sort_ID.py", label="Sort_ID", icon="2️⃣")


if __name__ == '__main__':
    show_home()
