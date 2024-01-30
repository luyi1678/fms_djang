import django_filters
from .models import *
from django import forms


class AdminFilter(django_filters.FilterSet):
    user = django_filters.ModelChoiceFilter(queryset=User.objects.all(), empty_label='用户')
    date = django_filters.DateFilter(field_name='date', widget=forms.DateInput(attrs={'type': 'date'}))
    mould = django_filters.ModelChoiceFilter(queryset=Mould.objects.all(), empty_label='模具')
    category = django_filters.ModelChoiceFilter(queryset=Category.objects.all(), empty_label='类别')
    machine = django_filters.ModelChoiceFilter(queryset=Machine.objects.all(), empty_label='机器')
    material = django_filters.ModelChoiceFilter(queryset=Material.objects.all(), empty_label='材料')

    class Meta:
        model = Post
        fields = ['user','mould', 'date', 'category', 'machine','material']


class PostFilter(django_filters.FilterSet):
    date = django_filters.DateFilter(field_name='date', widget=forms.DateInput(attrs={'type': 'date'}))
    mould = django_filters.ModelChoiceFilter(queryset=Mould.objects.all(), empty_label='模具')
    category = django_filters.ModelChoiceFilter(queryset=Category.objects.all(), empty_label='类别')
    # category = django_filters.ModelChoiceFilter(queryset=Category.objects.all())
    machine = django_filters.ModelChoiceFilter(queryset=Machine.objects.all(), empty_label='机器')
    material = django_filters.ModelChoiceFilter(queryset=Material.objects.all(), empty_label='材料')


    class Meta:
        model = Post
        fields = ['mould', 'date', 'category', 'machine','material']


class UserFilter(django_filters.FilterSet):
    date = django_filters.DateFilter(field_name='date', widget=forms.DateInput(attrs={'type': 'date'}))
    mould = django_filters.ModelChoiceFilter(queryset=Mould.objects.none(), empty_label='模具')
    category = django_filters.ModelChoiceFilter(queryset=Category.objects.none(), empty_label='类别')
    machine = django_filters.ModelChoiceFilter(queryset=Machine.objects.none(), empty_label='机器')
    material = django_filters.ModelChoiceFilter(queryset=Material.objects.none(), empty_label='材料')

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super(UserFilter, self).__init__(*args, **kwargs)
        if user:
            self.queryset = Post.objects.filter(user=user)
            self.filters['mould'].queryset = Mould.objects.filter(post__user=user).distinct()
            self.filters['category'].queryset = Category.objects.filter(post__user=user).distinct()
            self.filters['machine'].queryset = Machine.objects.filter(post__user=user).distinct()
            self.filters['material'].queryset = Material.objects.filter(post__user=user).distinct()

    class Meta:
        model = Post
        fields = ['mould', 'date', 'category', 'machine', 'material']