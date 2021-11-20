from django.db import connection
from django.http.response import JsonResponse
from django.shortcuts import redirect
from django.urls import reverse
from django.http import HttpResponse
from django.utils.functional import empty
from django.views.decorators.csrf import csrf_exempt
from django.views import View

from rest_framework import generics

import json
import bcrypt
import re
import datetime 
import jwt
import datetime
import ast


from main.models import Participant, Project, Todo, User, Member, Notification
from main.serializer import ProjectSerializer, UserSerializer, MemberSerializer, NotificationSerializer
from config import SECRET_KEY 

# Create your views here.
def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")

def reorder(object):
    cur = connection.cursor()
        
    cur.execute("ALTER TABLE " + object + " AUTO_INCREMENT=1")
    cur.execute("SET @COUNT = 0")
    cur.execute("UPDATE " + object + " SET id = @COUNT:=@COUNT+1")
    cur.fetchall()
    
    connection.commit()
    connection.close()

## 회원
# 회원가입
class SignUp(View):
    def post(self, request):
        data = json.loads(request.body)

        try:
            # 필수항목 미입력
            for key, val in data.items():
                if val == "" and key not in ['checked_id', 'belong']:
                    return JsonResponse({'message' : '필수 항목을 모두 입력하세요.'}, status =210)
            
            # ID 중복
            if data['id'] != data['checked_id']:
                return JsonResponse({'message' : 'ID 중복 확인을 수행하세요.'}, status =210)

            # 비밀번호 재입력 불일치
            if data['password'] != data['password_check']:
                return JsonResponse({'message' : '비밀번호가 일치하지 않습니다.'}, status = 210)

            # 이메일 중복
            if User.objects.filter(email = data['email']).exists():
                return JsonResponse({'message' : '동일한 이메일로 가입한 회원이 존재합니다.'}, status = 210)
            
            else: # 이메일 형식 오류
                regex= re.compile(r"[a-zA-Z0-9_]+@[a-z]+[.][a-z.]+")
                mo = regex.search(data['email'])
                if mo == None:
                    return JsonResponse({'message' : '이메일 형식이 옳지 않습니다.'}, status = 210)
            
            User.objects.create(
                id = data['id'],
                password = bcrypt.hashpw(data['password'].encode("UTF-8"), bcrypt.gensalt()).decode("UTF-8"),
                name = data['name'],
                email = data['email'],
                belong = data['belong']
            ).save()

            return JsonResponse({'message' : '회원가입 성공'}, status = 210)

        except json.JSONDecodeError as e :
            return JsonResponse({'message': f'Json_ERROR:{e}'}, status = 500)
        except KeyError:
            return JsonResponse({'message' : 'Invalid Value'}, status = 500)

# 로그인
class SignIn(View):
    @csrf_exempt
    def post(self, request):
        data = json.loads(request.body)
        
        try: 
            if data['id'] == "" or data['password'] == "":
                return JsonResponse({"message": "Please fill in the required items."}, status = 210) 

            if User.objects.filter(id = data['id']).exists():
                user = User.objects.get(id = data['id'])

                if bcrypt.checkpw(data['password'].encode('UTF-8'), user.password.encode('UTF-8')):
                    id = user.id
                    name = user.name
                    return JsonResponse({'id' : id, 'name' : name}, status=200)

                return JsonResponse({"message" : "Wrong Password"}, status = 210)
              
            return JsonResponse({"message": "Unexist ID"}, status = 210)
        
        except json.JSONDecodeError as e :
            return JsonResponse({'message': f'Json_ERROR:{e}'}, status = 500)
        except KeyError:
            return JsonResponse({'message' : 'Invalid Value'}, status = 500)
    
# ID 중복 확인
class CheckID(View):
    def get(self,request):
        id = request.GET.get('id', None)
        try:
            # 항목 미입력
            if id == "":
                return JsonResponse({'message' : 'ID를 입력하세요.', 'checked_id' : ""}, status =210)

            # ID 중복
            if User.objects.filter(id = id).exists():
                return JsonResponse({'message' : '동일한 ID가 존재합니다.', 'checked_id' : ""}, status = 210)
            else: 
                return JsonResponse({'message' : '생성 가능한 ID입니다.', 'checked_id': id}, status = 200)

        except json.JSONDecodeError as e :
            return JsonResponse({'message': f'Json_ERROR:{e}'}, status = 500)
        except KeyError:
            return JsonResponse({'message' : 'Invalid Value'}, status = 500)


