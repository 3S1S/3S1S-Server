from django.http.response import JsonResponse
from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from django.views import View
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import generics

import json
import bcrypt
import re
import jwt
import datetime
import ast

from main.models import Project, User, Notification
from main.serializer import NotificationSerializer, ProjectSerializer, UserSerializer
from config import SECRET_KEY 

# Create your views here.
def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")

# 회원
class SignUp(View):
    def post(self, request):
        data = json.loads(request.body)

        try:
            # 필수항목 미입력
            for key, val in data.items():
                if val == "" and key != 'belong':
                    return JsonResponse({'message' : '필수 항목을 모두 입력하세요.'}, status =400)
            
            if not data['is_valid']:
                return JsonResponse({'message' : 'ID 중복 확인을 수행해주세요.'}, status =400)

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
                email = data['email'],
                belong = data['belong']
            ).save()

            return JsonResponse({'message' : '회원가입 성공'}, status = 201)

        except json.JSONDecodeError as e :
            return JsonResponse({'message': f'Json_ERROR:{e}'}, status = 500)
        except KeyError:
            return JsonResponse({'message' : 'Invalid Value'}, status = 500)

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
        
        except json.JSONDecodeError as e :
            return JsonResponse({'message': f'Json_ERROR:{e}'}, status = 500)
        except KeyError:
            return JsonResponse({'message' : 'Invalid Value'}, status = 500)

class CheckID(View):
    def get(self,request):
        id = request.GET.get('id', None)
        
        try:
            # ID 중복
            if User.objects.filter(id = id).exists():
                return JsonResponse({'message' : '동일한 ID가 존재합니다.', 'is_valid' : False}, status = 400)
            else: 
                return JsonResponse({'message' : '생성 가능한 ID입니다.', 'is_valid' : True}, status = 200)
        except json.JSONDecodeError as e :
            return JsonResponse({'message': f'Json_ERROR:{e}'}, status = 500)
        except KeyError:
            return JsonResponse({'message' : 'Invalid Value'}, status = 500)


# 프로젝트
class Project(generics.ListCreateAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer

    def get(self, request):
        return JsonResponse({})

class Notification(generics.ListCreateAPIView):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer

    def create(self, request, *args, **kwargs):
        # request에서 body 뽑아오기
        byte_str = request.body
        dict_str = byte_str.decode("UTF-8")
        data = eval(repr(ast.literal_eval(dict_str)))

        # 뽑아온 body에 원하는 작업 수행
        data['invite_date'] = str(datetime.datetime.now())
        
        # 수행 결과를 다시 request에 반영
        data = json.dumps(data, indent=4).encode('utf-8')
        request.body = data

        return super().create(request, *args, **kwargs)
