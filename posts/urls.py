from django.urls import path

from . import views

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('follow/', views.FollowView.as_view(), name='follow'),
    path('<username>/follow/', views.ProfileFollowView.as_view(), name='profile_follow'),
    path('<username>/unfollow/', views.ProfileUnfollowView.as_view(), name='profile_unfollow'),
    path('new/', views.CreatePostView.as_view(), name='post_create'),
    path('group/<slug>/', views.GroupView.as_view(), name='group'),
    path('<username>/', views.ProfileView.as_view(), name='profile'),
    path('<username>/<int:post_id>/', views.ReadPostView.as_view(), name='post'),
    path('<username>/<int:post_id>/edit/', views.UpdatePostView.as_view(), name='post_update'),
    path('<username>/<int:post_id>/comment/', views.CreateCommentView.as_view(), name='add_comment')
]
