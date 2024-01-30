from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from fms_django.settings import MEDIA_ROOT, MEDIA_URL
import json
from django.contrib import messages
from django.contrib.auth.models import User
from django.http import HttpResponse, FileResponse, Http404, JsonResponse
from fmsApp.forms import UserRegistration, SavePost, UpdateProfile, UpdatePasswords,FilterForm
from fmsApp.models import Post
from cryptography.fernet import Fernet
from django.conf import settings
import base64
from .models import *
import os
from datetime import datetime
import mimetypes
from io import BytesIO
# from xhtml2pdf import pisa
from django.template.loader import get_template
from .filters import *
import shutil
from .decorators import unauthenticated_user, allowed_users, admin_only
from django.core.files.storage import FileSystemStorage
from urllib.parse import unquote
from django.core.paginator import Paginator  # import Paginator
from rest_framework.views import APIView
from rest_framework.response import Response

# Create your views here.

context = {
    'page_title': 'File Management System',
}


class LoginUser(APIView):
    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user is not None and user.is_active:
            login(request, user)
            return Response({'status': 'success'})
        return Response({'status':'failed', 'msg':'Incorrect username or password'})



# login
def login_user(request):
    logout(request)
    resp = {"status": 'failed', 'msg': ''}
    username = ''
    password = ''
    if request.POST:
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                resp['status'] = 'success'
            else:
                resp['msg'] = "Incorrect username or password"
        else:
            resp['msg'] = "Incorrect username or password"
    return HttpResponse(json.dumps(resp), content_type='application/json')


# Logout
def logoutuser(request):
    logout(request)
    return redirect('/')


@login_required
def home(request):
    context['page_title'] = 'Home'
    if request.user.is_superuser:
        posts = Post.objects.all().order_by("id")
        myFilter = AdminFilter(request.GET, queryset=posts)
    else:
        posts = Post.objects.filter(user=request.user).all().order_by("id")
        myFilter = UserFilter(request.GET, queryset=posts,user=request.user)
    posts = myFilter.qs
    context['posts'] = posts
    context['postsLen'] = posts.count()
    context['myFilter'] = myFilter
    print(request.build_absolute_uri())
    return render(request, 'home.html', context)


def registerUser(request):
    user = request.user
    if user.is_authenticated:
        return redirect('home-page')
    context['page_title'] = "Register User"
    if request.method == 'POST':
        data = request.POST
        form = UserRegistration(data)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            pwd = form.cleaned_data.get('password1')
            loginUser = authenticate(username=username, password=pwd)
            login(request, loginUser)
            form = UserRegistration()
            return redirect('home-page')
        else:
            context['reg_form'] = form

    return render(request, 'register.html', context)


@login_required
def profile(request):
    context['page_title'] = 'Profile'
    return render(request, 'profile.html', context)


@login_required
def posts_mgt(request):
    context['page_title'] = 'Uploads'
    if request.user.is_superuser:
        posts = Post.objects.all().order_by('title', '-date_created').all()
        myFilter = AdminFilter(request.GET, queryset=posts)
    else:
        posts = Post.objects.filter(user=request.user).order_by('title', '-date_created').all()
        myFilter = UserFilter(request.GET, queryset=posts,user=request.user)

    # posts = Post.objects.filter(user=request.user).order_by('title', '-date_created').all()
    # myFilter = PostFilter(request.GET, queryset=posts)
    posts = myFilter.qs
    context['posts'] = posts
    context['myFilter'] = myFilter
    return render(request, 'posts_mgt.html', context)


@login_required
@allowed_users(allowed_roles=['luyi1','ww','100017','zyh216077','老穆','靖'])
def manage_post(request, pk=None):
    context['page_title'] = 'Manage Post'
    context['post'] = {}
    context['categories'] = Category.objects.all()
    context['moulds'] = Mould.objects.all()
    context['machines'] = Machine.objects.all()
    context['materials'] = Material.objects.all()
    if not pk is None:
        post = Post.objects.get(id=pk)
        context['post'] = post
    return render(request, 'manage_post.html', context)


