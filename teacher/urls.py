from django.urls import path
from teacher import views

urlpatterns = [
    path('dashboard', views.dashboard_view, name='teacher-dashboard'),
    path('add-exam', views.add_exam_view, name='teacher-add-exam'),
    path('questions/<str:exam_id>/', views.questions_view, name='teacher-questions'),
    path('add-question/<str:exam_id>', views.add_question_view, name='teacher-add-question'),
    path('edit-question/<str:question_id>', views.edit_question_view, name='teacher-edit-question'),
    path('delete-question/<str:question_id>', views.delete_question_view, name='teacher-delete-question'),
    path('delete-exam/<str:exam_id>', views.delete_exam_view, name='teacher-delete-exam'),
    path('exam-results/<str:exam_id>', views.exam_results_view, name='teacher-exam-results'),
]
