from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    
    # 회원
    path('signup',views.SignUp.as_view()),
    path('signin',views.SignIn.as_view()),
    path('checkid',views.CheckID.as_view()),   

    # 프로젝트
    path('projects',views.ProjectList.as_view()),
    
    # 멤버
    path('members',views.MemberList.as_view()),

    # 알림
    path('notifications',views.NotificationList.as_view()),

    # ToDo
    path('todos',views.ToDoList.as_view())
]