@login_required
def upload_img(request):
    resp = {'status': 'failed', 'msg': ''}
    if request.method == 'POST':
        user = request.user
        mould = request.POST.get("mould_new")
        date = request.POST.get("date")
        files = request.FILES.getlist('files')
        print(len(files))
        # print(files[0].name)
        save_path = request.POST.get("savePath")
        root_dir = "Z:\\"
        upload_dir = os.path.join(root_dir, save_path, user.username, mould, date)
        print(upload_dir)
        os.makedirs(upload_dir, exist_ok=True)
        print("upload_dir before for loop:", upload_dir)
        for file in files:
            print('file_name:', file.name)
            upload_path = os.path.join(upload_dir, file.name)
            print(upload_path)
            with open(upload_path, 'wb') as f:
                for chunk in file.chunks():
                    f.write(chunk)
        messages.success(request, 'File has been saved successfully.')
        resp['status'] = 'success'
        return redirect('/my_posts')
    else:
        resp['msg'] = "No Data sent."
        return render(request, 'upload_img.html')


@login_required
@allowed_users(allowed_roles=['luyi1', 'ww', '100017', 'zyh216077', '老穆', '靖'])
def save_post(request):
    resp = {'status': 'failed', 'msg': ''}
    if request.method == 'POST':
        if not request.POST['id'] == '':
            post = Post.objects.get(id=request.POST['id'])
            form = SavePost(request.POST, request.FILES, instance=post)

        else:
            form = SavePost(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)

            #Update date
            if request.POST.get('date'):
                date = request.POST.get('date')
            else:
                date = datetime.today()

            # Update category information
            category_id = request.POST.get('category_id')
            category_new = request.POST.get('category_new')
            if category_id:
                category = Category.objects.get(pk=category_id)
                post.category = category
            elif category_new:
                category, created = Category.objects.get_or_create(name=category_new)
                post.category = category

            # Update mould information
            mould_id = request.POST.get('mould_id')
            mould_new = request.POST.get('mould_new')
            if mould_id:
                mould = Mould.objects.get(pk=mould_id)
                post.mould = mould
            elif mould_new:
                mould, created = Mould.objects.get_or_create(name=mould_new)
                post.mould = mould

            # Update machine information
            machine_id = request.POST.get('machine_id')
            mac_new_loc = request.POST.get('mac_new_loc')
            mac_new_sn = request.POST.get('mac_new_sn')
            if machine_id:
                machine = Machine.objects.get(pk=machine_id)
                post.machine = machine
            elif mac_new_loc and mac_new_sn:
                machine, created = Machine.objects.get_or_create(location=mac_new_loc, seri_numer=mac_new_sn)
                post.machine = machine

            # Update material information
            material_id = request.POST.get('material_id')
            material_new_name = request.POST.get('material_new_name')
            material_new_grade = request.POST.get('material_new_grade')
            material_new_manu = request.POST.get('material_new_manu')
            if material_id:
                material = Material.objects.get(pk=material_id)
                post.material = material
            elif material_new_name and material_new_grade and material_new_manu:
                material, created = Material.objects.get_or_create(
                    name=material_new_name,
                    grade=material_new_grade,
                    manufacturer=material_new_manu,
                )
                post.material = material
            # post.save()
            # form.save()
            post = form.save(commit=False)

            # Generate the target directory
            user = request.user
            temp_dir = user.username + '/'
            if post.mould:
            # if mould_id or mould_new:
                temp_dir += (post.mould.name + '/')
            if 'date' in request.POST:
                try:
                    date = datetime.strptime(request.POST['date'], '%Y-%m-%d')
                    temp_dir += date.strftime('%Y-%m-%d') + '/'
                except:
                    pass
            if post.category:
                # if category_id or category_new:
                temp_dir += (post.category.name + '/')

            print(temp_dir)

            files = request.FILES.getlist('file_paths')
            print(len(files))
            target_dir = os.path.join(settings.MEDIA_ROOT, temp_dir)
            os.makedirs(target_dir, exist_ok=True)

            upload_dir = ""
            print("前端按钮值：",request.POST.get("saveOptions"))
            if request.POST.get("saveOptions") == "Lan":
                print("前端路径：", request.POST.get("savePath") !="" )
                if request.POST.get("savePath") != "":
                    root_dir = "Z:\\"
                    save_path = request.POST.get("savePath")
                    upload_dir = os.path.join(root_dir, save_path, temp_dir)
                    os.makedirs(upload_dir, exist_ok=True)
                    print("upload_dir before for loop:", upload_dir)

            for file in files:
                print(file.name)
                target_path = os.path.join(target_dir, file.name)
                print("before", post.file_path)
                post.file_path = target_path
                print("after", post.file_path)
                print(target_path)
                with open(target_path, 'wb') as f:
                    for chunk in file.chunks():
                        f.write(chunk)
                Post.objects.create(
                    user=user,
                    title=request.POST.get('title'),
                    description=request.POST.get('description'),
                    category=post.category,
                    mould=post.mould,
                    machine=post.machine,
                    date=date,
                    material=post.material,
                    file_path=post.file_path,
                )

                if upload_dir != "":
                    upload_path = os.path.join(upload_dir, file.name)
                    with open(upload_path, 'wb') as f:
                        for chunk in file.chunks():
                            f.write(chunk)

            # form.save()
            print("last", post.file_path)
            messages.success(request, 'File has been saved successfully.')
            resp['status'] = 'success'
            print(machine_id, mac_new_loc, mac_new_sn)
        else:
            for fields in form:
                for error in fields.errors:
                    resp['msg'] += str(error + '<br/>')
            form = SavePost(request.POST, request.FILES)
            print(form.errors)
            print(form.cleaned_data)

    else:
        resp['msg'] = "No Data sent."
    print(resp)
    return HttpResponse(json.dumps(resp), content_type="application/json")


