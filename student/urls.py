from django.urls import path
from student import views

urlpatterns = [
    path('dashboard', views.dashboard_view, name='student-dashboard'),
    path('exams', views.exams_view, name='student-exams'),
    path('start/<str:exam_id>', views.start_exam_view, name='student-start-exam'),
    path('quiz/<str:exam_id>', views.quiz_view, name='student-quiz'),
    path('result/<str:exam_id>', views.result_view, name='student-result'),
    path('my-results', views.my_results_view, name='student-my-results'),
]
