import streamlit as st
from io import StringIO
from pathlib import Path
from tools.utils import current_time, download_button


def main():
    st.title("Sort ID")
    on1 = st.toggle("according group or index")
    start_id = 1
    if on1:
        st.write("according group")
    else:
        st.write("according index")
        start_id = st.number_input("input start number:  :rainbow[[id]]", value=1,
                                   placeholder="type a number...", step=1)
    uploaded_template_file = st.file_uploader("upload JSON", type=['json'])
    if uploaded_template_file:
        if st.button("generate JSON file", type="primary"):
            with st.spinner('wait for it...'):
                import json
                stringio = StringIO(uploaded_template_file.getvalue().decode("utf-8"))
                data = json.loads(stringio.read())

                for index, item in enumerate(data, start=start_id):
                    if on1:
                        item["id"] = f"{item['target_database']}.{item['target_schema']}.{item['target_table']}"
                    else:
                        item["id"] = str(index)
                updated_json_data = json.dumps(data, indent=4)
                temp_file = Path(f"static/temp/{int(current_time())}.json")
                with open(temp_file, 'w') as f:
                    f.write(updated_json_data)
                download_button("Download Converted JSON", temp_file, 'json')


if __name__ == '__main__':
    main()