@login_required
def edit_post(request, pk=None):
    context['page_title'] = 'Edit Post'
    context['post'] = {}
    context['categories'] = Category.objects.all()
    context['moulds'] = Mould.objects.all()
    context['machines'] = Machine.objects.all()
    context['materials'] = Material.objects.all()
    if not pk is None:
        post = Post.objects.get(id=pk)
        context['post'] = post
    return render(request, 'edit_post.html', context)


@login_required
def edit_save(request):
    resp = {'status': 'failed', 'msg': ''}
    if request.method == 'POST':
        post = get_object_or_404(Post, pk=request.POST['id'])
        form = SavePost(request.POST, request.FILES, instance=post)
        full_file_path_before = post.file_path.name
        file_path_before = post.file_path
        file_before = post.file_path.file
        file_name_before = os.path.basename(full_file_path_before)
        dir_before = os.path.dirname(post.file_path.path)
        print("file_path_before",file_path_before)


        if form.is_valid():
            post = form.save(commit=False)
            print(post.file_path)

            # Update category information
            category_id = request.POST.get('category_id')
            category_new = request.POST.get('category_new')
            if category_id:
                category = Category.objects.get(pk=category_id)
                post.category = category
            elif category_new:
                category, created = Category.objects.get_or_create(name=category_new)
                post.category = category

            # Update mould information
            mould_id = request.POST.get('mould_id')
            mould_new = request.POST.get('mould_new')
            if mould_id:
                mould = Mould.objects.get(pk=mould_id)
                post.mould = mould
            elif mould_new:
                mould, created = Mould.objects.get_or_create(name=mould_new)
                post.mould = mould

            # Update machine information
            machine_id = request.POST.get('machine_id')
            mac_new_loc = request.POST.get('mac_new_loc')
            mac_new_sn = request.POST.get('mac_new_sn')
            if machine_id:
                machine = Machine.objects.get(pk=machine_id)
                post.machine = machine
            elif mac_new_loc and mac_new_sn:
                machine, created = Machine.objects.get_or_create(location=mac_new_loc, seri_numer=mac_new_sn)
                post.machine = machine

            # Update material information
            material_id = request.POST.get('material_id')
            material_new_name = request.POST.get('material_new_name')
            material_new_grade = request.POST.get('material_new_grade')
            material_new_manu = request.POST.get('material_new_manu')
            if material_id:
                material = Material.objects.get(pk=material_id)
                post.material = material
            elif material_new_name and material_new_grade and material_new_manu:
                material, created = Material.objects.get_or_create(
                    name=material_new_name,
                    grade=material_new_grade,
                    manufacturer=material_new_manu,
                )
                post.material = material
            # post.save()
            # form.save()
            # post = form.save()

            # Generate the target directory
            user = request.user
            target_dir = user.username + '/'
            if post.mould:
                # if mould_id or mould_new:
                target_dir += (post.mould.name + '/')
            if 'date' in request.POST:
                try:
                    date = datetime.strptime(request.POST['date'], '%Y-%m-%d')
                    target_dir += date.strftime('%Y-%m-%d') + '/'
                except:
                    pass
            if post.category:
                # if category_id or category_new:
                target_dir += (post.category.name + '/')

            uploaded_file = request.FILES.get('file_path')
            print("uploaded_file",uploaded_file)
            print("pk", request.POST['id'])
            target_dir = os.path.join(settings.MEDIA_ROOT, target_dir)

            if uploaded_file:
                uploaded_file_name = os.path.basename(uploaded_file.name)
                print('uploaded_file_name',uploaded_file_name)
                if (uploaded_file_name != file_name_before) or (target_dir != dir_before):
                    file_path_before.close() # 必须要手动关闭之前的文件，否则会报permissionError
                    # file_path_before.delete(save=False)
                    target_path = os.path.join(target_dir, uploaded_file_name)
                    print("before", full_file_path_before)
                    post.file_path = target_path
                    os.makedirs(target_dir, exist_ok=True)
                    with open(target_path, 'wb') as f:
                        for chunk in uploaded_file.chunks():
                            f.write(chunk)
                    post.save()
                    print("after", post.file_path)
                    # form.save()
                    messages.success(request, 'File has been saved successfully.')
                    resp['status'] = 'success'
                else:
                    post.save()
                    # form.save()
            else:
                if target_dir != dir_before:
                    print('dir_before', dir_before)
                    print('target_dir', target_dir)
                    print('file_name_before',file_name_before)
                    target_path = os.path.join(target_dir, file_name_before)
                    print("before", post.file_path)
                    post.file_path = target_path
                    print("after", post.file_path)
                    os.makedirs(target_dir, exist_ok=True)
                    file_before.close()
                    shutil.move(file_path_before.path, target_path)
                    post.save()
                    # form.save()
                    # file_path_before.delete()
                else:
                    post.save()
                    # form.save()

                print("last", post.file_path)
                messages.success(request, 'File has been saved successfully.')
                resp['status'] = 'success'
                print(machine_id, mac_new_loc, mac_new_sn)

        else:
            for fields in form:
                for error in fields.errors:
                    resp['msg'] += str(error + '<br/>')
            form = SavePost(request.POST, request.FILES)
            print(form.errors)
            print(form.cleaned_data)
    else:
        resp['msg'] = "No Data sent."
    print(resp)

    return HttpResponse(json.dumps(resp), content_type="application/json")
    # return HttpResponse(json.dumps({'status': 'success', 'redirect_url': reverse('posts-page')}),
    #                     content_type="application/json")


