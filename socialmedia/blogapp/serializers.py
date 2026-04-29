from rest_framework import serializers
from .models import Comment , Blog, User, Like

class RegisterSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email','username','password']
        extra_kwargs = {
            'password':{'write_only' : True}
        }

    def create(self , validated_data):
        return User.objects.create_user(**validated_data)
    


class SimpleUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username']

class CommentSerializer(serializers.ModelSerializer):
    user = SimpleUserSerializer(read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'content', 'user', 'created_at']
        read_only_fields = ['user', 'created_at']


class LikeSerializer(serializers.ModelSerializer):
    user = SimpleUserSerializer(read_only=True)

    class Meta:
        model = Like
        fields = ['id', 'user', 'blog', 'created_at']
        read_only_fields = ['user', 'created_at']

class BlogSerializer(serializers.ModelSerializer):
    user = SimpleUserSerializer(read_only=True)
    comments = CommentSerializer(many=True, read_only=True)

    like_count = serializers.SerializerMethodField()

    class Meta:
        model = Blog
        fields = [
            'id',
            'title',
            'content',
            'publish_date',
            'user',
            'comments',
            'like_count'
        ]
        read_only_fields = ['user', 'publish_date']

    def get_like_count(self, obj):
        return obj.likes.count()