## 프로젝트
# 프로젝트 생성, 목록
class ProjectList(View):
    def get(self, request):
        id = request.GET.get('id',None)

        try:
            project_list = list(Member.objects.filter(user_id = id).values('project_id'))
            
            result = ""
            for project in project_list:
                if result != "":
                    result |= Project.objects.filter(id = project['project_id'])
                else: result = Project.objects.filter(id = project['project_id'])

            return JsonResponse({'project_list' : list(result.values()) if result != "" else []}, status = 200)
        
        except json.JSONDecodeError as e :
            return JsonResponse({'message': f'Json_ERROR:{e}'}, status = 500)
        except KeyError:
            return JsonResponse({'message' : 'Invalid Value'}, status = 500)
    
    def post(self, request):
        data = json.loads(request.body)

        try:
            # 필수항목 미입력
            for key, val in data.items():
                if val == "" and key in ['title', 'team', 'description']:
                    return JsonResponse({'message' : '필수 항목을 모두 입력하세요.'}, status =210)

            created_project = Project.objects.create(
                title = data['title'],
                team = data['team'],
                description = data['description'],
                subject = data['subject'],
                purpose = data['purpose'],
                progress_rate = 0.0,
                img_url = data["img_url"]
            )
            created_project.save()

            Member.objects.create(
                project = created_project,
                user = User.objects.get(id = data['creator']),
                leader = 1,
                contribution_rate = 0.0
            ).save()
            
            return JsonResponse({'message' : '프로젝트 생성 성공'}, status = 201)

        except json.JSONDecodeError as e :
            return JsonResponse({'message': f'Json_ERROR:{e}'}, status = 500)
        except KeyError:
            return JsonResponse({'message': 'Invalid Value'}, status = 500)   

class ProjectDetail(View):
    def get(self, request, id):
        item = list(Project.objects.filter(id = id).values())[0]

        try:
            return JsonResponse({'Project_content' : item}, status = 201)

        except json.JSONDecodeError as e :
            return JsonResponse({'message': f'Json_ERROR:{e}'}, status = 500)
        except KeyError:
            return JsonResponse({'message': 'Invalid Value'}, status = 500)   

    def delete(self, request, id):
        try:
            Project.objects.get(id = id).delete()
        
            return JsonResponse({'message': '프로젝트 삭제 성공'}, status = 200)

        except json.JSONDecodeError as e :
            return JsonResponse({'message': f'Json_ERROR:{e}'}, status = 500)
        except KeyError:
            return JsonResponse({'message': 'Invalid Value'}, status = 500)  


## 멤버
# 멤버 추가, 목록
class MemberList(generics.ListCreateAPIView):
    queryset = Member.objects.all()
    serializer_class = MemberSerializer
    
    # get 메소드 파라미터로 입력된 프로젝트의 멤버를 모두 보여준다.    
    def get(self, request, *args, **kwargs):
        reorder("Member")
        
        project_id = request.GET.get('project', None)
        try:        
            queryset = Member.objects.filter(project = project_id).all()    
            return JsonResponse({'data': list(queryset.values())}, status = 200)
        
        except KeyError:
            return JsonResponse({"message" : "Invalid Value"}, status = 400)
        
class DeleteMember(View):
    def post(self, request):
        data = json.loads(request.body)
        
        try:
            Member.objects.get(project = data['project'], user = data['user']).delete()

            if not Member.objects.filter(project = data['project']).exists():
                ProjectDetail.delete(self, request, id = data['project'])
                return JsonResponse({'message': '프로젝트 탈퇴 후 프로젝트 삭제'}, status = 200)

            return JsonResponse({'message': '프로젝트 탈퇴 성공'}, status = 200)

        except json.JSONDecodeError as e :
            return JsonResponse({'message': f'Json_ERROR:{e}'}, status = 500)
        except KeyError:
            return JsonResponse({'message': 'Invalid Value'}, status = 500)  

