from django.db.models import (
    Count,
    Max,
    F,
    Q,
    Subquery,
    OuterRef,
)
from .models import User, Blog, Comment, Like, Notifications


def exercise_1_total_blogs():
    result = Blog.objects.aggregate(total=Count("id"))
    print(f"Total blogs: {result}")
    return result


def exercise_2_most_recent_blog():
    result = Blog.objects.aggregate(latest=Max("publish_date"))
    print(f"Latest blog date: {result}")
    return result


def exercise_3_total_likes():
    result = Like.objects.aggregate(total=Count("id"))
    print(f"Total likes: {result}")
    return result


def exercise_4_total_comments():
    result = Comment.objects.aggregate(total=Count("id"))
    print(f"[Ex 4] Total comments: {result}")
    return result


def exercise_5_blogs_with_like_count():
    blogs = Blog.objects.annotate(like_count=Count("likes"))
    for blog in blogs:
        print(f"Blog: {blog.title} | Likes: {blog.like_count}")
    return blogs


def exercise_6_blogs_ordered_by_likes():
    blogs = Blog.objects.annotate(
        like_count=Count("likes"), comment_count=Count("comments")
    ).order_by("-like_count")
    for blog in blogs:
        print(
            f"Blog: {blog.title} | Likes: {blog.like_count} | Comments: {blog.comment_count}"
        )
    return blogs


def exercise_8_users_with_blog_count():
    users = User.objects.annotate(blog_count=Count("blogs")).order_by("-blog_count")
    for user in users:
        print(f"User: {user.username} | Blogs: {user.blog_count}")
    return users


def exercise_9_blogs_per_user():
    result = Blog.objects.values("user__username").annotate(blog_count=Count("id"))
    for row in result:
        print(f"User: {row['user__username']} | Blogs: {row['blog_count']}")
    return result


def exercise_10_top_3_authors():
    result = User.objects.annotate(blog_count=Count("blogs")).order_by("-blog_count")[
        :3
    ]
    for user in result:
        print(f"User: {user.username} | Blogs: {user.blog_count}")
    return result


def exercise_11_likes_per_blog():
    result = Like.objects.values("blog__title").annotate(like_count=Count("id"))
    for row in result:
        print(f"Blog: {row['blog__title']} | Likes: {row['like_count']}")
    return result


def exercise_12_comments_per_blog():
    result = Comment.objects.values("blog__title").annotate(
        comment_count=Count("id")
    )  # .values() is used for groupby
    for row in result:
        print(f"Blog: {row['blog__title']} | Comments: {row['comment_count']}")
    return result


def exercise_13_mark_all_notifications_as_read():
    count = Notifications.objects.update(is_read=True)
    print(f"Updated {count} notifications")
    return count


def exercise_14_search_title_or_content():
    result = Blog.objects.filter(
        Q(title__icontains="hello") | Q(content__icontains="by")
    )
    for blog in result:
        print(f"Blog: {blog.title} | Content: {blog.content}")
    return result


def exercise_15_select_related_user():
    blogs = Blog.objects.select_related("user")
    for blog in blogs:
        print(f"Blog: {blog.title} | User: {blog.user.username}")
    return blogs


def exercise_16_latest_blog_per_user():
    latest_blog = (
        Blog.objects.filter(user=OuterRef("id"))
        .order_by("-publish_date")
        .values("title")[:1]
    )

    users = User.objects.annotate(latest_blog_title=Subquery(latest_blog))
    for user in users:
        print(f"User: {user.username} | Latest blog: {user.latest_blog_title}")
    return users


def exercise_17_blog_latest_comment_content():
    latest_comment = (
        Comment.objects.filter(blog=OuterRef("id"))
        .order_by("-created_at")
        .values("content")[:1]
    )

    blogs = Blog.objects.annotate(latest_comment_content=Subquery(latest_comment))
    for blog in blogs:
        print(f"Blog: {blog.title} | Latest comment: {blog.latest_comment_content}")
    return blogs


def exercise_18_blogs_with_author():
    blogs = Blog.objects.select_related("user").all()
    for blog in blogs:
        print(f"Blog: '{blog.title}' | Author: {blog.user.email}")
    return blogs


def exercise_20_blogs_with_comments():
    blogs = Blog.objects.prefetch_related("comments").all()
    for blog in blogs:
        print(f"Blog: '{blog.title}' ({blog.comments.count()} comments)")
    return blogs
