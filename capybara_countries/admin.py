from django.contrib import admin
from .models import Country, City, SuperLocal, SubLocal
from .forms import SubLocalForm


class SubLocalInline(admin.TabularInline):
    model = SubLocal

class SuperLocalAdmin(admin.ModelAdmin):
    exclude = ('super_Local',)
    inlines = [SubLocalInline]


class SubRubricAdmin(admin.ModelAdmin):
    form = SubLocalForm

admin.site.register(SuperLocal, SuperLocalAdmin)

admin.site.register(Country)
admin.site.register(City)