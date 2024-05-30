import streamlit as st
from io import StringIO
from pathlib import Path
from tools.utils import current_time, download_button


def main():
    st.title("Sort ID")
    on1 = st.toggle("According Group or Index")
    if on1:
        st.write("According Group")
    else:
        st.write("According Index")
    uploaded_template_file = st.file_uploader("upload json", type=['json'])
    if uploaded_template_file:
        if st.button("Generate JSON file", type="primary"):
            with st.spinner('Wait for it...'):
                import json
                stringio = StringIO(uploaded_template_file.getvalue().decode("utf-8"))
                data = json.loads(stringio.read())

                for index, item in enumerate(data, start=1):
                    if on1:
                        item["id"] = f"{item['target_database']}-{item['target_schema']}-{item['target_table']}"
                    else:
                        item["id"] = str(index)
                updated_json_data = json.dumps(data, indent=4)
                temp_file = Path(f"static/temp/{int(current_time())}.json")
                with open(temp_file, 'w') as f:
                    f.write(updated_json_data)
                download_button("Download Converted JSON", temp_file, 'json')


if __name__ == '__main__':
    main()
