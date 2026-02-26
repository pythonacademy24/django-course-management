from django.urls import path
from tct.courses.views import (
   CourseListView, CourseCreateView,
   CourseListFilteredView, CourseUpdateDeleteView, CourseEnrollView, CourseUnrollView, CourseBulkImportView
)

from tct.teacher.views import (
   TeacherListView, TeacherListFilteredView, TeacherCreateView, TeacherUpdateDeleteView, TeacherBulkCreateView
)

from tct.student.views import (
   StudentListView, StudentListFilteredView, StudentCreateView, StudentUpdateDeleteView, StudentBulkCreateView
)



urlpatterns = [
   # course views
   path("course/<int:pk>", CourseListView.as_view(), name='course-list'),
   path("filter-course/", CourseListFilteredView.as_view(), name='course-list-filtered'),
   path("course-create", CourseCreateView.as_view(), name='course-create'),
   path("course-detail/<int:pk>", CourseUpdateDeleteView.as_view(), name='course-detail'),
   path("course/<int:pk>/enroll", CourseEnrollView.as_view(), name='enroll-student'),
   path("course/<int:pk>/unroll", CourseUnrollView.as_view(), name='unroll-student'),
   path("course-create-bulk", CourseBulkImportView.as_view(), name='course-create-bulk'),

   # teacher views
   path("teacher/<int:pk>", TeacherListView.as_view(), name='teacher-list'),
   path("filter-teacher/", TeacherListFilteredView.as_view(), name='teacher-list-filtered'),
   path("teacher-create", TeacherCreateView.as_view(), name='teacher-create'),
   path("teacher-detail/<int:pk>", TeacherUpdateDeleteView.as_view(), name='teacher-detail'),
   path("teacher-create-bulk", TeacherBulkCreateView.as_view(), name='teacher-create-bulk'),

   # student views
   path("student/<int:pk>", StudentListView.as_view(), name='student-list'),
   path("filter-student/", StudentListFilteredView.as_view(), name='student-list-filtered'),
   path("student-create", StudentCreateView.as_view(), name='student-create'),
   path("student-detail/<int:pk>", StudentUpdateDeleteView.as_view(), name='student-detail'),
   path("student-create-bulk", StudentBulkCreateView.as_view(), name='student-create-bulk'),

]
