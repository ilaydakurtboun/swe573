from django.shortcuts import render
from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.status import HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.decorators import action
from .serializers import *
from .models import *
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from user.models import User


# Create your views here.

class SpaceViewSet(viewsets.ModelViewSet):
    serializer_class = SpaceCreateSerializer
    queryset = Space.objects.all()

    def create(self, request, *args, **kwargs):
        request.data._mutable = True
        user = User.objects.filter(id=request.user.id).first()
        request.data["owner"]=user
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        spaces = Space.objects.all().order_by("-id")
        # return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        return render (request, "spaces.html",{"spaces":spaces,"owner":user.first_name + " " + user.last_name})
    
    @action(detail=False, methods=['get'], name='Own Spaces')
    def own_spaces(self, request, pk=None):
        user = User.objects.filter(id=request.user.id).first()      
        spaces = Space.objects.filter(owner = user.id).order_by("-id")
        # return Response({"detail":"Liked succesfully"},status=200)   
        return render (request, "yourSpaces.html",{"spaces":spaces,"owner":user.first_name + " " + user.last_name})
        
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response("Deleted successfully",status=200)

    def list(self, request, *args, **kwargs):
        user = request.user
        if user:
            spaces = Space.objects.all().order_by("-id")
            return render (request, "spaces.html",{"spaces":spaces,"owner":user.first_name + " " + user.last_name})
        else:
            return render (request, "spaces.html",{"spaces":spaces})


    def retrieve(self, request, *args, **kwargs):
        space = self.get_object()
        data = SpaceListSerializer(space).data    
        if request.user.is_anonymous == False:
            user = request.user
            return render (request, "spacePosts.html",{"space":data,"owner":user.first_name + " " + user.last_name})
        else:
            return render (request, "mainPosts.html",{"space":data})
    
    def get_serializer_class(self, *args, **kwargs):
        if self.action == 'retrieve' or self.action == 'list':
            return SpaceListSerializer
        else:
            return SpaceCreateSerializer

    def get_permissions(self):
        if self.action == 'retrieve' or self.action=='list':
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]


class LabelViewSet(viewsets.ModelViewSet):
    serializer_class = LabelSerializer
    queryset = Label.objects.all()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response("Deleted successfully",status=200)

    def get_permissions(self):
        if self.action == 'retrive' or self.action=='list':
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]


class PostViewSet(viewsets.ModelViewSet):
    serializer_class = PostCreateSerializer
    queryset = Post.objects.all()
    paginate_by = 2
    def create(self, request, *args, **kwargs):
        request.data._mutable = True
        print(request.data)
        user = User.objects.filter(id=request.user.id).first()
        request.data["owner"]=user.id
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        # return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        posts = Post.objects.all().order_by("-id")
        return render (request, "posts.html",{"posts":posts,"owner":user.first_name + " " + user.last_name})

    @action(detail=True, methods=['get'], name='Like Post')
    def like_post(self, request, pk=None):
        user = User.objects.filter(id=request.user.id).first()      
        post = self.get_object()
        post.liked_by.add(user)
        post.save()
        posts = Post.objects.all().order_by("-id")
        # return Response({"detail":"Liked succesfully"},status=200)   
        return render (request, "posts.html",{"posts":posts,"owner":user.first_name + " " + user.last_name})

    @action(detail=False, methods=['get'], name='Liked Posts')
    def liked_posts(self, request, pk=None):
        user = User.objects.filter(id=request.user.id).first()      
        posts = Post.objects.filter(liked_by__id = user.id).order_by("-id")
        # return Response({"detail":"Liked succesfully"},status=200)   
        return render (request, "likedPosts.html",{"posts":posts,"owner":user.first_name + " " + user.last_name})

    @action(detail=False, methods=['get'], name='Liked Posts')
    def own_posts(self, request, pk=None):
        user = User.objects.filter(id=request.user.id).first()      
        posts = Post.objects.filter(owner = user.id).order_by("-id")
        # return Response({"detail":"Liked succesfully"},status=200)   
        return render (request, "yourPosts.html",{"posts":posts,"owner":user.first_name + " " + user.last_name})

    @action(detail=True, methods=['put'], name='Like Post')
    def add_label(self, request, pk=None):
        post = self.get_object()
        for label_id in request.data.get("labels"):
            label = Label.objects.get(id=label_id)
            post.label.add(label)
            post.save()
        return Response({"detail":"Added label succesfully"},status=200)   

    @action(detail=True, methods=['put'], name='Add Space')
    def add_space(self, request, pk=None):
        post = self.get_object()
        space = Space.objects.get(id=request.data.get("space"))
        post.space = space.id
        post.save()
        return Response({"detail":"Added to space succesfully"},status=200)     

    def list(self, request, *args, **kwargs):
        user = request.user
        posts = Post.objects.all().order_by("-id")
        return render (request, "posts.html",{"posts":posts,"owner":user.first_name + " " + user.last_name})

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response("Deleted successfully",status=200)

    def get_serializer_class(self, *args, **kwargs):
        if self.action == 'retrieve' or self.action == 'list':
            return PostListSerializer
        else:
            return PostCreateSerializer

    def get_permissions(self):
        if self.action == 'retrive' or self.action=='list':
            permission_classes = [AllowAny]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]
