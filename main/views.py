from django.db.models import query
from django.db.models.query import QuerySet
from django.db.models.query_utils import Q
from django.http.response import JsonResponse
from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from django.views import View
from rest_framework.serializers import Serializer
from rest_framework.views import APIView
from rest_framework import generics

import json, ast
import bcrypt
import re
import datetime 
import jwt

from main.models import Project, User, Member, Notification
from main.serializer import ProjectSerializer, UserSerializer, MemberSerializer, NotificationSerializer
from config import SECRET_KEY 

# Create your views here.
def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")

class SignUp(View):
    def post(self, request):
        data = json.loads(request.body)

        try:
            # 필수항목 미입력
            for val in data.values():
                if val == "":
                    return JsonResponse({'message' : '필수 항목을 모두 입력하세요.'}, status =400)
            
            # ID 중복
            if User.objects.filter(id = data['id']).exists():
                return JsonResponse({'message' : '동일한 ID가 존재합니다.'}, status = 400)
            
            # 비밀번호 재입력 불일치
            if data['password'] != data['password_check']:
                return JsonResponse({'message' : '비밀번호가 일치하지 않습니다.'}, status = 400)

            # 이메일 중복
            if User.objects.filter(email = data['email']).exists():
                return JsonResponse({'message' : '동일한 이메일로 가입한 회원이 존재합니다.'}, status = 400)
            else: # 이메일 형식 오류
                regex= re.compile(r"[a-zA-Z0-9_]+@[a-z]+[.]com")
                mo = regex.search(data['email'])
                if mo == None:
                    return JsonResponse({'message' : '이메일 형식이 옳지 않습니다.'}, status = 400)
            
            User.objects.create(
                id = data['id'],
                password = bcrypt.hashpw(data['password'].encode("UTF-8"), bcrypt.gensalt()).decode("UTF-8"),
                name = data['name'],
                email = data['email']
            ).save()

            return JsonResponse({'message' : '회원가입 성공'}, status = 201)

        except json.JSONDecodeError as e :
            return JsonResponse({"status": 400, 'message': f'Json_ERROR:{e}'}, status = 400)
        except KeyError:
            return JsonResponse({"status": 400, "message" : "Invalid Value"}, status = 400)



class SignIn(View):
    @csrf_exempt
    def post(self, request):
        data = json.loads(request.body)

        try: 
            if data['id'] == "" or data['password'] == "":
                return JsonResponse({"message": "Please fill in the required items."}, status = 400) 

            if User.objects.filter(id = data['id']).exists():
                user = User.objects.get(id = data['id'])


                if bcrypt.checkpw(data['password'].encode('UTF-8'), user.password.encode('UTF-8')):
                    token = user.id
                    return JsonResponse({'token' : token}, status=200)

                return JsonResponse({"message" : "Wrong Password"}, status = 201)
              
            return JsonResponse({"message": "Unexist ID"}, status = 202)
        except KeyError:

            return JsonResponse({"message" : "Invalid Value"}, status = 401)


class ProjectList (generics.ListCreateAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    
class MemberList(generics.ListCreateAPIView):
    queryset = Member.objects.all()
    serializer_class = MemberSerializer
    
    def create(self, request, *args, **kwargs):
            # request에서 body 뽑아오기
        byte_str = request.body
        dict_str = byte_str.decode("UTF-8")
        data = eval(repr(ast.literal_eval(dict_str)))

        try:
            #중복된 멤버
            if Member.objects.filter(project = data['project'], user = data['user']).exists() :
                return JsonResponse({"message" : "이미 멤버로 참여하고 있습니다."}, status = 210)
        
            #해당 학생이 없을 때
            if not User.objects.filter(id = data['user']).exists():
                return JsonResponse({"message" : "해당 학생이 없습니다."}, status = 210)

            # 중복된 리더 
            if data['leader']== 1:
                if Member.objects.filter(project = data['project'], leader = data['leader']).exists():
                    return JsonResponse({"message" : "리더가 이미 있습니다."}, status = 210)

            # 성공했을 때 
            # 성공 status 201
            return super().create(request, *args, **kwargs)
            
        except KeyError:

            return JsonResponse({"message" : "Invalid Value"}, status = 401)
        

        
    