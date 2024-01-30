from django import forms
from django.contrib.auth.forms import UserCreationForm,PasswordChangeForm, UserChangeForm

from markdownx.fields import MarkdownxFormField

from django.contrib.auth.models import User
from .models import *

class UserRegistration(UserCreationForm):
    email = forms.EmailField(max_length=250,help_text="The email field is required.")
    first_name = forms.CharField(max_length=250,help_text="The First Name field is required.")
    last_name = forms.CharField(max_length=250,help_text="The Last Name field is required.")

    class Meta:
        model = User
        fields = ('email', 'username', 'password1', 'password2', 'first_name', 'last_name')
    

    def clean_email(self):
        email = self.cleaned_data['email']
        try:
            user = User.objects.get(email = email)
        except Exception as e:
            return email
        raise forms.ValidationError(f"The {user.email} mail is already exists/taken")

    def clean_username(self):
        username = self.cleaned_data['username']
        try:
            user = User.objects.get(username = username)
        except Exception as e:
            return username
        raise forms.ValidationError(f"The {user.username} mail is already exists/taken")


class UpdateProfile(UserChangeForm):
    username = forms.CharField(max_length=250,help_text="The Username field is required.")
    email = forms.EmailField(max_length=250,help_text="The Email field is required.")
    first_name = forms.CharField(max_length=250,help_text="The First Name field is required.")
    last_name = forms.CharField(max_length=250,help_text="The Last Name field is required.")
    current_password = forms.CharField(max_length=250)

    class Meta:
        model = User
        fields = ('email', 'username','first_name', 'last_name')

    def clean_current_password(self):
        if not self.instance.check_password(self.cleaned_data['current_password']):
            raise forms.ValidationError(f"Password is Incorrect")

    def clean_email(self):
        email = self.cleaned_data['email']
        try:
            user = User.objects.exclude(id=self.cleaned_data['id']).get(email = email)
        except Exception as e:
            return email
        raise forms.ValidationError(f"The {user.email} mail is already exists/taken")

    def clean_username(self):
        username = self.cleaned_data['username']
        try:
            user = User.objects.exclude(id=self.cleaned_data['id']).get(username = username)
        except Exception as e:
            return username
        raise forms.ValidationError(f"The {user.username} mail is already exists/taken")

class UpdatePasswords(PasswordChangeForm):
    old_password = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control form-control-sm rounded-0'}), label="Old Password")
    new_password1 = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control form-control-sm rounded-0'}), label="New Password")
    new_password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class':'form-control form-control-sm rounded-0'}), label="Confirm New Password")
    class Meta:
        model = User
        fields = ('old_password','new_password1', 'new_password2')


class SavePost(forms.ModelForm):
    user = forms.IntegerField(help_text = "User Field is required.")
    title = forms.CharField(max_length=250,help_text = "Title Field is required.")
    description = forms.Textarea()
    date = forms.DateTimeInput()
    category = forms.ModelChoiceField(queryset=Category.objects.all(), empty_label='请选择', required=False)
    category_new = forms.CharField(max_length=250, required=False)
    mould = forms.ModelChoiceField(queryset=Mould.objects.all(), empty_label='请选择', required=False)
    mould_new = forms.CharField(max_length=250, required=False)
    machine = forms.ModelChoiceField(queryset=Machine.objects.all(), empty_label='请选择', required=False)
    mac_new_loc = forms.CharField(max_length=250, required=False)
    mac_new_sn = forms.CharField(max_length=250, required=False)
    material = forms.ModelChoiceField(queryset=Material.objects.all(),empty_label='请选择', required=False)
    material_new_name = forms.CharField(max_length=250, required=False)
    material_new_grade = forms.CharField(max_length=250, required=False)
    material_new_manu = forms.CharField(max_length=250, required=False)

    class Meta:
        model= Post
        fields = ('user','title','description','file_path','category', 'mould', 'machine','date','material')
    
    def clean_title(self):
        id = self.instance.id if not self.instance == None else 0
        try:
            if id.isnumeric():
                 post = Post.objects.exclude(id = id).get(title = self.cleaned_data['title'])
            else:
                 post = Post.objects.get(title = self.cleaned_data['title'])
        except:
            return self.cleaned_data['title']
        raise forms.ValidationError(f'{post.title} post Already Exists.')

    def clean_user(self):
        user_id = self.cleaned_data['user']
        print("USER: "+ str(user_id))
        try:
            user = User.objects.get(id = user_id)
            return user
        except:
            raise forms.ValidationError("User ID is unrecognize.")

    # def clean_category(self):
    #     category = self.cleaned_data.get('category')
    #     if category and not Category.objects.filter(id=category.id).exists():
    #         raise forms.ValidationError("Invalid category.")
    #     return category


class FilterForm(forms.Form):
    user = forms.ModelChoiceField(queryset=User.objects.all(), empty_label='请选择', required=False)
    mould = forms.ModelChoiceField(queryset=Mould.objects.all(), empty_label='请选择', required=False)
    date = forms.DateField
    category = forms.ModelChoiceField(queryset=Category.objects.all(), empty_label='请选择', required=False)
    machine = forms.ModelChoiceField(queryset=Machine.objects.all(), empty_label='请选择', required=False)
    material = forms.ModelChoiceField(queryset=Material.objects.all(), empty_label='请选择', required=False)

    class Meta:
        model= Post
        fields = ('user','file_path','category', 'mould', 'machine','date','material')


class MyForm(forms.Form):
    myfield = MarkdownxFormField()