## 알림
# 알림 생성
class NotificationList(View):
    # get 메소드 파라미터로 입력된 invitee의 알림을 모두 보여준다.      
    def get(self, request, *args, **kwargs):
        reorder("Notification")
        invitee_id = request.GET.get('invitee',None)
        
        try:        
            notifications = list(Notification.objects.filter(invitee = invitee_id).values())
            for notification in notifications:
                notification['project_title'] = Project.objects.filter(id = notification['project_id'])[0].title
                notification['invitee_name'] = User.objects.get(id = notification['invitee_id']).name
                notification['inviter_name'] = User.objects.get(id = notification['inviter_id']).name

            return JsonResponse({'notifications': notifications}, status = 200)
        
        except KeyError:
            return JsonResponse({"message" : "Invalid Value"}, status = 400)
        
    def post(self, request, *args, **kwargs):
        data=json.loads(request.body)

        try:    
            #이미 알림을 보냈을 경우 
            if Notification.objects.filter(project = data['project'], invitee = data['invitee']).exists() :
                return JsonResponse({"message" : "이미 알림을 보냈습니다"}, status = 210)
            
            #이미 멤버로 참여 하고 있을 경우 
            if Member.objects.filter(project = data['project'], user = data['invitee']).exists() :
                return JsonResponse({"message" : "이미 멤버로 참여하고 있습니다."}, status = 210)
                    
            #해당 학생이 없을 때
            if not User.objects.filter(id = data['invitee']).exists():
                return JsonResponse({"message" : "해당 학생이 없습니다."}, status = 210)

            data['invite_date'] = str(datetime.datetime.now())

            Notification.objects.create(
                project = Project.objects.get(id = data['project']),
                invitee = User.objects.get(id = data['invitee']),
                inviter = User.objects.get(id = data['inviter']),
                invite_date = data['invite_date']
            ).save()
            
            return JsonResponse({'message': '초대 알림 생성 성공'})

        except json.JSONDecodeError as e :
                return JsonResponse({'message': f'Json_ERROR:{e}'}, status = 500)
        except KeyError:
                return JsonResponse({'message' : 'Invalid Value'}, status = 500)

            

# 알림 수락 / 거절
class NotificationResponse(View):

    #알림을 수락 하였을 때 멤버 db에 추가 
    def post(self, request, *args, **kwargs):
        data=json.loads(request.body)
        
        try:
            # 수락 했을 때 
            # 성공 status 201
            if data['accept'] == 1:
                
                ## leader의 값은 무조건 0이 된다.
                Member.objects.create(
                    project = Project.objects.get(id = data['project']),
                    user = User.objects.get(id = data['user']),
                    leader = 0,
                    contribution_rate = 0
                ).save()
                message, status = '멤버 초대를 수락 하였습니다.', 201
            # 거절 했을 때 
            # 거절 status 200
            else:
                message, status = '멤버 초대를 거절 하였습니다.', 200
            
            # 알림 삭제 
            Notification.objects.filter(project = data['project'], invitee = data['user']).delete()     
            
            return JsonResponse({'message': message}, status = status) 
            
        except json.JSONDecodeError as e :
            return JsonResponse({'message': f'Json_ERROR:{e}'}, status = 500)
        except KeyError:
            return JsonResponse({'message' : 'Invalid Value'}, status = 500)


