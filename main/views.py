from django.db import connection
from django.forms.models import model_to_dict
from django.http.response import JsonResponse
from django.http import HttpResponse
from django.utils.functional import empty
from django.views.decorators.csrf import csrf_exempt
from django.views import View
from django.core.mail import EmailMessage

from rest_framework import generics

import json
import bcrypt
import re
import datetime
import jwt
import ast
import string
import secrets
import parse

from main.models import Participant, Project, Schedule, Todo, User, Member, Notification, Comment, File
from config import SECRET_KEY

# 회원
# 회원가입


class SignUp(View):
    def post(self, request):
        data = json.loads(request.body)

        try:
            # 필수항목 미입력
            for key, val in data.items():
                if val == "" and key not in ['checked_id', 'belong']:
                    return JsonResponse({'message': '필수 항목을 모두 입력하세요.'}, status=210)

            # ID 중복
            if data['id'] != data['checked_id']:
                return JsonResponse({'message': 'ID 중복 확인을 수행하세요.'}, status=210)

            # 비밀번호 재입력 불일치
            elif data['password'] != data['password_check']:
                return JsonResponse({'message': '비밀번호가 일치하지 않습니다.'}, status=210)

            # 이메일 중복
            elif User.objects.filter(email=data['email']).exists():
                return JsonResponse({'message': '동일한 이메일로 가입한 회원이 존재합니다.'}, status=210)

            else:  # 이메일 형식 오류
                regex = re.compile(r"[a-zA-Z0-9_]+@[a-z]+[.][a-z.]+")
                mo = regex.search(data['email'])
                if mo == None:
                    return JsonResponse({'message': '이메일 형식이 옳지 않습니다.'}, status=210)

            User.objects.create(
                id=data['id'],
                password=bcrypt.hashpw(data['password'].encode(
                    "UTF-8"), bcrypt.gensalt()).decode("UTF-8"),
                name=data['name'],
                email=data['email'],
                belong=data['belong'],
                img_url='/img/blank-person.png'
            ).save()

            return JsonResponse({'message': '회원가입 성공'}, status=201)

        except json.JSONDecodeError as e:
            return JsonResponse({'message': f'Json_ERROR:{e}'}, status=500)
        except KeyError:
            return JsonResponse({'message': 'Invalid Value'}, status=500)

# 로그인


class SignIn(View):
    @csrf_exempt
    def post(self, request):
        data = json.loads(request.body)

        try:
            if data['id'] == "" or data['password'] == "":
                return JsonResponse({"message": "Please fill in the required items."}, status=210)

            if User.objects.filter(id=data['id']).exists():
                user = User.objects.get(id=data['id'])

                if bcrypt.checkpw(data['password'].encode('UTF-8'), user.password.encode('UTF-8')):
                    id = user.id
                    name = user.name
                    return JsonResponse({'id': id, 'name': name}, status=200)

                return JsonResponse({"message": "Wrong Password"}, status=210)

            return JsonResponse({"message": "Unexist ID"}, status=210)

        except json.JSONDecodeError as e:
            return JsonResponse({'message': f'Json_ERROR:{e}'}, status=500)
        except KeyError:
            return JsonResponse({'message': 'Invalid Value'}, status=500)

# ID 중복 확인


class CheckID(View):
    def get(self, request):
        id = request.GET.get('id', None)
        try:
            # 항목 미입력
            if id == "":
                return JsonResponse({'message': 'ID를 입력하세요.', 'checked_id': ""}, status=210)

            # ID 중복
            if User.objects.filter(id=id).exists():
                return JsonResponse({'message': '동일한 ID가 존재합니다.', 'checked_id': ""}, status=210)
            else:
                return JsonResponse({'message': '생성 가능한 ID입니다.', 'checked_id': id}, status=200)

        except json.JSONDecodeError as e:
            return JsonResponse({'message': f'Json_ERROR:{e}'}, status=500)
        except KeyError:
            return JsonResponse({'message': 'Invalid Value'}, status=500)


class UserSearch(View):
    def get(self, request):
        user = request.GET.get('user', '')
        try:
            # 검색한 유저가 없을 경우
            if user == '':
                return JsonResponse({'search_list': []}, status=210)
            else:   # 유저 검색 결과
                users = list(User.objects.filter(
                    id__contains=user).values('id', 'name').order_by('id'))
                return JsonResponse({'search_list': users[:5]}, status=200)
        except json.JSONDecodeError as e:
            return JsonResponse({'message': f'Json_ERROR:{e}'}, status=500)
        except KeyError:
            return JsonResponse({'message': 'Invalid Value'}, status=500)


