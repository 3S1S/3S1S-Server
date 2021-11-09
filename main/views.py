from django.http.response import JsonResponse
from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from django.views import View
from rest_framework.views import APIView
from rest_framework import generics

import json
import bcrypt
import re

from main.models import User
from main.serializer import UserSerializer

# @csrf_exempt
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
                return JsonResponse({'message' : '동일한 ID가 존재합니다.'}, status = 401)
            
            # 비밀번호 재입력 불일치
            if data['password'] != data['password_check']:
                return JsonResponse({'message' : '비밀번호가 일치하지 않습니다.'}, status = 402)

            # 이메일 중복
            if User.objects.filter(email = data['email']).exists():
                return JsonResponse({'message' : '동일한 이메일로 가입한 회원이 존재합니다.'}, status = 403)
            else: # 이메일 형식 오류
                regex= re.compile(r"[a-zA-Z0-9_]+@[a-z]+[.]com")
                mo = regex.search(data['email'])
                if mo == None:
                    return JsonResponse({'message' : '이메일 형식이 옳지 않습니다.'}, status = 403)
            
            User.objects.create(
                id = data['id'],
                password = bcrypt.hashpw(data['password'].encode("UTF-8"), bcrypt.gensalt()).decode("UTF-8"),
                name = data['name'],
                email = data['email']
            ).save()

            return JsonResponse({'message' : '회원가입 성공'}, status = 200)

        except json.JSONDecodeError as e :
            return JsonResponse({"status": 400, 'message': f'Json_ERROR:{e}'}, status = 400)
        except KeyError:
            return JsonResponse({"status": 400, "message" : "Invalid Value"}, status = 400)