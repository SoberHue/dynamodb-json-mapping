from pathlib import Path
import streamlit as st
import datetime


def download_button(button_name:str, file_path: Path, file_type: str) -> None:
    try:
        with open(file_path, "rb") as file:
            file_bytes = file.read()
        if file_type in ['xlsx','zip','json']:
            if file_type == 'xlsx':
                mime_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            elif file_type == 'zip':
                mime_type = "application/zip"
            elif file_type == 'json':
                mime_type = "application/json"
            else:
                st.error(f"file_type: {file_type}. Unsupported file type.")
                mime_type = "text/plain"
            st.download_button(
                label=button_name,
                data=file_bytes,
                file_name=file_path.name,
                mime=mime_type
            )
        else:
            st.error(f"file_type: {file_type}. Unsupported file type.")
    except FileNotFoundError:
        st.error(f"File not found: {file_path}")


def generate_input(col: st.delta_generator.DeltaGenerator, col_name: str) -> str:
    if col_name.lower().startswith('is'):
        result = col.selectbox(
            col_name,
            ("Y", "N"),
            index=None,
            placeholder="Select Y or N ...",
        )
    else:
        result = col.text_input(col_name, "")

    return result

def current_time():
    return int(datetime.datetime.now().timestamp() * 1000)
