from django.contrib.auth.models import User
from .operations import Filteration
from utils.operations import chapter_count_map
from qb import models


chapter_names = ['Preposition', 'Pronoun', 'Comprehension', 'Article']
def test_filteration():
    chapter_names = ['Comprehension', 'Article']
    chapter_list = list(models.Chapter.objects.all())
    meta_list = list(models.QuestionMetaData.objects.filter(chapter__in=chapter_list))
    user = User.objects.first()
    filteration = Filteration(meta_list, 50, user)
    bulk = filteration.get_filtered_bulk()
    _map = chapter_count_map(bulk)
    print('\n'*3)
    for k,v in _map.items(): print(k,v)
