from abc import ABC

from django.db import transaction

from tct.file_service import FileService
from tct.teacher.models import Teacher
import pandas as pd
from django.core.validators import validate_email
from django.core.exceptions import ValidationError as DjangoValidationError


class AbstractTeacherService(ABC):

    def import_teachers(self, file):
        raise NotImplementedError


class TeacherDataService(AbstractTeacherService, FileService):

    def clean_dataframe(self, df):
        df = df.dropna(how="all")

        df["teacher"] = df["teacher"].astype(str).str.strip()
        df["email"] = df["email"].astype(str).str.strip().str.lower()
        return df

    def import_teachers(self, file):

        df = self.read_file(file)
        self.validate_columns(df, "teacher")
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
            Teacher.objects.values_list("email", flat=True)
        )
        teachers_to_create = []

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
                    "error": "Teacher already exists in database"
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
            teachers_to_create.append(
                Teacher(
                    teacher=row["teacher"],
                    email=row["email"]
                )
            )
        with transaction.atomic():
            created = Teacher.objects.bulk_create(
                teachers_to_create,
                batch_size=100
            )
        report["created"] = len(created)
        return report

