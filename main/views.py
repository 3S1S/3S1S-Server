from django.http.response import JsonResponse
from django.shortcuts import render
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

from django.views import View
from rest_framework.views import APIView
from rest_framework import generics

import json
import bcrypt

from main.models import User
from main.serializer import UserSerializer

# Create your views here.
def index(request):
    return HttpResponse("Hello, world. You're at the polls index.")

class SignUp(View):
    @csrf_exempt
    def post(self, request):
        data = json.loads(request.body)
        
        print(len(data))
        try:
            # ID 중복확인
            if User.objects.filter(id = data['id']).exists():
                return JsonResponse({'message' : '동일한 ID가 존재합니다.'}, status = 400)
            
            User.objects.create(
                id = data['id'],
                password = bcrypt.hashpw(data['password'].encode("UTF-8"), bcrypt.gensalt()).decode("UTF-8"),
                name = data['name'],
                email = data['email']
            ).save()

            return JsonResponse({'message' : 'Success'}, status = 200)

        except json.JSONDecodeError as e :
            return JsonResponse({"status": 400, 'message': f'Json_ERROR:{e}'}, status = 400)
        except KeyError:
            return JsonResponse({"status": 400, "message" : "Invalid Value"}, status = 400)

            