class Mypage(View):
    def get(self, request, id):
        try:
            userInformation = list(User.objects.filter(id=id).values(
                'id', 'name', 'email', 'belong', 'img_url'))[0]

            # status 200
            return JsonResponse({'information': userInformation})

        except json.JSONDecodeError as e:
            return JsonResponse({'message': f'Json_ERROR:{e}'}, status=500)

    def put(self, request, id):
        try:
            data = json.loads(request.body)
            userInformation = User.objects.get(id=id)

            userInformation.email = data['email']
            userInformation.belong = data['belong']
            userInformation.img_url = data['img_url']
            userInformation.save()

            return JsonResponse({'message': '유저 정보 수정 성공'}, status=200)

        except json.JSONDecodeError as e:
            return JsonResponse({'message': f'Json_ERROR:{e}'}, status=500)
        except KeyError:
            return JsonResponse({'message': 'Invalid Value'}, status=500)


class FindID(View):
    def get(self, request):
        try:
            name, email = request.GET.get(
                'name', None), request.GET.get('email', None)

            if name == "" or email == "":
                return JsonResponse({'message': '입력하지 않은 필드가 존재합니다.'}, status=210)

            elif User.objects.filter(name=name, email=email).exists():
                id = User.objects.get(name=name, email=email).id
                id = id[:-5] + '*****'

                return JsonResponse({'id': id}, status=200)
            else:
                return JsonResponse({'message': '해당 사용자 정보가 존재하지 않습니다.'}, status=210)
        except json.JSONDecodeError as e:
            return JsonResponse({'message': f'Json_ERROR:{e}'}, status=500)
        except KeyError:
            return JsonResponse({'message': 'Invalid Value'}, status=500)


class ChangePassword(View):
    def get(self, request):
        try:
            id, name, email = request.GET.get('id', None), request.GET.get(
                'name', None), request.GET.get('email', None)

            if id == "" or name == "" or email == "":
                return JsonResponse({'message': '입력하지 않은 필드가 존재합니다.'}, status=210)

            if User.objects.filter(id=id, name=name, email=email).exists():
                user = User.objects.get(id=id, name=name, email=email)

                subject = '[SSIS 비밀번호 찾기] ' + \
                    user.name + ' 회원님의 임시 비밀번호입니다.'
                string_pool = string.ascii_letters + string.digits
                while True:
                    temp_password = ''.join(secrets.choice(
                        string_pool) for i in range(10))
                    if (any(c.islower() for c in temp_password)
                        and any(c.isupper() for c in temp_password)
                            and sum(c.isdigit() for c in temp_password) >= 3):
                        break
                message = '요청하신 임시 비밀번호입니다.\n임시 비밀번호 : ' + \
                    str(temp_password) + \
                    '\n\n해당 비밀번호로 로그인한 후 비밀번호 변경 후 사용하시길 바랍니다.'
                mail = EmailMessage(subject, message, to=[user.email])
                mail.send()

                user.password = bcrypt.hashpw(temp_password.encode(
                    "UTF-8"), bcrypt.gensalt()).decode("UTF-8")
                user.save()

                return JsonResponse({'message': '입력하신 이메일(' + user.email + ')로\n임시 비밀번호가 발급되었습니다.'}, status=200)

            else:
                return JsonResponse({'message': '해당 사용자 정보가 존재하지 않습니다.'}, status=210)

        except json.JSONDecodeError as e:
            return JsonResponse({'message': f'Json_ERROR:{e}'}, status=500)
        except KeyError:
            return JsonResponse({'message': 'Invalid Value'}, status=500)

    def put(self, request):
        try:
            data = json.loads(request.body)

            # 필수항목 미입력
            for key, val in data.items():
                if val == "":
                    return JsonResponse({'message': '입력하지 않은 필드가 존재합니다.'}, status=210)

            # 비밀번호 재입력 불일치
            if data['password_change'] != data['password_check']:
                return JsonResponse({'message': '변경할 비밀번호가 일치하지 않습니다.'}, status=210)

            user = User.objects.get(id=data['id'])
            # 기존 비밀번호 불일치
            if not bcrypt.checkpw(data['password'].encode('UTF-8'), user.password.encode('UTF-8')):
                return JsonResponse({'message': '기존의 비밀번호가 일치하지 않습니다.'}, status=210)

            else:
                user.password = bcrypt.hashpw(data["password_change"].encode("UTF-8"),
                                              bcrypt.gensalt()).decode("UTF-8")
                user.save()

            return JsonResponse({'message': '비밀번호 변경 성공'}, status=200)

        except json.JSONDecodeError as e:
            return JsonResponse({'message': f'Json_ERROR:{e}'}, status=500)
        except KeyError:
            return JsonResponse({'message': 'Invalid Value'}, status=500)

# 프로젝트
# 프로젝트 생성, 목록


