from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('register/', views.register_view, name='register'),

    path('courses/', views.CourseListView.as_view(), name='courses'),
    path('course/<int:pk>', views.CourseDetailView.as_view(), name='course-detail'),

    path('professors/', views.ProfesorListView.as_view(), name='professors'),
    path('professors/<int:pk>', views.ProfesorDetailView.as_view(), name='professor-detail'),

    path('students/', views.StudentListView.as_view(), name='students'),
    path('student/<int:pk>', views.StudentDetailView.as_view(), name='student-detail'),

    path('management/create/', views.profesor_create_view, name='profesor-create'),
    path('management/my-classes/', views.profesor_classes_view, name='profesor-classes'),

    path('management/enroll/<int:pk>/', views.enroll_class_view, name='enroll-class'),
    path('management/enroll/', views.student_enroll_view, name='student-enroll'),
    path('management/student-my-classes/', views.student_classes_view, name='student-classes'),
    path('management/unenroll-class/<int:pk>/',views.unenroll_class_view,name='unenroll-class'),
]