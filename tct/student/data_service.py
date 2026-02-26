from abc import ABC

from django.db import transaction
from rest_framework.exceptions import ValidationError

from tct.student.models import Student
import pandas as pd
from django.core.validators import validate_email
from django.core.exceptions import ValidationError as DjangoValidationError


class AbstractStudentService(ABC):

    def read_file(self, file):
        raise NotImplementedError

    def validate_columns(self, df):
        raise NotImplementedError

    def clean_dataframe(self, df):
        raise NotImplementedError

    def import_students(self, file):
        raise NotImplementedError


class StudentDataService(AbstractStudentService):

    REQUIRED_COLUMNS = ["student", "email"]

    def read_file(self, file):
        if file.name.endswith(".csv"):
            return pd.read_csv(file)

        if file.name.endswith(".xlsx"):
            return pd.read_excel(file)
        raise ValidationError("Only CSV or XLSX files are supported")

    def validate_columns(self, df):
        missing = set(self.REQUIRED_COLUMNS) - set(df.columns)
        if missing:
            raise ValidationError(
                f"Missing columns: {list(missing)}"
            )

    def clean_dataframe(self, df):
        df = df.dropna(how="all")

        df["student"] = df["student"].astype(str).str.strip()
        df["email"] = df["email"].astype(str).str.strip().str.lower()
        return df

    def import_students(self, file):
        df = self.read_file(file)
        self.validate_columns(df)
        df = self.clean_dataframe(df)

        report = {
            "total_rows": len(df),
            "created": 0,
            "failed": 0,
            "duplicated_in_db": 0,
            "duplicated_in_file": 0,
            "invalid_emails": 0,
            "errors": []
        }
        duplicate_emails = df[df.duplicated("email")]["email"].tolist()

        existing_emails = set(
            Student.objects.values_list("email", flat=True)
        )
        students_to_create = []

        for index, row in df.iterrows():
            row_number = index + 1
            if row["email"] in duplicate_emails:
                report["duplicated_in_file"] += 1
                report["failed"] += 1
                report["errors"].append({
                    "row": row_number,
                    "error": "Duplicated email in file"
                })
                continue
            if row["email"] in existing_emails:
                report["duplicated_in_file"] += 1
                report["failed"] += 1
                report["errors"].append({
                    "row": row_number,
                    "error": "student already exists in database"
                })
                continue
            try:
                validate_email(row["email"])
            except DjangoValidationError:
                report["invalid_emails"] += 1
                report["failed"] += 1
                report["errors"].append({
                    "row": row_number,
                    "error": "Email is not valid!!"
                })
            students_to_create.append(
                Student(
                    student=row["student"],
                    email=row["email"]
                )
            )
        with transaction.atomic():
            created = Student.objects.bulk_create(
                students_to_create,
                batch_size=100
            )
        report["created"] = len(created)
        return report

