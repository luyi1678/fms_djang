from django.http import HttpResponse
from django.shortcuts import redirect


def unauthenticated_user(view_func):
    def wrapper_func(request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('Stocks:home')
        else:
            return view_func(request, *args, **kwargs)

    return wrapper_func


def allowed_users(allowed_roles=[]):
    def decorator(view_func):
        def wrapper_func(request, *args, **kwargs):
            username = request.user.username
            if username in allowed_roles:
                return view_func(request, *args, **kwargs)
            else:
                return HttpResponse("permission needed")

        return wrapper_func

    return decorator


def admin_only(view_func):
    def wrapper_function(request, *args, **kwargs):
        group = None
        if request.user.groups.exists():
            group = request.user.groups.all()[0].name
            if group == 'admin':
                return view_func(request, *args, **kwargs)
            else:
                return redirect('/Stocks')
        else:
            return redirect('/Stocks')
    return wrapper_function


