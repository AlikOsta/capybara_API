from django.contrib import admin
from .models import Category, SuperRubric, SubRubric
from .forms import SubRubricForm


class SubRubricInline(admin.TabularInline):
    model = SubRubric


class SuperRubricAdmin(admin.ModelAdmin):
    exclude = ('super_rubric',)
    inlines = [SubRubricInline]


class SubRubricAdmin(admin.ModelAdmin):
    form = SubRubricForm


admin.site.register(Category)

admin.site.register(SuperRubric, SuperRubricAdmin)


