from django.shortcuts import render
from .models import User,Blog,Comment,Like
from .jwt_serializer import CustomTokenSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import RegisterSerializer , CommentSerializer ,LikeSerializer, BlogSerializer

from rest_framework.viewsets import ModelViewSet
from .permissions import IsOwnerOrReadOnly
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

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
    permission_classes = [IsOwnerOrReadOnly]

    def get_permissions(self):
        if self.action == 'toggle_like':
            return [IsAuthenticated()]
        return [IsOwnerOrReadOnly()]

    def get_queryset(self):
        user = self.request.user

        if user.is_staff:
            return Blog.objects.all()
        
        return Blog.objects.all()
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=False, methods=['get'], url_path='my-post')
    def my_post(self, request):
        queryset = Blog.objects.filter(user=request.user)
        serializer = self.get_serializer(queryset , many=True)
        return Response(serializer.data)
    
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
        user = self.request.user
    
        if user.is_staff:
            return Comment.objects.all() 

        blog_id = self.request.query_params.get('blog')

        if blog_id:
            queryset = queryset.filter(blog_id=blog_id)

        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