class ProjectList(View):
    def get(self, request):
        try:
            id = request.GET.get('id', None)
            project_list = list(Member.objects.filter(
                user_id=id).values('project_id'))

            result = ""
            for project in project_list:
                if result != "":
                    result |= Project.objects.filter(id=project['project_id'])
                else:
                    result = Project.objects.filter(id=project['project_id'])

            return JsonResponse({'project_list': list(result.values()) if result != "" else []}, status=200)

        except json.JSONDecodeError as e:
            return JsonResponse({'message': f'Json_ERROR:{e}'}, status=500)
        except KeyError:
            return JsonResponse({'message': 'Invalid Value'}, status=500)

    def post(self, request):
        data = json.loads(request.body)

        try:
            # 필수항목 미입력
            for key, val in data.items():
                if val == "" and key in ['title', 'team', 'description']:
                    return JsonResponse({'message': '필수 항목을 모두 입력하세요.'}, status=210)

            created_project = Project.objects.create(
                title=data['title'],
                team=data['team'],
                description=data['description'],
                subject=data['subject'],
                purpose=data['purpose'],
                progress_rate=0.0,
                img_url=data["img_url"],
                memo=""
            )
            created_project.save()

            Member.objects.create(
                project=created_project,
                user=User.objects.get(id=data['creator']),
                leader=1,
                contribution_rate=0.0
            ).save()

            return JsonResponse({'message': '프로젝트 생성 성공'}, status=201)

        except json.JSONDecodeError as e:
            return JsonResponse({'message': f'Json_ERROR:{e}'}, status=500)
        except KeyError:
            return JsonResponse({'message': 'Invalid Value'}, status=500)


class ProjectDetail(View):
    def get(self, request, id):
        try:
            item = list(Project.objects.filter(id=id).values())[0]

            if not Member.objects.filter(project=id, leader=1).exists():
                return JsonResponse({'message': '올바르지 않은 프로젝트 id에 대한 접근입니다.'}, status=400)
            else:
                item['leader'] = list(Member.objects.filter(
                    project=id, leader=1).values('user'))[0]['user']

            return JsonResponse({'project_content': item}, status=201)

        except json.JSONDecodeError as e:
            return JsonResponse({'message': f'Json_ERROR:{e}'}, status=500)
        except KeyError:
            return JsonResponse({'message': 'Invalid Value'}, status=500)

    def put(self, request, id):
        try:
            data = json.loads(request.body)

            for key, val in data.items():
                if val == "" and key in ['title', 'team', 'description']:
                    return JsonResponse({'message': '필수 항목을 모두 입력하세요.'}, status=210)

            project = Project.objects.get(id=id)
            if 'memo' not in data.keys():
                project.title = data['title']
                project.team = data['team']
                project.description = data['description']
                project.subject = data['subject']
                project.purpose = data['purpose']
                project.img_url = data["img_url"]
            else:
                project.memo = data["memo"]
            project.save()

            return JsonResponse({'message': '프로젝트 정보 수정 성공'}, status=200)

        except json.JSONDecodeError as e:
            return JsonResponse({'message': f'Json_ERROR:{e}'}, status=500)
        except KeyError:
            return JsonResponse({'message': 'Invalid Value'}, status=500)

    def delete(self, request, id):
        try:
            Project.objects.get(id=id).delete()

            return JsonResponse({'message': '프로젝트 삭제 성공'}, status=200)

        except json.JSONDecodeError as e:
            return JsonResponse({'message': f'Json_ERROR:{e}'}, status=500)
        except KeyError:
            return JsonResponse({'message': 'Invalid Value'}, status=500)


class ProjectItem(View):
    def get(self, request, id, item):
        try:
            if item != 'leader':
                item = list(Project.objects.filter(
                    id=id).values(item))[0][item]
            else:
                item = list(Member.objects.filter(
                    project=id, leader=1).values('user'))[0]['user']

            return JsonResponse({'item': item}, status=201)

        except json.JSONDecodeError as e:
            return JsonResponse({'message': f'Json_ERROR:{e}'}, status=500)
        except KeyError:
            return JsonResponse({'message': 'Invalid Value'}, status=500)


class ProjectDetailInDeadline(View):
    def get(self, request, id):
        try:
            todos = list(Todo.objects.filter(project=id).exclude(
                state=2).values('id', 'title', 'state', 'end_date'))

            inDeadline = []
            for todo in todos:
                d_day = abs((datetime.date.today() - todo['end_date']).days)
                if d_day <= 3:
                    d_day = " - " + (str(d_day) if d_day != 0 else 'Day')
                    todo['d_day'] = "D" + d_day
                    inDeadline.append(todo)

            return JsonResponse({'todo_list': inDeadline}, status=200)

        except json.JSONDecodeError as e:
            return JsonResponse({'message': f'Json_ERROR:{e}'}, status=500)
        except KeyError:
            return JsonResponse({'message': 'Invalid Value'}, status=500)


