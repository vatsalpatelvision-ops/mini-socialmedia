from django.shortcuts import render
from .models import User,Blog,Comment,Like
from .jwt_serializer import CustomTokenSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import RegisterSerializer , CommentSerializer ,LikeSerializer, BlogSerializer
from datetime import datetime
from rest_framework.viewsets import ModelViewSet
from .permissions import IsOwnerOrReadOnly
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page


from django.http import JsonResponse

from django.core.cache import cache


# Create your views here.
class EmailRegisterView(APIView):
    def post(self,request):
        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User created"}, status=201)
        return Response(serializer.errors, status=400)

class EmailLoginView(TokenObtainPairView):
    serializer_class = CustomTokenSerializer

class BlogViewSet(ModelViewSet):
    serializer_class = BlogSerializer
    permission_classes = [IsAuthenticated,IsOwnerOrReadOnly]

    def get_permissions(self):
        if self.action == 'toggle_like':
            return [IsAuthenticated()]
        return [IsOwnerOrReadOnly()]

    def get_queryset(self):
        user = self.request.user
        queryset = Blog.objects.all()


        my_post = self.request.query_params.get('my_post')

        if my_post == 'true':
            queryset = queryset.filter(user=user)

        return queryset
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    
    @action(detail=True, methods=['post'], url_path='toggle-like')
    def toggle_like(self,request, pk=None):
        blog = self.get_object()
        user = request.user

        like , created = Like.objects.get_or_create(user = user, blog = blog)
        if not created:
            like.delete()
            return Response ({'status' : 'unliked'})
        
        return Response({'status':'liked'})

class CommentViewSet(ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        queryset = Comment.objects.all()

        blog_id = self.request.query_params.get('blog')

        if blog_id:
            queryset = queryset.filter(blog_id=blog_id)

        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

class BlogListView(APIView):

    @method_decorator(cache_page(60 * 5))  # cache for 5 minutes
    def get(self, request):
        data = {
            "time": datetime.now().strftime("%H:%M:%S"),
            "data": [
                {"id": 1, "title": "Post 1"},
                {"id": 2, "title": "Post 2"},
            ]
        }
        return Response(data)
    

def blog_list(request):
    data = cache.get("blog_list")

    if not data:
        print("From db")
        data = ["blog1" , "blog2", "blog3"]
        cache.set("blog_list",data,timeout=60)

    return JsonResponse({"data": data})


from django.http import JsonResponse
from .tasks import send_email_welcome

def register_user(request):
    user_email = "test@gmail.com"  
    send_email_welcome.delay(user_email)

    return JsonResponse({"message": "User registered successfully"})