## ToDo
# ToDo 생성, 목록
class ToDoList(View):
    def get(self, request):
        project, state = request.GET.get('project', None), request.GET.get('state', None)

        try:    
            todos = list(Todo.objects.filter(project = project, state = state).values())

            for todo in todos:
                d_day = todo['d_day'] = (datetime.date.today() - todo['end_date']).days
                d_day = " + " + str(d_day) if d_day > 0 else " - " + (str(d_day * -1) if d_day != 0 else 'Day')
                todo['d_day'] = "D" + d_day

                participants = Participant.objects.filter(todo = todo['id']).values('user')
                participants = [d['user'] for d in participants]
                todo['participants'] = participants

            return JsonResponse({'todo_list': todos}, status = 200)
        
        except json.JSONDecodeError as e :
                return JsonResponse({'message': f'Json_ERROR:{e}'}, status = 500)
        except KeyError:
                return JsonResponse({'message': 'Invalid Value'}, status = 500)

    def post(self, request):
        data = json.loads(request.body)

        try:
            # 필수항목 미입력
            for val in data.items():
                if val == "":
                    return JsonResponse({'message' : '필수 항목을 모두 입력하세요.'}, status =210)

            # 날짜 정보 부정확
            if data['start_date'] > data['end_date']:
                return JsonResponse({'message' : '설정한 기간이 올바르지 않습니다.'}, status =210)

            created_todo = Todo.objects.create(
                project = Project.objects.get(id = data['project']),
                writer = User.objects.get(id = data['writer']),
                title = data['title'],
                description = data['description'],
                state = 0,
                start_date = data['start_date'],
                end_date = data['end_date']
            )
            created_todo.save()

            for participant in data['participants']:
                Participant.objects.create(
                    todo = created_todo,
                    user = User.objects.get(id = participant)
                ).save()
            
            return JsonResponse({'message' : 'ToDo 생성 성공'}, status = 201)

        except json.JSONDecodeError as e :
            return JsonResponse({'message': f'Json_ERROR:{e}'}, status = 500)
        except KeyError:
            return JsonResponse({'message' : 'Invalid Value'}, status = 500)