class ProjectDetailMyTodo(View):
    def get(self, request, id):
        user = request.GET.get('user', None)
        try:
            todos = list(Todo.objects.filter(project=id).exclude(
                state=2).values('id', 'title', 'state', 'end_date'))

            MyTodo = []
            for todo in todos:
                if Participant.objects.filter(todo=todo['id'], user=user).values('user').exists():
                    d_day = abs(
                        (datetime.date.today() - todo['end_date']).days)
                    d_day = " - " + (str(d_day) if d_day != 0 else 'Day')
                    todo['d_day'] = "D" + d_day
                    MyTodo.append(todo)

            return JsonResponse({'todo_list': MyTodo}, status=200)

        except json.JSONDecodeError as e:
            return JsonResponse({'message': f'Json_ERROR:{e}'}, status=500)
        except KeyError:
            return JsonResponse({'message': 'Invalid Value'}, status=500)

# 멤버
# 멤버 추가, 목록


class MemberList(View):
    # get 메소드 파라미터로 입력된 프로젝트의 멤버를 모두 보여준다.
    def get(self, request):
        project_id, showName = request.GET.get(
            'project', None), request.GET.get('showname', 'false')

        try:
            members = Member.objects.filter(project=project_id).values(
                'user_id', 'leader', 'contribution_rate').order_by('-leader')
            for member in members:
                member['profile_img'] = User.objects.get(
                    id=member['user_id']).img_url
                member['name'] = User.objects.get(
                    id=member['user_id']).name
                if showName == 'true':
                    member['name'] = User.objects.get(
                        id=member['user_id']).name + '(' + member['user_id'] + ')'
            return JsonResponse({'members': list(members)}, status=200)

        except KeyError:
            return JsonResponse({"message": "Invalid Value"}, status=400)


class DeleteMember(View):
    def post(self, request):
        data = json.loads(request.body)

        try:
            user = Member.objects.get(
                project=data['project'], user=data['user'])

            if user.leader == 1:
                if Member.objects.filter(project=data['project']).count() > 1:
                    return JsonResponse({'message': '팀장은 프로젝트를 탈퇴할 수 없습니다.\n탈퇴를 원하실 경우 다른 팀원에게 팀장을 위임한 후 시도하세요.'}, status=210)

            user.delete()

            if not Member.objects.filter(project=data['project']).exists():
                ProjectDetail.delete(self, request, id=data['project'])
                return JsonResponse({'message': '프로젝트 탈퇴 후 프로젝트 삭제'}, status=200)

            return JsonResponse({'message': '프로젝트 탈퇴 성공'}, status=200)

        except json.JSONDecodeError as e:
            return JsonResponse({'message': f'Json_ERROR:{e}'}, status=500)
        except KeyError:
            return JsonResponse({'message': 'Invalid Value'}, status=500)


class CheckMember(View):
    def get(self, request):
        try:
            project, user = request.GET.get(
                'project', None), request.GET.get('user', None)
            # 이미 알림을 보냈을 경우
            if Notification.objects.filter(project=project, invitee=user).exists():
                return JsonResponse({"message": "이미 알림을 보냈습니다.", "is_valid": False}, status=210)
            # 이미 멤버로 참여 하고 있을 경우
            elif Member.objects.filter(project=project, user=user).exists():
                return JsonResponse({"message": "이미 멤버로 참여하고있습니다.", "is_valid": False}, status=210)
            else:   # 멤버로 초대 가능한 경우
                return JsonResponse({"message": "초대 가능한 유저입니다.", "is_valid": True}, status=200)

        except json.JSONDecodeError as e:
            return JsonResponse({'message': f'Json_ERROR:{e}'}, status=500)
        except KeyError:
            return JsonResponse({'message': 'Invalid Value'}, status=500)


class AuthorizeLeader(View):
    def put(self, request):
        try:
            data = json.loads(request.body)
            leader = Member.objects.get(project=data['project'], leader=1)
            leader_change = Member.objects.get(
                project=data['project'], user=data['leader'])

            leader.leader = 0
            leader_change.leader = 1
            leader.save()
            leader_change.save()

            return JsonResponse({"message": "리더 변경 성공"}, status=200)

        except json.JSONDecodeError as e:
            return JsonResponse({'message': f'Json_ERROR:{e}'}, status=500)
        except KeyError:
            return JsonResponse({'message': 'Invalid Value'}, status=500)


# 알림
# 알림 생성


class NotificationList(View):
    # get 메소드 파라미터로 입력된 invitee의 알림을 모두 보여준다.
    def get(self, request):
        invitee_id = request.GET.get('invitee', None)

        try:
            notifications = list(Notification.objects.filter(
                invitee=invitee_id).values())
            for notification in notifications:
                notification['project_title'] = Project.objects.get(
                    id=notification['project_id']).title
                notification['invitee_name'] = User.objects.get(
                    id=notification['invitee_id']).name
                notification['inviter_name'] = User.objects.get(
                    id=notification['inviter_id']).name

            return JsonResponse({'notifications': notifications}, status=200)

        except KeyError:
            return JsonResponse({"message": "Invalid Value"}, status=400)

    def post(self, request):
        try:
            data = json.loads(request.body)
            data['invite_date'] = str(datetime.datetime.now())

            for invitee in data['invitees']:
                Notification.objects.create(
                    project=Project.objects.get(id=data['project']),
                    invitee=User.objects.get(id=invitee),
                    inviter=User.objects.get(id=data['inviter']),
                    invite_date=data['invite_date']
                ).save()

            return JsonResponse({'message': '초대 알림 생성 성공'})

        except json.JSONDecodeError as e:
            return JsonResponse({'message': f'Json_ERROR:{e}'}, status=500)
        except KeyError:
            return JsonResponse({'message': 'Invalid Value'}, status=500)

