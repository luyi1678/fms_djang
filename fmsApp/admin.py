from django.contrib import admin
from .models import *
from import_export.admin import ImportExportModelAdmin
from import_export.admin import ImportExportMixin
from .resource import *

# Register your models here.
# admin.site.register(Category)
# admin.site.register(Mould)
# admin.site.register(Machine)
# admin.site.register(Material)
# admin.site.register(Post)


class MyImportExportMixin(ImportExportMixin):
    from_encoding = "gb2312"
    to_encoding = "utf-8"


class PostTmpAdmin(MyImportExportMixin, admin.ModelAdmin):
    resource_class = PostResource


class MouldTmpAdmin(MyImportExportMixin, admin.ModelAdmin):
    resource_class = MouldResource


class MachineTmpAdmin(MyImportExportMixin, admin.ModelAdmin):
    resource_class = MachineResource


class MaterialTmpAdmin(MyImportExportMixin, admin.ModelAdmin):
    resource_class = MaterialResource


class CategoryTmpAdmin(MyImportExportMixin, admin.ModelAdmin):
    resource_class = CategoryResource


admin.site.register(Post, PostTmpAdmin)
admin.site.register(Material, MaterialTmpAdmin)
admin.site.register(Machine, MachineTmpAdmin)
admin.site.register(Mould, MouldTmpAdmin)
admin.site.register(Category, CategoryTmpAdmin)