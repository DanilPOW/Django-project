from django.db import models


class MainPage(models.Model):
    title = models.TextField(blank=True, verbose_name='Название профессии')
    description = models.TextField(blank=True, verbose_name='Описание профессии')
    image = models.ImageField(blank=False, verbose_name='Изображение', upload_to='images/')


class MainPageImage(models.Model):
    main_page = models.ForeignKey(MainPage, on_delete=models.CASCADE, related_name='additional_images',
                                  verbose_name='Основная страница')
    image = models.ImageField(verbose_name='Дополнительное изображение', upload_to='images/')


class Demand(models.Model):
    graph_salary_level = models.ImageField(blank=False,
                                           verbose_name='График уровня зарплат по годам')
    graph_num_vacancy = models.ImageField(blank=False,
                                          verbose_name='График количества вакансий по годам')
    salary_table = models.TextField(blank=False, verbose_name='Таблица уровня зарплат по годам')
    vacancy_table = models.TextField(blank=False, verbose_name='Таблица количества вакансий по годам')


class Geography(models.Model):
    graph_salary_level_by_city = models.ImageField(blank=False,
                                                   verbose_name='График уровень зарплат по городам')
    graph_vacancy_fraction_by_city = models.ImageField(blank=False,
                                                       verbose_name='График доля вакансий по городам')
    level_by_city_table = models.TextField(blank=False, verbose_name='Таблица уровень зарплат по городам')
    fraction_by_city_table = models.TextField(blank=False, verbose_name='Таблица доля вакансий по городам')


class SkillsSet(models.Model):
    table_name = models.TextField(blank=False, verbose_name='Название таблицы', max_length=30)
    table = models.TextField(blank=False, verbose_name='Таблица')
    graph_skills = models.ImageField(blank=False, verbose_name='График по скиллам')

    class Meta:
        verbose_name = 'skill'
        verbose_name_plural = 'skills'


class StatisticSet(models.Model):
    yearly_salary_graph = models.ImageField(blank=False, verbose_name='График уровня зарплат по годам')
    yearly_salary_table = models.TextField(blank=False, verbose_name='Таблица уровня зарплат по годам')

    yearly_vacancy_count_graph = models.ImageField(blank=False, verbose_name='График количества вакансий по годам')
    yearly_vacancy_count_table = models.TextField(blank=False, verbose_name='Таблица количества вакансий по годам')

    city_salary_graph = models.ImageField(blank=False, verbose_name='График уровня зарплат по городам')
    city_salary_table = models.TextField(blank=False, verbose_name='Таблица уровня зарплат по городам')

    city_rate_vacancy_graph = models.ImageField(blank=False, verbose_name='График доли вакансий по городам')
    city_rate_vacancy_table = models.TextField(blank=False, verbose_name='Таблица доли вакансий по городам')

    top20_skills_graph = models.ImageField(blank=False, verbose_name='График топ 20 навыков по годам')
    top20_skills_table = models.TextField(blank=False, verbose_name='Таблица топ 20 навыков по годам')