# 알림 수락 / 거절


class NotificationResponse(View):
    # 알림을 수락 하였을 때 멤버 db에 추가
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body)

        try:
            # 수락 했을 때
            # 성공 status 201
            if data['accept'] == 1:

                # leader의 값은 무조건 0이 된다.
                Member.objects.create(
                    project=Project.objects.get(id=data['project']),
                    user=User.objects.get(id=data['user']),
                    leader=0,
                    contribution_rate=0
                ).save()
                message, status = '멤버 초대를 수락 하였습니다.', 201
            # 거절 했을 때
            # 거절 status 200
            else:
                message, status = '멤버 초대를 거절 하였습니다.', 200

            # 알림 삭제2
            Notification.objects.filter(
                project=data['project'], invitee=data['user']).delete()

            return JsonResponse({'message': message}, status=status)

        except json.JSONDecodeError as e:
            return JsonResponse({'message': f'Json_ERROR:{e}'}, status=500)
        except KeyError:
            return JsonResponse({'message': 'Invalid Value'}, status=500)


# ToDo
# ToDo 생성, 목록
class ToDoList(View):
    def get(self, request):
        try:
            project, state, ispast = request.GET.get('project', None), request.GET.get(
                'state', None), request.GET.get('ispast', 'true')

            if int(state) < 2:
                todos = list(Todo.objects.filter(
                    project=project, state=state).values().order_by('end_date'))

            else:
                todos = list(Todo.objects.filter(
                    project=project, state=state, end_date__gte=datetime.date.today()).values().order_by('end_date'))
                for todo in todos:
                    todo['color'] = 'white'

                if ispast == 'true':
                    past_todos = list(Todo.objects.filter(
                        project=project, state=state, end_date__lt=datetime.date.today()).values().order_by('-end_date'))
                    for past_todo in past_todos:
                        past_todo['color'] = '#e3e6e8'
                    todos += past_todos

            for todo in todos:
                todo['id'] = str(todo['id'])
                d_day = todo['d_day'] = (
                    datetime.date.today() - todo['end_date']).days
                d_day = " + " + str(d_day) if d_day > 0 else " - " + \
                    str(abs(d_day) if d_day != 0 else 'Day')
                todo['d_day'] = "D" + d_day

                participants = list(Participant.objects.filter(
                    todo=todo['id']).values('user'))
                participant_with_name = []
                for participant in participants:
                    user = dict()
                    user_obj = User.objects.get(id=participant['user'])
                    user['id'] = user_obj.id
                    user['name'] = user_obj.name
                    user['img_url'] = user_obj.img_url
                    participant_with_name.append(user)
                todo['participants'] = participant_with_name

            return JsonResponse({'todo_list': todos}, status=200)

        except json.JSONDecodeError as e:
            return JsonResponse({'message': f'Json_ERROR:{e}'}, status=500)
        except KeyError:
            return JsonResponse({'message': 'Invalid Value'}, status=500)

    def post(self, request):
        data = json.loads(request.body)

        try:
            # 필수항목 미입력
            for val in data.items():
                if val == "":
                    return JsonResponse({'message': '필수 항목을 모두 입력하세요.'}, status=210)

            # 날짜 정보 부정확
            if data['start_date'] > data['end_date']:
                return JsonResponse({'message': '설정한 기간이 올바르지 않습니다.'}, status=210)

            created_todo = Todo.objects.create(
                project=Project.objects.get(id=data['project']),
                writer=User.objects.get(id=data['writer']),
                title=data['title'],
                description=data['description'],
                state=0,
                start_date=data['start_date'],
                end_date=data['end_date']
            )
            created_todo.save()

            for participant in data['participants']:
                user = parse.parse('{name}({id})', participant)
                Participant.objects.create(
                    todo=created_todo,
                    user=User.objects.get(id=user['id'])
                ).save()

            calRate(data['project'])

            return JsonResponse({'message': 'ToDo 생성 성공'}, status=201)

        except json.JSONDecodeError as e:
            return JsonResponse({'message': f'Json_ERROR:{e}'}, status=500)
        except KeyError:
            return JsonResponse({'message': 'Invalid Value'}, status=500)


