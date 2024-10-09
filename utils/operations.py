from qb.models import *
from .stuff import stuff
from .chapters import chapters
from .atnu import atnu


def import_universities():
    University.objects.all().delete()
    _map = {'MEDICAL': 'MAT', 'DENTAL': 'DAT'}
    for at in atnu:
        for u in atnu[at]:
            _at = at if at not in _map else _map[at]
            admission_test = AdmissionTest.objects.get(acronym=_at)
            try:
                University(
                    admission_test=admission_test,
                    acronym=u,
                ).save()
            except: print('Error:', at, u)
    

def import_chapters():
    for chapter in chapters:
        Chapter(name=chapter).save()


def get_chaps():
    file = open('utils/chaps.txt', 'r')
    return file.read().split('\n')

def compare():
    return [chap.name for chap in Chapter.objects.all() if chap.name not in get_chaps()]


def import_qb():
    QuestionMetaData.objects.all().delete()
    import json
    file = open('utils/cool_qb.txt', 'r', encoding='utf-8')
    qb = json.loads(file.read())
    _len = len(qb)
    print('len:', _len)
    count = 0
    for _ in qb:
        university = University.objects.get(acronym=_['university'])
        metadata = QuestionMetaData(
            has_passage = _['has_passage'],
            has_appeared = True,
            chapter=Chapter.objects.get(name=_['chapter'])          
        )
        metadata.save()
        Appearance(
            metadata=metadata,
            university=university,
            unit=_['unit'],
            year=str(_['year'])
        ).save()
        if metadata.has_passage:
            Passage(metadata=metadata, text=_['passage']).save()
        for __ in _['block']:
            question = Question(metadata=metadata, text=__['text'])
            question.save()
            for opt in __['options']:
                option = Option(
                    question=question, 
                    text=opt['text'], 
                    is_correct=opt['is_correct']
                ) 
                option.save()
            Explanation(question=question, text=__['explanation']).save()
        count += 1
        print(f'{count}/{_len}')
