import json
import re

import pandas as pd
from dataclasses import dataclass, field
from pathlib import Path
import streamlit as st
import io
import shutil
from typing import List
from tools.utils import current_time


@dataclass
class JsonMapper:
    _excel_bytes: io.BytesIO
    _extra_df: pd.DataFrame
    _name_group: List = None
    _hierarchical_namespace: bool = False
    _create_time: int = field(default_factory=current_time)
    single_json_file: Path = None

    def __post_init__(self):
        self.json_path: Path = Path(__file__).parent.parent / "static" / "temp" / f"{self._create_time}"
        if not self.json_path.exists():
            self.json_path.mkdir(parents=True, exist_ok=True)
        self.single_json_data: List = []
        self._json_content: str = ""
        self._group = ['target_database', 'target_schema', 'target_table']

    def sheet_to_json(self, sheet) -> None:
        df = pd.read_excel(self._excel_bytes, sheet_name=sheet)
        if not df.empty:
            if not all(item in list(df.columns) for item in self._group):
                st.error(f'Sheet:{sheet} columns not match the group setting!')
                return None
        else:
            st.error(f'Sheet:{sheet} content empty!')
            return None
        if not self._extra_df.empty:
            def insert_extra_df(group):
                _extra_df_deep = self._extra_df.copy(deep=True)
                group_columns = group.columns
                extra_columns = _extra_df_deep.columns
                for col in group_columns.difference(extra_columns):
                    _extra_df_deep[col] = group[col].iloc[-1]
                result = pd.concat([group, _extra_df_deep], ignore_index=True)
                return result

            df = df.groupby(self._group).apply(insert_extra_df)
        df = df.reset_index(drop=True)
        if 'id' in df.columns:
            df = df.drop('id', axis=1)
        if 'column_sequence' in df.columns:
            df = df.drop('column_sequence', axis=1)

        df[self._group[0]] = df[self._group[0]].astype(str)
        df[self._group[1]] = df[self._group[1]].astype(str)
        df[self._group[2]] = df[self._group[2]].astype(str)
        # 初始化一个空的DataFrame用于存储处理后的分组
        updated_groups = []
        for (database, schema, table), group_df in df.groupby(self._group):
            # 使用正则表达式筛选出匹配的行
            pattern = re.compile(r"derive_col_\d+")  # 定义正则表达式
            matches = group_df['source_column_name'].apply(lambda x: bool(pattern.match(x)))
            # 找到匹配的行索引
            matching_indices = matches[matches].index
            # 如果有匹配的行，则移动到末尾
            if not matching_indices.empty:
                # 匹配的行
                matches = group_df.loc[matching_indices]
                # 非匹配的行
                non_matches = group_df.drop(index=matching_indices)
                # 重新组合DataFrame，将匹配的行置于末尾
                reordered_group = pd.concat([non_matches, matches])
            else:
                # 如果没有匹配的行，直接使用原分组数据
                reordered_group = group_df
            # 将处理后的分组添加到列表中
            updated_groups.append(reordered_group)
        # 合并所有处理后的分组
        df = pd.concat(updated_groups, ignore_index=True)
        df['id'] = df[self._group[0]].str.cat([df[self._group[1]], df[self._group[2]]], sep='-')
        df['column_sequence'] = df.groupby(self._group).cumcount() + 1
        df['column_sequence'] = df['column_sequence'].astype(str)
        df = df.fillna("None")
        if self._name_group:
            for name, group in df.groupby(self._name_group):
                if self._hierarchical_namespace:
                    json_name = '/'.join(name) + '.json'
                else:
                    json_name = '.'.join(name) + '.json'
                json_file = self.json_path / json_name
                if not json_file.parent.exists():
                    json_file.parent.mkdir(parents=True, exist_ok=True)
                json_data = group.to_json(orient='records')
                with open(json_file, 'a') as f:
                    f.write(json_data)
        else:
            self.single_json_data += json.loads(df.to_json(orient='records'))

    def convert_all_sheets(self) -> None:
        sheet_names = pd.ExcelFile(self._excel_bytes).sheet_names
        for sheet in sheet_names:
            json_name = Path(f"{sheet}.json")
            self.sheet_to_json(sheet)
        if not self._name_group:
            json_file = self.json_path / f"{self._create_time}.json"
            with open(json_file, 'a') as f:
                f.write(json.dumps(self.single_json_data, ensure_ascii=False))
            self.single_json_file = json_file

    def compress_folder(self):
        try:
            shutil.make_archive(self.json_path.parent / self.json_path.name, 'zip', self.json_path)
            shutil.rmtree(self.json_path)
            return self.json_path.parent / f"{self.json_path.name}.zip"
        except:
            return None


if '__main__' == __name__:
    jm = JsonMapper(Path("../static/test_table.xlsx"), None)
    jm.convert_all_sheets()
    a = jm.compress_folder()
    print(a)