class ToDoDetail(View):
    def get(self, request, id):
        try:
            todo = Todo.objects.get(id=id)
            todo = model_to_dict(todo)

            participants = list(Participant.objects.filter(
                todo=todo['id']).values('user'))
            participant_with_name = []
            for participant in participants:
                user = dict()
                user_obj = User.objects.get(id=participant['user'])
                user['id'] = user_obj.id
                user['name'] = user_obj.name
                user['name_id'] = user_obj.name+'('+user_obj.id+')'
                user['profile_img'] = user_obj.img_url
                participant_with_name.append(user)
            todo['participants'] = participant_with_name

            return JsonResponse({'todo_content': todo})

        except json.JSONDecodeError as e:
            return JsonResponse({'message': f'Json_ERROR:{e}'}, status=500)
        except KeyError:
            return JsonResponse({'message': 'Invalid Value'}, status=500)

    def put(self, request, id):
        try:
            data = json.loads(request.body)

            # 필수항목 미입력
            for val in data.values():
                if val == "":
                    return JsonResponse({'message': '필수 항목을 모두 입력하세요.'}, status=210)

            # 날짜 정보 부정확
            if data['start_date'] > data['end_date']:
                return JsonResponse({'message': '설정한 기간이 올바르지 않습니다.'}, status=210)

            todo = Todo.objects.get(id=id)
            todo.title = data['title']
            todo.description = data['description']
            todo.start_date = data['start_date']
            todo.end_date = data['end_date']
            todo.save()

            participants_id = []
            for participant in data['participants']:
                participant = (parse.parse('{name}({id})', participant))['id']
                participants_id.append(participant)
                if not Participant.objects.filter(todo=id, user=participant).exists():
                    Participant.objects.create(
                        todo=todo,
                        user=User.objects.get(id=participant)
                    ).save()

            participants = list(
                Participant.objects.filter(todo=id).values('user'))

            for participant in participants:
                if not participant['user'] in participants_id:
                    Participant.objects.get(
                        todo=id, user=participant['user']).delete()

            return JsonResponse({'message': 'Todo 수정 성공'}, status=200)

        except json.JSONDecodeError as e:
            return JsonResponse({'message': f'Json_ERROR:{e}'}, status=500)
        except KeyError:
            return JsonResponse({'message': 'Invalid Value'}, status=500)

    def delete(self, request, id):
        try:
            project_id = Todo.objects.get(id=id).project.id
            Todo.objects.get(id=id).delete()
            calRate(project_id)
            return JsonResponse({'message': 'Todo 삭제 성공'}, status=200)

        except json.JSONDecodeError as e:
            return JsonResponse({'message': f'Json_ERROR:{e}'}, status=500)
        except KeyError:
            return JsonResponse({'message': 'Invalid Value'}, status=500)


def calRate(todo_project):

    member_list = Member.objects.filter(
        project=todo_project).values('user')
    member_list = [d['user'] for d in member_list]

    # <<기여도 계산>>
    # 이 프로젝트에서 Todo 완료한 participant id (user id X)
    total_participants = Todo.objects.filter(
        state=2, project=todo_project).values('participant')
    total_participants = [d['participant']
                          for d in total_participants]

    if len(total_participants) > 1:
        total_participants.pop()

    # 새로 기여도를 계산 하기위해 초기화하여 저장
    for z in range(len(member_list)):
        zero = Member.objects.get(
            user=member_list[z], project=todo_project)
        zero.contribution_rate = 0
        zero.save()

    # 기여도를 게산 하여 저장
    for n in range(len(member_list)):
        for m in range(len(total_participants)):
            participants_id = Participant.objects.get(
                id=total_participants[m]).user.id

            member_id = member_list[n]

            if participants_id == member_id:
                member_new_rate = Member.objects.get(
                    user=member_list[n], project=todo_project)
                member_new_rate.contribution_rate += 1.0
                member_new_rate.save()
        member_rate = Member.objects.get(
            user=member_list[n], project=todo_project)
        member_rate.contribution_rate = member_rate.contribution_rate / \
            (len(total_participants) + 0.0001)
        temp = member_rate.contribution_rate
        member_rate.contribution_rate = round(temp, 2)*100
        member_rate.save()

    # <<진행율 계산>>
    complete_todo = Todo.objects.filter(
        state=2, project=todo_project).values('id')
    complete_todo = [d['id'] for d in complete_todo]

    ing_todo = Todo.objects.filter(
        state=1, project=todo_project).values('id')
    ing_todo = [d['id'] for d in ing_todo]

    pre_todo = Todo.objects.filter(
        state=0, project=todo_project).values('id')
    pre_todo = [d['id'] for d in pre_todo]

    project_instance = Project.objects.get(id=todo_project)

    total_prog = len(complete_todo) + len(ing_todo) + len(pre_todo)
    comp_prog = len(complete_todo)

    project_instance.progress_rate = round(
        (comp_prog / total_prog), 2) * 100
    project_instance.save()
    print("1")


