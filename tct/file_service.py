from abc import ABC
import pandas as pd
from rest_framework.exceptions import ValidationError


class AbstractFileService(ABC):

    def read_file(self, file):
        raise NotImplementedError

    def validate_columns(self, df, prefix):
        raise NotImplementedError

    def clean_dataframe(self, df):
        pass


class FileService(AbstractFileService):

    REQUIRED_COLUMNS = {
            "course": [
                "name",
                "teacher_id",
                "starting_date",
                "ending_date",
                "students",
            ],

            "teacher": [
                "teacher",
                "email"
            ],

            "student": [
                "student",
                "email"
            ],
         }

    def read_file(self, file):
        if file.name.endswith(".csv"):
            return pd.read_csv(file)

        if file.name.endswith(".xlsx"):
            return pd.read_excel(file)
        raise ValidationError("Only CSV or XLSX files are supported")

    def validate_columns(self, df, prefix):
        missing = set(self.REQUIRED_COLUMNS[prefix]) - set(df.columns)
        if missing:
            raise ValidationError(
                f"Missing columns: {list(missing)}"
            )
