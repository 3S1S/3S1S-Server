from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),

    # 회원
    path('signup', views.SignUp.as_view()),
    path('signin', views.SignIn.as_view()),
    path('checkid', views.CheckID.as_view()),
    path('users/search', views.UserSearch.as_view()),
    path('users/findid', views.FindID.as_view()),
    path('users/changepw', views.ChangePassword.as_view()),
    path('mypage/<str:id>', views.Mypage.as_view()),
    # 프로젝트
    path('projects', views.ProjectList.as_view()),
    path('projects/<int:id>', views.ProjectDetail.as_view()),
    path('projects/<int:id>/indeadline',
         views.ProjectDetailInDeadline.as_view()),
    path('projects/<int:id>/mytodos', views.ProjectDetailMyTodo.as_view()),
    path('projects/<int:id>/<str:item>', views.ProjectItem.as_view()),

    # 멤버
    path('members', views.MemberList.as_view()),
    path('members/delete', views.DeleteMember.as_view()),
    path('members/validcheck', views.CheckMember.as_view()),

    # 알림
    path('notifications', views.NotificationList.as_view()),
    path('notifications/response', views.NotificationResponse.as_view()),

    # ToDo
    path('todos', views.ToDoList.as_view()),
    path('todos/<int:id>', views.ToDoDetail.as_view()),
    path('todos/change', views.ToDoStateChange.as_view()),

    # comment
    path('comments', views.CommentList.as_view()),
    path('comments/<int:id>', views.CommentDetail.as_view()),


    # 일정
    path('schedules', views.ScheduleList.as_view()),
    path('schedules/<int:id>', views.ScheduleDetail.as_view()),

    # 파일
    path('files', views.FileList.as_view()),
    path('files/<int:id>', views.FileDetail.as_view())

]
