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

EMAIL_FORMAT_REGEX = r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b"
import uuid
from feed.models import Space
from app.settings import DOMAIN_URL


def index(request):
    print(request.user)
    spaces = Space.objects.all()
    return render(request, "main.html", {"spaces": spaces, "DOMAIN_URL": DOMAIN_URL})


class UserViewSet(viewsets.ModelViewSet):
    User = get_user_model()
    queryset = User.objects.all()

    def create(self, request, *args, **kwargs):
        first_name = request.data.get("first_name")
        last_name = request.data.get("last_name")
        email = request.data.get("email")
        password = request.data.get("password")
        password2 = request.data.get("password2")

        if first_name is None or first_name == "":
            args = {}
            args["error"] = "First Name can not be empty."
            args["DOMAIN_URL"] = DOMAIN_URL
            return render(request, "error.html", args)

        if last_name is None or last_name == "":
            args = {}
            args["error"] = "Last Name can not be empty."
            args["DOMAIN_URL"] = DOMAIN_URL
            return render(request, "error.html", args)

        if email is None or email == "":
            args = {}
            args["error"] = "Email can not be empty."
            args["DOMAIN_URL"] = DOMAIN_URL
            return render(request, "error.html", args)

        if password is None or password == "":
            args = {}
            args["error"] = "Password can not be empty."
            args["DOMAIN_URL"] = DOMAIN_URL
            return render(request, "error.html", args)

        if password2 is None or password2 == "":
            args = {}
            args["error"] = "Password Confimation can not be empty."
            args["DOMAIN_URL"] = DOMAIN_URL
            return render(request, "error.html", args)

        if re.fullmatch(EMAIL_FORMAT_REGEX, email) is None:
            args = {}
            args["error"] = "Email format is invalid."
            args["DOMAIN_URL"] = DOMAIN_URL
            return render(request, "error.html", args)

        user_exist = User.objects.filter(email=email).first()
        if user_exist:
            args = {}
            args["error"] = "There is already an account with this email."
            args["DOMAIN_URL"] = DOMAIN_URL
            return render(request, "error.html", args)
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return render(request, "login.html", {"DOMAIN_URL": DOMAIN_URL})
        else:
            args = {}
            args["error"] = "Passwords are not matched."
            args["DOMAIN_URL"] = DOMAIN_URL
            return render(request, "error.html", args)

    @action(detail=False, methods=["GET"])
    def register_form(self, request, *args, **kwargs):
        print(request.user)
        return render(request, "register.html", {"DOMAIN_URL": DOMAIN_URL})

    @action(detail=False, methods=["GET"])
    def login_form(self, request, *args, **kwargs):
        return render(request, "login.html", {"DOMAIN_URL": DOMAIN_URL})

    @action(detail=False, methods=["POST"])
    def login(self, request):
        data = request.data
        user = User.objects.filter(email=request.data.get("email")).first()
        if not user:
            args = {}
            args["error"] = "There is no account with this email."
            args["DOMAIN_URL"] = DOMAIN_URL
            return render(request, "error.html", args)

        serializer = UserLoginSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            res = {
                "success": "True",
                "status code": status.HTTP_200_OK,
                "message": "User logged in  successfully",
            }
            new_data = serializer.data
            res.update(new_data)
            # return Response(res,200)
            login(request, user)
            # return render (request=request, template_name="loginSuccess.html")
            spaces = Space.objects.all().order_by("-id")
            return render(
                request,
                "spaces.html",
                {
                    "spaces": spaces,
                    "owner": user.first_name + " " + user.last_name,
                    "DOMAIN_URL": DOMAIN_URL,
                },
            )

    @action(detail=False, methods=["GET"])
    def logout(self, request, *args, **kwargs):
        logout(request)
        return render(request, "login.html", {"DOMAIN_URL": DOMAIN_URL})

    @action(detail=False, methods=["get"], name="See Profile")
    def profile_form(self, request, *args, **kwargs):
        user = request.user
        return render(
            request,
            "profilePage.html",
            {
                "owner": user.first_name + " " + user.last_name,
                "DOMAIN_URL": DOMAIN_URL,
            },
        )

    @action(detail=False, methods=["post"], name="Update Profile")
    def profile_update_request(self, request, *args, **kwargs):
        user = request.user
        data = request.data
        if request.data["first_name"]:
            user.first_name = request.data["first_name"]
            user.save()
        if request.data["last_name"]:
            user.last_name = request.data["last_name"]
            user.save()
        return render(
            request,
            "profilePage.html",
            {
                "owner": user.first_name + " " + user.last_name,
                "DOMAIN_URL": DOMAIN_URL,
            },
        )

    @action(detail=False, methods=["get"], name="Reset Password")
    def reset_password_form(self, request, *args, **kwargs):
        return render(request, "resetPasswordRequest.html", {"DOMAIN_URL": DOMAIN_URL})

    @action(detail=False, methods=["post"], name="Reset Password")
    def reset_password_request(self, request, *args, **kwargs):
        data = request.data
        email = data.get("email")
        code = uuid.uuid4()
        ResetPassword.objects.create(email=email, code=code)
        sendEmail(email, code)
        # return Response({"detail": "The code for resetting password is sent to your email address."})
        return render(request, "resetPassword.html", {"DOMAIN_URL": DOMAIN_URL})

    @action(detail=False, methods=["post"], name="Reset Password")
    def reset_password(self, request, *args, **kwargs):
        data = request.data
        print(request.data)
        email = data.get("email")
        code = data.get("code")
        user = User.objects.get(email=email)
        reset_password_obj = ResetPassword.objects.filter(email=email).first()
        if reset_password_obj:
            if reset_password_obj.code == code:
                if data["password"] != data["password2"]:
                    raise ValidationError({"error": "New passwords do not match"})
                else:
                    user.set_password(data["password"])
                    user.save()
                    reset_password_obj.delete()
                    # return Response({"detail": "Password is reset successfully"})
                    return render(request, "login.html", {"DOMAIN_URL": DOMAIN_URL})

            # return Response({"detail": "Incorrect Reset Code"})
            args = {}
            args["error"] = "Incorrect Reset Code."
            args["DOMAIN_URL"] = DOMAIN_URL
            return render(request, "error.html", args)

        # return Response({"detail": "Incorrect Credentials"})
        args = {}
        args["error"] = "Incorrect Credentials."
        args["DOMAIN_URL"] = DOMAIN_URL
        return render(request, "error.html", args)

    @action(detail=False, methods=["get"], name="Change Password Form")
    def change_password_form(self, request, pk=None):
        user = request.user
        return render(
            request,
            "changePassword.html",
            {
                "owner": user.first_name + " " + user.last_name,
                "DOMAIN_URL": DOMAIN_URL,
            },
        )

    @action(detail=False, methods=["post"], name="Change Password")
    def change_password_request(self, request, pk=None):
        data = request.data
        user = request.user
        if user is None:
            args = {}
            args["error"] = "There is no such user"
            args["DOMAIN_URL"] = DOMAIN_URL
            args["owner"] = user.first_name + " " + user.last_name

            return render(request, "changePasswordError.html", args)

        if user.check_password(data["old_password"]) == False:
            args = {}
            args["error"] = "The old password does not match"
            args["DOMAIN_URL"] = DOMAIN_URL
            args["owner"] = user.first_name + " " + user.last_name

            return render(request, "changePasswordError.html", args)

        if data["password"] != data["password2"]:
            args = {}
            args["error"] = "New passwords do not match"
            args["owner"] = user.first_name + " " + user.last_name
            args["DOMAIN_URL"] = DOMAIN_URL
            return render(request, "changePasswordError.html", args)

        user.set_password(data["password"])
        user.save()
        login(request, user)
        return render(
            request,
            "changePassword.html",
            {
                "owner": user.first_name + " " + user.last_name,
                "DOMAIN_URL": DOMAIN_URL,
            },
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)

        return Response("Deleted successfully", status=200)

    def get_serializer_class(self):
        if self.action == "create":
            return UserRegisterSerializer
        else:
            return UserListSerializer
