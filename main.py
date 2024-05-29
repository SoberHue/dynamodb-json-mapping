import io
import shutil
import streamlit as st
from tools.utils import download_button
from tools.json_mapper import JsonMapper
from pathlib import Path
import pandas as pd
from datetime import datetime, timedelta

COLS_NUM = 4
MAX_TEMP_FILES = 10
TEST_EXCEL = Path("static/test.xlsx")


def generate_json(uploaded_file, df, start_id, group, hierarchical_namespace):
    json_mapper = JsonMapper(uploaded_file, df, start_id, group, hierarchical_namespace)
    json_mapper.convert_all_sheets()
    output_zip = json_mapper.compress_folder()

    if output_zip:
        st.success("Convert success!Please download zip file!")
        download_button("Download Template Excel", output_zip, 'zip')
    else:
        st.error("Generator Failed.")


def count_files_and_directories(directory_path):
    if not directory_path.exists() or not directory_path.is_dir():
        raise ValueError(f"The path '{directory_path}' does not exist or is not a directory.")
    file_count = sum(1 for item in directory_path.iterdir() if item.is_file())
    dir_count = sum(1 for item in directory_path.iterdir() if item.is_dir())
    return file_count + dir_count


def remove_all_contents(directory_path):
    if not directory_path.exists() or not directory_path.is_dir():
        raise (f"The path '{directory_path}' does not exist or is not a directory.")
    for item in directory_path.iterdir():
        current_time = datetime.now()
        file_creation_time = datetime.fromtimestamp(item.stat().st_ctime)
        if file_creation_time < current_time - timedelta(minutes=1):
            if item.is_file():
                item.unlink()
            elif item.is_dir():
                shutil.rmtree(item)


def main():
    st.set_page_config(page_title="JsonMapper", page_icon="🌞", layout="wide")
    st.title("JSON Generator")
    st.markdown(
        """
        #### 使用说明:
        ##### UploadFile:
        + 参照 Download Test Excel
        + 支持多个Sheet页
        
        ##### id 和 column_sequence
        + id 根据页面设置 Input Start Number 开始累加生成,不必在UploadFile添加
        + column_sequence 按照 固定的组 ["target_database", "target_schema", "target_table"] 自动生成,不必在UploadFile添加
        
        ##### Sys Field 添加系统字段
        + 使用当前cdp模板 choose template -> sci_template
        + 自定义模板点击 I need upload my own template file! 即可上传(还没测)
        
        ##### Json Result
        + 默认 Excel 中所有条目和Sheet页内容生成一个文件
        + Generate separate JSON files based on groups? 选项支持 按照指定的分组 生成文件,注意此分组和上面生成id和column_sequence的固定组是分开的
        + 如果文件命名过长生成失败可以开启 hierarchical_namespace 递归目录生成文件.
        """
    )
    download_button("Download Test Excel", TEST_EXCEL, 'xlsx')
    st.header('Upload File', divider='rainbow')

    uploaded_file = st.file_uploader("Upload Prepared Excel", type=['xlsx'])
    start_id = st.number_input("Input Start Number:  :rainbow[[id]]", value=None,
                               placeholder="Type a number...", step=1)
    on1 = st.toggle("Add SysField")
    df = pd.DataFrame()
    if on1:
        st.header('Sys Field', divider='rainbow')
        on2 = st.toggle("I need upload my own template file!")
        if on2:
            uploaded_template_file = st.file_uploader("upload template xlsx", type=['xlsx'])
            if uploaded_template_file:
                df = pd.read_excel(io.BytesIO(uploaded_template_file))
        else:
            option = st.selectbox(
                "choose template",
                ("sci_template",),
                index=None,
                placeholder="Choose a exists template.")
            if option == "sci_template":
                df = pd.read_excel(Path(__file__).parent / "static" / "template" / "extra_df.xlsx")

        if not df.empty:
            #     columns = df.columns
            #     cols = st.columns(COLS_NUM)
            #     for i, col in enumerate(columns):
            #         col_index = i % COLS_NUM
            #         result = generate_input(cols[col_index], col)
            #         if result:
            #             df[col] = result
            df = st.data_editor(df, hide_index=True, use_container_width=True, num_rows="dynamic")
    if uploaded_file and start_id:
        st.header('Json Result', divider='rainbow')
        on3 = st.toggle("Generate separate JSON files based on groups?")
        group = None
        on4 = False
        if on3:
            on4 = st.toggle("hierarchical_namespace")
            group = st.multiselect(
                "Pick Group",
                ["target_database", "target_schema", "target_table", ],
                ["target_database", "target_schema", "target_table", ])
        if st.button("Generate JSON file", type="primary"):
            # clear cache
            temp_path = Path(__file__).parent / "static" / "temp"
            count = count_files_and_directories(temp_path)
            if count > MAX_TEMP_FILES:
                remove_all_contents(temp_path)
            # run
            if on4:
                generate_json(uploaded_file, df, start_id, group, True)
            else:
                generate_json(uploaded_file, df, start_id, group, False)


if __name__ == '__main__':
    main()
