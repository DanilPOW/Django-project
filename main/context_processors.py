from . import core_constants
from .models import *


def fcs(request):
    return {'FCs': core_constants.FCs}


def academic_group(request):
    return {'ACADEMIC_GROUP': core_constants.ACADEMIC_GROUP}


def get_main_page(request):
    return MainPage.objects.prefetch_related('additional_images').all()


def get_skills_page(request):
    return SkillsSet.objects.all()


def profession_name(request):
    return {'PROFESSION_NAME': core_constants.PROFESSION_NAME}


def site_name(request):
    return {'SITE_NAME': core_constants.SITE_NAME}