class ToDo_state_change(View):
    def post(self, request):

        data = json.loads(request.body)
        
        todo_instance = Todo.objects.get(id=data['todo'])
        todo_project = Todo.objects.get(id=data['todo']).project
  
        member_list = Member.objects.filter(project = todo_project).values('user')     
        member_list = [d['user'] for d in member_list]
                               
        #시작전 -> 진행중      
        if data['state'] == 1 and todo_instance.state == 0:
            todo_instance.state = 1
            todo_instance.save()
            
        #시작전 -> 완료      
        elif data['state'] == 2 and todo_instance.state == 0:
            todo_instance.state = 2
            todo_instance.save()
            
            
            ##이 프로젝트에서 Todo 완료한 participant id (user id X)
            total_participants = Todo.objects.filter(state = 2, project = todo_project).values('participant')         
            total_participants = [d['participant'] for d in total_participants]
            if len(total_participants) > 1:
                total_participants.pop(0)
            ## 새로 기여도를 계산 하기위해 초기화하여 저장 
            for z in range(len(member_list)):
                zero = Member.objects.get(user = member_list[z], project = todo_project)                     
                zero.contribution_rate = 0
                zero.save()
            
            ## 기여도를 게산 하여 저장 
            for n in range(len(member_list)):
                for m in range(len(total_participants)):
                    participants_id = Participant.objects.get(id = total_participants[m]).user.id
                    member_id = member_list[n]
                    if  participants_id== member_id:                    
                        member_new_rate = Member.objects.get(user = member_list[n], project = todo_project)                     
                        member_new_rate.contribution_rate += 1.0                    
                        member_new_rate.save()
                member_rate = Member.objects.get(user = member_list[n], project = todo_project) 
                member_rate.contribution_rate = member_rate.contribution_rate / (len(total_participants) + 0.0001)
                temp = member_rate.contribution_rate 
                member_rate.contribution_rate = round(temp, 2)*100           
                member_rate.save()
            
        
        #진행중 -> 시작전      
        elif data['state'] == 0 and todo_instance.state == 1:
            todo_instance.state = 0
            todo_instance.save()
              
        #진행중 -> 완료 
        elif data['state'] == 2 and todo_instance.state == 1:
            todo_instance.state = 2
            todo_instance.save()
            
            total_participants = Todo.objects.filter(state = 2, project = todo_project).values('participant')         
            total_participants = [d['participant'] for d in total_participants]
            if len(total_participants) > 1:
                total_participants.pop(0)
             ## 새로 기여도를 계산 하기위해 초기화하여 저장 
            for z in range(len(member_list)):
                zero = Member.objects.get(user = member_list[z], project = todo_project)                     
                zero.contribution_rate = 0
                zero.save()
            
            ## 기여도를 게산 하여 저장 
            for n in range(len(member_list)):
                for m in range(len(total_participants)):
                    participants_id = Participant.objects.get(id = total_participants[m]).user.id
                    member_id = member_list[n]
                    if  participants_id== member_id:                    
                        member_new_rate = Member.objects.get(user = member_list[n], project = todo_project)                     
                        member_new_rate.contribution_rate += 1.0                    
                        member_new_rate.save()
                member_rate = Member.objects.get(user = member_list[n], project = todo_project) 
                member_rate.contribution_rate = member_rate.contribution_rate / (len(total_participants) + 0.0001)
                temp = member_rate.contribution_rate 
                member_rate.contribution_rate = round(temp, 2)*100            
                member_rate.save()
        
        #완료 -> 진행중      
        elif data['state'] == 1 and todo_instance.state == 2:
            todo_instance.state = 1
            todo_instance.save()
                        
            total_participants = Todo.objects.filter(state = 2, project = todo_project).values('participant')         
            total_participants = [d['participant'] for d in total_participants]
            if len(total_participants) > 1:
                total_participants.pop(0)
                
            ## 새로 기여도를 계산 하기위해 초기화하여 저장 
            for z in range(len(member_list)):
                zero = Member.objects.get(user = member_list[z], project = todo_project)                     
                zero.contribution_rate = 0
                zero.save()
            
            ## 기여도를 게산 하여 저장 
            for n in range(len(member_list)):
                for m in range(len(total_participants)):
                    participants_id = Participant.objects.get(id = total_participants[m]).user.id
                    member_id = member_list[n]
                    if  participants_id== member_id:                    
                        member_new_rate = Member.objects.get(user = member_list[n], project = todo_project)                     
                        member_new_rate.contribution_rate += 1.0                    
                        member_new_rate.save()
                member_rate = Member.objects.get(user = member_list[n], project = todo_project) 
                member_rate.contribution_rate = member_rate.contribution_rate / (len(total_participants) + 0.0001)
                temp = member_rate.contribution_rate 
                member_rate.contribution_rate = round(temp, 2)*100             
                member_rate.save()
                
        
        #완료 -> 시작전 
        elif data['state'] == 0 and todo_instance.state == 2:
            todo_instance.state = 0
            todo_instance.save()
            
            total_participants = Todo.objects.filter(state = 2, project = todo_project).values('participant')         
            total_participants = [d['participant'] for d in total_participants]
            if len(total_participants) > 1:
                total_participants.pop(0)  
            
            ## 새로 기여도를 계산 하기위해 초기화하여 저장 
            for z in range(len(member_list)):
                zero = Member.objects.get(user = member_list[z], project = todo_project)                     
                zero.contribution_rate = 0
                zero.save()
            
            ## 기여도를 게산 하여 저장 
            for n in range(len(member_list)):
                for m in range(len(total_participants)):
                    participants_id = Participant.objects.get(id = total_participants[m]).user.id
                    member_id = member_list[n]
                    if  participants_id== member_id:                    
                        member_new_rate = Member.objects.get(user = member_list[n], project = todo_project)                     
                        member_new_rate.contribution_rate += 1.0                    
                        member_new_rate.save()
                member_rate = Member.objects.get(user = member_list[n], project = todo_project) 
                member_rate.contribution_rate = member_rate.contribution_rate / (len(total_participants) + 0.0001)
                temp = member_rate.contribution_rate 
                member_rate.contribution_rate = round(temp, 2)*100              
                member_rate.save()
                
                

        
        else:
            return JsonResponse({'message': 'fail'})
        
                ## 진행율 계산 
        complete_todo = Todo.objects.filter(state = 2, project = todo_project).values('id')         
        complete_todo = [d['id'] for d in complete_todo]
        
        ing_todo = Todo.objects.filter(state = 1, project = todo_project).values('id')         
        ing_todo = [d['id'] for d in ing_todo]
        
        pre_todo = Todo.objects.filter(state = 0, project = todo_project).values('id')         
        pre_todo = [d['id'] for d in pre_todo]
        
        project_instance = Project.objects.get(id=todo_project.id)
        
        total_prog = len(complete_todo) + len(ing_todo) + len(pre_todo)
        comp_prog = len(complete_todo)
        
        project_instance.progress_rate = round((comp_prog / total_prog), 2) * 100
        project_instance.save()
                
        
        return JsonResponse({'message': complete_todo})
    
        return JsonResponse({'message': 'success'})
         
