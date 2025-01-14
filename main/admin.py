from django.contrib import admin
from .models import MainPage, MainPageImage, Demand, Geography, SkillsSet, StatisticSet


class MainPageImageInline(admin.TabularInline):
    model = MainPageImage
    extra = 1


@admin.register(MainPage)
class MainPageAdmin(admin.ModelAdmin):
    inlines = [MainPageImageInline]


admin.site.register(Demand)
admin.site.register(Geography)
admin.site.register(SkillsSet)
admin.site.register(StatisticSet)
