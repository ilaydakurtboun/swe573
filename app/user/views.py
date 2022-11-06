from django.shortcuts import render
from .serializers import UserRegisterSerializer,UserLoginSerializer
from .models import User
# Create your views here.
from rest_framework.views import APIView
from django.template.response import TemplateResponse

def index(request):
    return render (request=request, template_name="main.html")


def register_form(request):
    return render (request=request, template_name="register.html")


# class UserLoginAPIView(APIView):
#     serializer_class = UserRegisterSerializer

#     def post(self, request, *args, **kwargs):
def register(request):
    first_name=request.POST['first_name']
    last_name=request.POST['last_name']
    email=request.POST['email']
    password=request.POST['password']
    password2=request.POST['password2']

    print(first_name,last_name,email,password,password2)
    user_exist = User.objects.filter(email=email).first()
    if user_exist:
        args={}
        args['error'] = "There is already an account with this email."
        return render(request,'error.html', args)
    else:
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