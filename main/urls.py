from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    
    # 회원
    path('signup',views.SignUp.as_view()),
    path('signin',views.SignIn.as_view()),

    # 프로젝트
    path('project',views.ProjectList.as_view()),
    
    # 멤버
    path('member',views.MemberList.as_view()),


    
]