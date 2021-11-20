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
    path('projects/<int:id>',views.ProjectDetail.as_view()),
    path('projects/<int:id>/indeadline',views.ProjectDetailInDeadline.as_view()),
    path('projects/<int:id>/mytodos',views.ProjectDetailMyTodo.as_view()),
    
    # 멤버
    path('members',views.MemberList.as_view()),
    path('delete_members',views.DeleteMember.as_view()),

    # 알림
    path('notifications',views.NotificationList.as_view()),
    path('notifications/response',views.NotificationResponse.as_view()),

    # ToDo
    path('todos',views.ToDoList.as_view()),
    path('todos/change',views.ToDo_state_change.as_view())

]
