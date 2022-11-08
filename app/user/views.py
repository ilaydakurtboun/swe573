from django.shortcuts import render
from .serializers import UserRegisterSerializer,UserLoginSerializer
from .models import User
# Create your views here.
from rest_framework.views import APIView
from django.template.response import TemplateResponse
import re

EMAIL_FORMAT_REGEX = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

def index(request):
    return render (request=request, template_name="main.html")


def register_form(request):
    return render (request=request, template_name="register.html")


def register(request):
    first_name=request.POST['first_name']
    last_name=request.POST['last_name']
    email=request.POST['email']
    password=request.POST['password']
    password2=request.POST['password2']

    if first_name is None or first_name=="":
        args={}
        args['error'] = "First Name can not be empty."
        return render(request,'error.html', args)

    if last_name is None or last_name=="":
        args={}
        args['error'] = "Last Name can not be empty."
        return render(request,'error.html', args)

    if email is None  or email=="":
        args={}
        args['error'] = "Email can not be empty."
        return render(request,'error.html', args)

    if password is None or password=="":
        args={}
        args['error'] = "Password can not be empty."
        return render(request,'error.html', args)

    if password2 is None or password2=="":
        args={}
        args['error'] = "Password Confimation can not be empty."
        return render(request,'error.html', args)

    if re.fullmatch(EMAIL_FORMAT_REGEX,email) is None:
        args={}
        args['error'] = "Email format is invalid."
        return render(request,'error.html', args)

    user_exist = User.objects.filter(email=email).first()
    if user_exist:
        args={}
        args['error'] = "There is already an account with this email."
        return render(request,'error.html', args)
    # else:
    serializer = UserRegisterSerializer(data=request.POST)
    if serializer.is_valid():
        serializer.save()
        return render (request=request, template_name="login.html")
    else:
        args={}
        args['error'] = "Passwords are not matched."
        return render(request,'error.html', args)


def login_form(request):
    return render (request=request, template_name="login.html")


def login(request):
    data = request.POST
    email=request.POST['email']
    user = User.objects.filter(email=email).first()
    if not user:
        args={}
        args['error']="There is no account with this email."
        return render (request, "error.html",args)
    serializer = UserLoginSerializer(data=data)
    if serializer.is_valid():
        return render (request=request, template_name="loginSuccess.html")
    else:
        args={}
        args['error']="Incorrect password."
        return render (request, "error.html",args)
