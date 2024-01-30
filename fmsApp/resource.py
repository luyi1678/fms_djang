from import_export import resources
from .models import *


class PostResource(resources.ModelResource):
    class Meta:
        model = Post


class MouldResource(resources.ModelResource):
    class Meta:
        model = Mould


class MachineResource(resources.ModelResource):
    class Meta:
        model = Machine


class MaterialResource(resources.ModelResource):
    class Meta:
        model = Material


class CategoryResource(resources.ModelResource):
    class Meta:
        model = Category