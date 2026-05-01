from django.db.models import Count, Max, Min
from .models import User, Blog, Comment, Like
from .jwt_serializer import CustomTokenSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import (
    RegisterSerializer,
    CommentSerializer,
    LikeSerializer,
    BlogSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
)
from datetime import datetime
from rest_framework.viewsets import ModelViewSet
from .permissions import IsOwnerOrReadOnly
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated

from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page

from django.http import JsonResponse

from django.core.cache import cache
from .tasks import clear_blog_cache

# email setup
from django.conf import settings
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.contrib.auth import get_user_model
from django.core.mail import send_mail

from rest_framework.throttling import AnonRateThrottle, UserRateThrottle
# Create your views here.

class LoginThrottle(AnonRateThrottle):
    rate = '5/minute'


class EmailRegisterView(APIView):
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response({"message": "User created"}, status=201)
        return Response(serializer.errors, status=400)


class EmailLoginView(TokenObtainPairView):
    serializer_class = CustomTokenSerializer
    throttle_classes = [LoginThrottle]


class BlogViewSet(ModelViewSet):
    serializer_class = BlogSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def get_permissions(self):
        if self.action == "toggle_like":
            return [IsAuthenticated()]
        return [IsOwnerOrReadOnly()]

    def get_queryset(self):
        user = self.request.user
        queryset = Blog.objects.all()

        my_post = self.request.query_params.get("my_post")

        if my_post == "true":
            queryset = queryset.filter(user=user)

        return queryset

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=["post"], url_path="toggle-like")
    def toggle_like(self, request, pk=None):
        blog = self.get_object()
        user = request.user

        like, created = Like.objects.get_or_create(user=user, blog=blog)
        if not created:
            like.delete()
            return Response({"status": "unliked"})

        return Response({"status": "liked"})


class CommentViewSet(ModelViewSet):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        queryset = Comment.objects.all()

        blog_id = self.request.query_params.get("blog")

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
            ],
        }
        return Response(data)


def blog_list(request):
    data = cache.get("blog_list")

    if not data:
        print("From db")
        data = ["blog1", "blog2", "blog3"]
        cache.set("blog_list", data, timeout=60)

    return JsonResponse({"data": data})


class CacheBlogViewSet(ModelViewSet):
    serializer_class = BlogSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def get_permissions(self):
        if self.action == "toggle_like":
            return [IsAuthenticated()]
        return [IsOwnerOrReadOnly()]

    def get_queryset(self):
        user = self.request.user
        queryset = Blog.objects.all()

        my_post = self.request.query_params.get("my_post")

        if my_post == "true":
            queryset = queryset.filter(user=user)

        return queryset

    def _clear_cache(self):
        cache.delete("cached_blog_list")

    def list(self, request, *args, **kwargs):
        cache_key = "cached_blog_list"
        cached = cache.get(cache_key)
        if cached is not None:
            return Response(cached)

        res = super().list(request, *args, **kwargs)
        cache.set(cache_key, res.data, timeout=60 * 2)

        print(datetime.now().strftime("%H:%M:%S"))
        return res

    def retrieve(self, request, *args, **kwargs):
        blog_id = kwargs.get("pk")
        cache_key = f"cached_blog_detail_{blog_id}"
        cached = cache.get(cache_key)
        if cached is not None:
            return Response(cached)

        res = super().retrieve(request, *args, **kwargs)
        cache.set(cache_key, res.data, timeout=60 * 5)
        return res

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
        clear_blog_cache.delay()

    def perform_update(self, serializer):
        blog_id = self.kwargs["pk"]
        super().perform_update(serializer)
        clear_blog_cache.delay(blog_id)

    def perform_destroy(self, instance):
        blog_id = instance.id
        print(blog_id)

        super().perform_destroy(instance)
        clear_blog_cache.delay(blog_id)

    @action(detail=True, methods=["post"], url_path="toggle-like")
    def toggle_like(self, request, pk=None):
        blog = self.get_object()
        user = request.user
        print(pk)
        like, created = Like.objects.get_or_create(user=user, blog=blog)
        if not created:
            like.delete()
            clear_blog_cache.delay(pk)

            return Response({"status": "unliked"})

        clear_blog_cache.delay(pk)

        return Response({"status": "liked"})


class PracticeAggregationsView(APIView):
    def get(self, request):
        total_blogs = Blog.objects.aggregate(total=Count("id"))

        total_comments = Comment.objects.aggregate(total=Count("id"))

        latest_blog = Blog.objects.aggregate(latest=Max("publish_date"))

        earliest_blog = Blog.objects.aggregate(earliest=Min("publish_date"))

        # comments_per_blog
        comments_per_blog = Blog.objects.annotate(  # noqa: F841
            comment_count=Count("comments__id")
        ).values("title", "comment_count")

        # using blog manager
        blog_today = Blog.objects.today()
        serializer = BlogSerializer(blog_today, many=True)

        blog_recent = Blog.objects.recent()
        recent_serializer = BlogSerializer(blog_recent, many=True)

        blog_by_user = Blog.objects.filter(user=self.request.user)
        user_blog_serializer = BlogSerializer(blog_by_user, many=True)

        return Response(
            {
                # '1_count_total_blogs': total_blogs,
                # '2_count_total_comments': total_comments,
                # '3_max_latest_blog': latest_blog,
                # '4_min_earliest_blog': earliest_blog,
                # '5_comments_per_blog': comments_per_blog,
                "6_blog_today": serializer.data,
                "7_blog_recent": recent_serializer.data,
                "8_blog_by_user": user_blog_serializer.data,
            }
        )

class PasswordResetThrottle(UserRateThrottle):
    rate = '3/hour'


class PasswordResetRequestView(APIView):
    throttle_classes = [PasswordResetThrottle]
    def post(self, request):

        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        User = get_user_model()

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response(
                {
                    "message": "Account does not exists",
                },
                status=status.HTTP_200_OK,
            )

        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        email_body = (
            f"Password Reset Request\n\n"
            f"Use the following details to reset your password:\n\n"
            f"uidb64: {uidb64}\n"
            f"token: {token}\n\n"
            f"Send these values to the password-reset-confirm endpoint with your new password.\n"
            f"This token will expire in 3 days."
        )

        send_mail(
            subject="Password Reset Request",
            message=email_body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
            fail_silently=False,
        )

        return Response(
            {"message": "A reset link has been sent"},
            status=status.HTTP_200_OK,
        )


class PasswordResetConfirmView(APIView):
    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {"message": "Password reset successful"},
            status=status.HTTP_200_OK,
        )