class ToDoStateChange(View):
    def post(self, request):
        try:
            data = json.loads(request.body)

            todo_instance = Todo.objects.get(id=data['todo'])

            todo_instance.state = data['state']
            todo_instance.save()
            todo_project = Todo.objects.get(id=data['todo']).project.id
            calRate(todo_project)

            return JsonResponse({'message': ""})

        except json.JSONDecodeError as e:
            return JsonResponse({'message': f'Json_ERROR:{e}'}, status=500)
        except KeyError:
            return JsonResponse({'message': 'Invalid Value'}, status=500)

# Todo 댓글


class CommentList(View):
    def get(self, request):
        todo_id = request.GET.get('todo', None)

        try:
            comments = list(Comment.objects.filter(todo=todo_id).values())
            for comment in comments:
                print(str(comment['create_at']))
                comment['writer_name'] = User.objects.get(
                    id=comment['writer_id']).name + '(' + comment['writer_id'] + ')'
                created_at = parse.parse(
                    '{date} {time}', str(comment['create_at']))
                comment['create_at'] = created_at['date'] + \
                    ' '+created_at['time'][:-3]

            return JsonResponse({'comments': list(comments)}, status=200)

        except KeyError:
            return JsonResponse({"message": "Invalid Value"}, status=500)

    def post(self, request):
        try:
            data = json.loads(request.body)
            data['create_at'] = str(datetime.datetime.now())

            # 필수항목 미입력
            for val in data.values():
                if val == "":
                    return JsonResponse({'message': '필수 항목을 모두 입력하세요.'}, status=210)

            Comment.objects.create(
                todo=Todo.objects.get(id=data['todo']),
                writer=User.objects.get(id=data['writer']),
                content=data['content'],
                create_at=data['create_at']
            ).save()

            return JsonResponse({'message': '댓글 생성 성공'}, status=201)
        except json.JSONDecodeError as e:
            return JsonResponse({'message': f'Json_ERROR:{e}'}, status=500)
        except KeyError:
            return JsonResponse({'message': 'Invalid Value'}, status=500)


class CommentDetail(View):
    def put(self, request, id):
        try:
            data = json.loads(request.body)
            data['create_at'] = str(datetime.datetime.now())

            # 필수항목 미입력
            for val in data.values():
                if val == "":
                    return JsonResponse({'message': '필수 항목을 모두 입력하세요.'}, status=210)

            comment = Comment.objects.get(id=id)

            comment.content = data['content']
            comment.create_at = data['create_at']
            comment.save()

            return JsonResponse({'message': '댓글 수정 성공'}, status=201)

        except json.JSONDecodeError as e:
            return JsonResponse({'message': f'Json_ERROR:{e}'}, status=500)
        except KeyError:
            return JsonResponse({'message': 'Invalid Value'}, status=500)

    def delete(self, request, id):
        try:
            Comment.objects.get(id=id).delete()

            return JsonResponse({'message': '댓글 삭제 성공'}, status=200)

        except json.JSONDecodeError as e:
            return JsonResponse({'message': f'Json_ERROR:{e}'}, status=500)
        except KeyError:
            return JsonResponse({'message': 'Invalid Value'}, status=500)


class ScheduleList(View):
    def get(self, request):
        try:
            project, type = request.GET.get(
                'project', None), request.GET.get('type', 'calendar')

            # 캘린더 타입 목록
            if type == 'calendar':
                schedules = list(Schedule.objects.filter(
                    project=project).defer('project_id', 'writer').values())
                for schedule in schedules:
                    if schedule['start_date'] != schedule['end_date']:
                        schedule['end_date'] += datetime.timedelta(days=1)

                    schedule['start'] = schedule.pop('start_date')
                    schedule['end'] = schedule.pop('end_date')
            elif type == 'list':   # 리스트 타입 목록
                schedules = list(Schedule.objects.filter(
                    project=project).values().order_by('end_date'))

                for schedule in schedules:
                    if schedule['end_date'] >= datetime.date.today():
                        schedule['is_end'] = True
                    else:
                        schedule['is_end'] = False

            return JsonResponse({'schedule_list': schedules}, status=200)

        except json.JSONDecodeError as e:
            return JsonResponse({'message': f'Json_ERROR:{e}'}, status=500)
        except KeyError:
            return JsonResponse({'message': 'Invalid Value'}, status=500)

    def post(self, request):
        try:
            data = json.loads(request.body)

            for val in data.values():
                if val == "":
                    return JsonResponse({'message': '필수 항목을 모두 입력하세요.'}, status=210)

            # 날짜 정보 부정확
            if data['start_date'] > data['end_date']:
                return JsonResponse({'message': '설정한 기간이 올바르지 않습니다.'}, status=210)

            Schedule.objects.create(
                project=Project.objects.get(id=data['project']),
                writer=User.objects.get(id=data['writer']),
                title=data['title'],
                description=data['description'],
                start_date=data['start_date'],
                end_date=data['end_date'],
                color=data['color']
            ).save()

            return JsonResponse({'message': '일정 생성 성공'}, status=201)

        except json.JSONDecodeError as e:
            return JsonResponse({'message': f'Json_ERROR:{e}'}, status=500)
        except KeyError:
            return JsonResponse({'message': 'Invalid Value'}, status=500)