@login_required()
def preview(request, pk):
    post = Post.objects.get(id=pk)
    file_name = os.path.basename(post.file_path.name)
    file_type, encoding = mimetypes.guess_type(str(post.file_path))
    file_path = post.file_path.path
    print(file_path)
    preview_content = None
    preview_type = None

    if file_type is not None:
        print(f"File type: file_type")
        if file_type.startswith('image'):
            preview_content = post.file_path.url
            # preview_content = private_storage.url(post.file_path.name)
            preview_type = 'image'
        elif file_type == 'application/pdf':
            preview_type = 'pdf'
            preview_content = post.file_path.url
        elif file_type in (
                            'application/vnd.ms-powerpoint',
                            'application/vnd.openxmlformats-officedocument.presentationml.presentation'):
            preview_content = post.file_path.url
            preview_type = 'ppt'
        elif file_type in (
                            'application/vnd.ms-excel',
                            'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'):
            preview_content = post.file_path.url
            preview_type = 'excel'
        elif file_type.startswith('text'):
            with open(file_path, 'r') as f:
                preview_content = f.read()
            preview_type = 'text'

    context = {
        'preview_content': preview_content,
        'preview_type': preview_type,
        'file_name': file_name,
        'post': post,
    }

    return render(request, 'preview.html', context)


@login_required
def delete_post(request):
    resp = {'status': 'failed', 'msg': ''}
    if request.method == 'POST':
        try:
            post = Post.objects.get(id=request.POST['id'])
            post.delete()
            resp['status'] = 'success'
            messages.success(request, 'Post has been deleted successfully')
        except:
            resp['msg'] = "Undefined Post ID"
    return HttpResponse(json.dumps(resp), content_type="application/json")


