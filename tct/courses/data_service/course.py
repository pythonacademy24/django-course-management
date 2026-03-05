import csv
import io
from abc import ABC

from django.db import transaction
from rest_framework.exceptions import ValidationError

from tct.courses.models.course import Course
from tct.file_service import FileService
from tct.student.models import Student
from tct.teacher.models import Teacher
import pandas as pd
from datetime import date

class AbstractCourseService(ABC):

    def create_course(self, params: dict):
        raise NotImplementedError

    def preview_data(self, file):
        raise NotImplementedError

    def import_courses(self, file):
        raise NotImplementedError

    def attach_students_bulk(self, courses, mapping):
        raise NotImplementedError

    def generate_error_file(self, errors):
        raise NotImplementedError

    @staticmethod
    def get_course_progress(course_id):
        raise NotImplementedError

    @staticmethod
    def change_status(course_id, status):
        raise NotImplementedError


class CourseService(AbstractCourseService, FileService):

    def create_course(self, params: dict):
        try:
            Teacher.objects.get(id=params.get("teacher_id"))
        except Exception:
            raise ValidationError("Teacher not found!")

        return Course.objects.create(**params)

    def clean_dataframe(self, df):
        df["starting_date"] = pd.to_datetime(df["starting_date"])
        df["ending_date"] = pd.to_datetime(df["ending_date"])

        df["teacher_id"] = df["teacher_id"].astype(int)

        df["students"] = df["students"].apply(
            lambda x: [int(i) for i in str(x).split("|") if i]
        )
        return df

    def preview_data(self, file):
        df = self.read_file(file)
        self.validate_columns(df, "course")
        df = self.clean_dataframe(df)
        return {
            "rows_detected": len(df),
            "preview": df.head(10).to_dict(orient="records")
        }

    def import_courses(self, file):
        df = self.read_file(file)
        self.validate_columns(df, "course")
        df = self.clean_dataframe(df)

        df = df.dropna(how="all")
        df = df.drop(columns=["id"], errors="ignore")

        report = {
            "total_rows": len(df),
            "created": 0,
            "failed": 0,
            "duplicated_in_db": 0,
            "duplicated_in_file": 0,
            "invalid_teachers": 0,
            "invalid_students": 0,
            "date_errors": 0,
            "errors": []
        }

        duplicate_names = df[df.duplicated("name")]["name"].tolist()

        existing_courses = set(
            Course.objects.values_list("name", flat=True)
        )

        teachers = Teacher.objects.in_bulk(
            df["teacher_id"].unique().tolist()
        )

        courses_to_create = []
        student_mapping = {}

        for index, row in df.iterrows():
            row_number = index + 1

            if row["name"] in duplicate_names:
                report["duplicated_in_file"] += 1
                report["failed"] += 1
                report["errors"].append({
                    "row": row_number,
                    "error": "Duplicate course inside file"
                })
                continue

            if row["name"] in existing_courses:
                report["duplicated_in_db"] += 1
                report["failed"] += 1
                report["errors"].append({
                    "row": row_number,
                    "error": "Course already exists"
                })
                continue

            teacher = teachers.get(row["teacher_id"])
            if not teacher:
                report["invalid_teachers"] += 1
                report["failed"] += 1
                report["errors"].append({
                    "row": row_number,
                    "error": "Teacher not found"
                })
                continue

            if row["ending_date"] <= row["starting_date"]:
                report["date_errors"] += 1
                report["failed"] += 1
                report["errors"].append({
                    "row": row_number,
                    "error": "Invalid date range"
                })
                continue

            course = Course(
                name=row["name"],
                teacher=teacher,
                starting_date=row["starting_date"],
                ending_date=row["ending_date"],
                number_of_students=0
            )

            courses_to_create.append(course)
            student_mapping[len(courses_to_create) - 1] = row["students"]

        # IMPORTANT: bulk_create outside the loop
        with transaction.atomic():
            created_courses = Course.objects.bulk_create(
                courses_to_create,
                batch_size=500
            )

            invalid_students = self.attach_students_bulk(
                created_courses,
                student_mapping
            )

        report["created"] = len(created_courses)
        report["invalid_students"] = invalid_students
        report["failed"] += invalid_students

        return report

    def attach_students_bulk(self, courses, mapping):
        all_student_ids = set()
        for ids in mapping.values():
            all_student_ids.update(ids)

        students = Student.objects.in_bulk(all_student_ids)

        invalid_students = 0
        for index, course in enumerate(courses):
            student_ids = mapping[index]
            valid_students = []
            for std_id in student_ids:
                if std_id in students:
                    valid_students.append(std_id)
                else:
                    invalid_students += 1

            course.student.add(*valid_students)
            course.number_of_students = len(valid_students)
            course.save(update_fields=["number_of_students"])
        return invalid_students

    def generate_error_file(self, errors):
        buffer = io.StringIO()
        writer = csv.DictWriter(
            buffer,
            fieldnames=[
                "row",
                "error"
            ]
        )
        for error in errors:
            writer.writerow(error)
        buffer.seek(0)
        return buffer

    @staticmethod
    def get_course_progress(course_id):
        course = Course.objects.get(id=course_id)
        if not course:
            raise ValidationError("Course does not exist!!")

        today = date.today()
        total_days = (course.ending_date - course.starting_date).days
        passed_days = (today - course.starting_date).days
        if total_days <= 0:
            return 0
        progress = (passed_days / total_days) * 100
        progress = max(0, min(progress, 100))
        return round(progress, 2)

    @staticmethod
    def change_status(course_id, status):
        course = Course.objects.get(id=course_id)
        if not course:
            raise ValidationError("Course does not exist!!")
        course.status = status
        course.save()
        return course

