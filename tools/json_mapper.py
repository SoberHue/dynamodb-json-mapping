import pandas as pd
from dataclasses import dataclass, field
from pathlib import Path
import datetime
import streamlit as st
import io
import shutil
from typing import List


def current_time():
    return int(datetime.datetime.now().timestamp() * 1000)


@dataclass
class JsonMapper:
    _excel_bytes: io.BytesIO
    _extra_df: pd.DataFrame
    _start_id: int
    _group = ['target_database', 'target_schema', 'target_table']
    _name_group: List = None
    _hierarchical_namespace: bool = False
    _create_time: int = field(default_factory=current_time)

    def __post_init__(self):
        self.json_path: Path = Path(__file__).parent.parent / "static" / "temp" / f"{self._create_time}"
        if not self.json_path.exists():
            self.json_path.mkdir(parents=True, exist_ok=True)

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
        id_column = pd.Series(range(self._start_id, self._start_id + len(df))).astype(str)
        df.insert(0, 'id', id_column)
        self._start_id = df['id'].iloc[-1] + 1
        df['column_sequence'] = df.groupby(self._group).cumcount() + 1
        df['column_sequence'] = df['column_sequence'].astype(str)
        df = df.fillna("None")
        if self._name_group:
            for name, group in df.groupby(self._name_group):
                if self._hierarchical_namespace:
                    json_name = '/'.join(name) + '.json'
                else:
                    json_name = '-'.join(name) + '.json'
                json_file = self.json_path / json_name
                if not json_file.parent.exists():
                    json_file.parent.mkdir(parents=True, exist_ok=True)
                json_data = group.to_json(orient='records')
                with open(json_file, 'a') as f:
                    f.write(json_data)
        else:
            json_file = self.json_path / f"{self._create_time}.json"
            json_data = df.to_json(orient='records')
            with open(json_file, 'a') as f:
                f.write(json_data)

    def convert_all_sheets(self) -> None:
        sheet_names = pd.ExcelFile(self._excel_bytes).sheet_names
        for sheet in sheet_names:
            json_name = Path(f"{sheet}.json")
            self.sheet_to_json(sheet)

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