def shareF(request, id=None):
    # print(str("b'UdhnfelTxqj3q6BbPe7H86sfQnboSBzb0irm2atoFUw='").encode())
    context['page_title'] = 'Shared File'
    if not id is None:
        key = settings.ID_ENCRYPTION_KEY
        fernet = Fernet(key)
        id = base64.urlsafe_b64decode(id)
        id = fernet.decrypt(id).decode()
        post = Post.objects.get(id=id)
        context['post'] = post
        context['page_title'] += str(" - " + post.title)

    return render(request, 'share-file.html', context)


@login_required
def update_profile(request):
    context['page_title'] = 'Update Profile'
    user = User.objects.get(id=request.user.id)
    if not request.method == 'POST':
        form = UpdateProfile(instance=user)
        context['form'] = form
        print(form)
    else:
        form = UpdateProfile(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile has been updated")
            return redirect("profile")
        else:
            context['form'] = form

    return render(request, 'manage_profile.html', context)


@login_required
def update_password(request):
    context['page_title'] = "Update Password"
    if request.method == 'POST':
        form = UpdatePasswords(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Your Account Password has been updated successfully")
            update_session_auth_hash(request, form.user)
            return redirect("profile")
        else:
            context['form'] = form
    else:
        form = UpdatePasswords(request.POST)
        context['form'] = form
    return render(request, 'update_password.html', context)


def mold_posts(request):
    if request.user.is_superuser:
        posts = Post.objects.all().order_by("id")
        myFilter = AdminFilter(request.GET, queryset=posts)
    else:
        posts = Post.objects.filter(user=request.user).all().order_by("id")
        myFilter = UserFilter(request.GET, queryset=posts,user=request.user)
    posts = myFilter.qs

    for post in posts:
        file_name = os.path.basename(post.file_path.name)
        file_type, encoding = mimetypes.guess_type(str(post.file_path))
        file_path = post.file_path.path
        post.file_name = file_name
        if file_type.startswith('image'):
            post.preview_content = post.file_path.url
            post.preview_type = 'image'
        elif file_type == 'application/pdf':
            post.preview_type = 'pdf'
            post.preview_content = post.file_path.url
        elif file_type in (
                'application/vnd.ms-powerpoint',
                'application/vnd.openxmlformats-officedocument.presentationml.presentation'):
            post.preview_content = post.file_path.url
            post.preview_type = 'ppt'
        elif file_type in (
                'application/vnd.ms-excel',
                'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'):
            post.preview_content = post.file_path.url
            post.preview_type = 'excel'
        elif file_type.startswith('text'):
            with open(file_path, 'r') as f:
                post.preview_content = f.read()
            post.preview_type = 'text'


    paginator = Paginator(posts, 1)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context2 = {
        # 'posts': posts,
        'posts': page_obj,
        'myFilter': myFilter,
        'current_url': request.build_absolute_uri(),
    }

    return render(request, 'view_selected.html', context2)


@login_required
def directory_view(request):
    # Assuming you have a function that gets the directory data
    directory_data = path_to_dict(settings.MEDIA_ROOT)
    context = {'directory_data': directory_data}
    return render(request, 'directory_view.html', context)


def create_directory(request, path):
    # Base directory (you might want to change this)
    base_dir = settings.MEDIA_ROOT

    # Construct full path
    full_path = os.path.join(base_dir, path)

    try:
        # Make directory, including all intermediate directories if not exist
        os.makedirs(full_path, exist_ok=True)
        return JsonResponse({"message": "Directory created successfully!"})
    except Exception as e:
        return JsonResponse({"error": str(e)})


def path_to_dict(path):
    d = {'name': os.path.basename(path)}
    if os.path.isdir(path):
        d['type'] = "directory"
        d['children'] = [path_to_dict(os.path.join(path,x)) for x in os.listdir(path)]
    else:
        d['type'] = "file"
    return d


def directory_tree(request):
    base_dir = settings.MEDIA_ROOT  # Replace with your desired root
    tree = path_to_dict(base_dir)
    return JsonResponse(tree)


