from django.urls import path , include
from . import views
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView


router = DefaultRouter()
router.register("blog",views.BlogViewSet , basename='blog')
router.register("comment",views.CommentViewSet , basename='comment')
router.register("cacheblog", views.CacheBlogViewSet, basename='cacheblog')

urlpatterns = [
    path('register/', views.EmailRegisterView.as_view()),
    path('login/', views.EmailLoginView.as_view()),
    path('roken/refresh/', TokenRefreshView.as_view()),
    path('bloglistview/', views.BlogListView.as_view()),
    path("", include(router.urls)),
    # path('run/' , views.run_task),
    path('register-email/' , views.register_user),
]