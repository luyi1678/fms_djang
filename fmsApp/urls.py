from django.contrib import admin
from django.urls import path
from django.conf.urls.static import static
from . import views
from django.contrib.auth import views as auth_views
from django.views.generic.base import RedirectView
from .views import LoginUser

urlpatterns = [
    path('redirect-admin', RedirectView.as_view(url="/admin"),name="redirect-admin"),
    path('login',auth_views.LoginView.as_view(template_name="login.html",redirect_authenticated_user = True),name='login'),
    path('userlogin', views.login_user, name="login-user"),
    path('user-register', views.registerUser, name="register-user"),
    path('logout',views.logoutuser,name='logout'),
    path('profile',views.profile,name='profile'),
    path('update-profile',views.update_profile,name='update-profile'),
    # path('update-avatar',views.update_avatar,name='update-avatar'),
    path('update-password',views.update_password,name='update-password'),
    path('', views.home, name='home-page'),
    path('my_posts', views.posts_mgt, name='posts-page'),
    path('manage_post', views.manage_post, name='manage-post'),
    path('manage_post/<int:pk>', views.manage_post, name='manage-post'),
    path('save_post', views.save_post, name='save-post'),
    path('edit_post', views.edit_post, name='edit-post'),
    path('edit_post/<int:pk>', views.edit_post, name='edit-post'),
    path('edit_save', views.edit_save, name='edit-save'),
    path('delete_post', views.delete_post, name='delete-post'),
    path(r'shareF/<str:id>', views.shareF, name='share-file-id'),
    path('shareF/', views.shareF, name='share-file'),
    path('preview/my_posts?<int:pk>', views.preview, name='preview'),
    path('upload_img', views.upload_img, name='upload-img'),
    path('mold_posts', views.mold_posts, name='mold-posts'),
    path('directory-view', views.directory_view, name='directory-view'),
    path('directory-tree', views.directory_tree, name='directory-tree'),
    # DRF integration
    path('api/login', LoginUser.as_view(), name="api-login")

]