class ScheduleDetail(View):
    def get(self, request, id):
        try:
            schedule = Schedule.objects.get(id=id)
            schedule = model_to_dict(schedule)

            return JsonResponse({'schedule_content': schedule}, status=200)

        except json.JSONDecodeError as e:
            return JsonResponse({'message': f'Json_ERROR:{e}'}, status=500)
        except KeyError:
            return JsonResponse({'message': 'Invalid Value'}, status=500)

    def put(self, request, id):
        try:
            data = json.loads(request.body)

            # 필수항목 미입력
            for val in data.values():
                if val == "":
                    return JsonResponse({'message': '필수 항목을 모두 입력하세요.'}, status=210)

            # 날짜 정보 부정확
            if data['start_date'] > data['end_date']:
                return JsonResponse({'message': '설정한 기간이 올바르지 않습니다.'}, status=210)

            schedule = Schedule.objects.get(id=id)
            schedule.title = data['title']
            schedule.description = data['description']
            schedule.start_date = data['start_date']
            schedule.end_date = data['end_date']
            schedule.color = data['color']
            schedule.save()

            return JsonResponse({'message': '일정 수정 성공'}, status=200)

        except json.JSONDecodeError as e:
            return JsonResponse({'message': f'Json_ERROR:{e}'}, status=500)
        except KeyError:
            return JsonResponse({'message': 'Invalid Value'}, status=500)

    def delete(self, request, id):
        try:
            Schedule.objects.get(id=id).delete()

            return JsonResponse({'message': '일정 삭제 성공'}, status=200)

        except json.JSONDecodeError as e:
            return JsonResponse({'message': f'Json_ERROR:{e}'}, status=500)
        except KeyError:
            return JsonResponse({'message': 'Invalid Value'}, status=500)

# 자료


class FileList(View):
    def get(self, request):
        project_id = request.GET.get('project', None)

        try:
            files = list(File.objects.filter(project=project_id).values())
            for file in files:
                file['writer_name'] = User.objects.get(
                    id=file['writer_id']).name + '(' + file['writer_id'] + ')'

            return JsonResponse({'file': list(files)}, status=200)

        except KeyError:
            return JsonResponse({"message": "Invalid Value"}, status=500)

    def post(self, request):
        try:
            data = json.loads(request.body)
            data['create_at'] = str(datetime.date.today())

            # 필수항목 미입력
            for val in data.values():
                if val == "":
                    return JsonResponse({'message': '필수 항목을 모두 입력하세요.'}, status=210)

            File.objects.create(
                project=Project.objects.get(id=data['project']),
                writer=User.objects.get(id=data['writer']),
                title=data['title'],
                description=data['description'],
                file_name=data['file_name'],
                file_url=data['file_url'],
                create_at=data['create_at']
            ).save()

            return JsonResponse({'message': '파일 생성 성공'}, status=201)
        except json.JSONDecodeError as e:
            return JsonResponse({'message': f'Json_ERROR:{e}'}, status=500)
        except KeyError:
            return JsonResponse({'message': 'Invalid Value'}, status=500)


class FileDetail(View):
    def get(self, request, id):

        try:
            files = list(File.objects.filter(id=id).values())
            for file in files:
                file['writer_name'] = User.objects.get(
                    id=file['writer_id']).name + '(' + file['writer_id'] + ')'
                file['writer_name_only'] = User.objects.get(
                    id=file['writer_id']).name

            return JsonResponse({'file': file})

        except json.JSONDecodeError as e:
            return JsonResponse({'message': f'Json_ERROR:{e}'}, status=500)
        except KeyError:
            return JsonResponse({'message': 'Invalid Value'}, status=500)

    def put(self, request, id):
        try:
            data = json.loads(request.body)
            data['create_at'] = str(datetime.date.today())

            # 필수항목 미입력
            for val in data.values():
                if val == "":
                    return JsonResponse({'message': '필수 항목을 모두 입력하세요.'}, status=210)

            file = File.objects.get(id=id)

            file.title = data['title']
            file.description = data['description']
            file.file_name = data['file_name']
            file.file_url = data['file_url']
            file.create_at = data['create_at']
            file.save()

            return JsonResponse({'message': '파일 수정 성공'}, status=201)

        except json.JSONDecodeError as e:
            return JsonResponse({'message': f'Json_ERROR:{e}'}, status=500)
        except KeyError:
            return JsonResponse({'message': 'Invalid Value'}, status=500)

    def delete(self, request, id):
        try:
            File.objects.get(id=id).delete()

            return JsonResponse({'message': '파일 삭제 성공'}, status=200)

        except json.JSONDecodeError as e:
            return JsonResponse({'message': f'Json_ERROR:{e}'}, status=500)
        except KeyError:
            return JsonResponse({'message': 'Invalid Value'}, status=500)
