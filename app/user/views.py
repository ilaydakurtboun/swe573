from django.shortcuts import render
from .serializers import UserRegisterSerializer,UserLoginSerializer
from .models import User
# Create your views here.
from rest_framework.views import APIView

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

    serializer = UserRegisterSerializer(data=request.POST)
    serializer.is_valid(raise_exception=True)
    serializer.save()
    email = serializer.data.get("email")
    user = User.objects.filter(email=email).first()

    return render (request=request, template_name="login.html")


def login_form(request):
    return render (request=request, template_name="login.html")


def login(request):
    data = request.POST
    email=request.POST['email']
    user = User.objects.get(email=email)
    serializer = UserLoginSerializer(data=data)
    if serializer.is_valid(raise_exception=True):
        return render (request=request, template_name="loginSuccess.html")
    return render (request=request, template_name="main.html")