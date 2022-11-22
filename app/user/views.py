from django.shortcuts import render
from django.template.response import TemplateResponse
import re
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from .models import *
from .serializers import *
from django.contrib.auth import authenticate, login, logout
from .sendEmail import sendEmail
EMAIL_FORMAT_REGEX = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
import uuid
from feed.models import Space

def index(request):
    print(request.user)
    spaces = Space.objects.all()
    return render (request,"main.html",{"spaces":spaces})

class UserViewSet(viewsets.ModelViewSet):
    User = get_user_model()
    queryset = User.objects.all()

    def create(self, request, *args, **kwargs):
        first_name=request.data.get('first_name')
        last_name=request.data.get('last_name')
        email=request.data.get('email')
        password=request.data.get('password')
        password2=request.data.get('password2')

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
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return render (request=request, template_name="login.html")
        else:
            args={}
            args['error'] = "Passwords are not matched."
            return render(request,'error.html', args)
    
    @action(detail=False, methods=["GET"])
    def register_form(self, request, *args, **kwargs):
        print(request.user)
        return render (request=request, template_name="register.html")

    @action(detail=False, methods=["GET"])
    def login_form(self, request, *args, **kwargs):
        return render (request=request, template_name="login.html")
    
    @action(detail=False, methods=["POST"])
    def login(self, request):
        data = request.data
        user = User.objects.filter(email=request.data.get("email")).first()
        if not user:
            args={}
            args['error'] = "There is no account with this email."
            return render(request,'error.html', args)
        serializer = UserLoginSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            res = {
                'success': 'True',
                'status code': status.HTTP_200_OK,
                'message': 'User logged in  successfully',
            }
            new_data = serializer.data
            res.update(new_data)
            # return Response(res,200)
            login(request, user)
            # return render (request=request, template_name="loginSuccess.html")
            spaces=Space.objects.all().order_by("-id")
            return render (request, "spaces.html",{"spaces":spaces,"owner":user.first_name + " " + user.last_name})
            
    @action(detail=False, methods=["GET"])
    def logout(self, request, *args, **kwargs):
        print(request.user)
        user = User.objects.get(id=request.user.id)
        logout(request)
        return render (request=request, template_name="login.html")

    @action(detail=False, methods=['get'], name='Reset Password')
    def reset_password_form(self, request, *args, **kwargs):
        return render (request=request, template_name="resetPasswordRequest.html")
        
    @action(detail=False, methods=['post'], name='Reset Password')
    def reset_password_request(self, request, *args, **kwargs):
        data = request.data
        email = data.get("email")
        code = uuid.uuid4()
        ResetPassword.objects.create(email=email,code=code)
        sendEmail(email,code)
        # return Response({"detail": "The code for resetting password is sent to your email address."})
        return render (request=request, template_name="resetPassword.html")

    @action(detail=False, methods=['post'], name='Reset Password')
    def reset_password(self, request, *args, **kwargs):
        data = request.data
        print(request.data)
        email = data.get("email")
        code = data.get("code")
        user=User.objects.get(email=email)
        reset_password_obj = ResetPassword.objects.filter(email=email).first()
        if reset_password_obj:
            if reset_password_obj.code == code:
                if data['password'] != data['password2']:
                    raise ValidationError({"error": "New passwords do not match"})
                else:
                    user.set_password(data['password'])
                    user.save()
                    reset_password_obj.delete()
                    # return Response({"detail": "Password is reset successfully"})
                    return render (request=request, template_name="login.html")

            # return Response({"detail": "Incorrect Reset Code"})
            args={}
            args['error'] = "Incorrect Reset Code."
            return render(request,'error.html', args)
            
        # return Response({"detail": "Incorrect Credentials"})
        args={}
        args['error'] = "Incorrect Credentials."
        return render(request,'error.html', args)    

    @action(detail=True, methods=['put'], name='Change Password')
    def change_password(self, request, pk=None):
        data = request.data
        user = self.get_object()
        if user is None:
            raise ValidationError({"error": "There is no such user"})

        if user.check_password(data['old_password']) == False:
            raise ValidationError({"error": "The old password does not match"})

        if data['password']!=data['password2']:
            raise ValidationError({"error": "New passwords do not match"})

        user.set_password(data['password'])
        user.save()
        return Response({"detail":"Changed succesfully"})


    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)

        return Response("Deleted successfully",status=200)

    def get_serializer_class(self):
        if self.action == 'create':
            return UserRegisterSerializer
        else:
            return UserListSerializer

