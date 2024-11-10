import math
from qb import models
from tests import engine
from library import models as lib_models
from utils import constants as const

def chapter_progress(user):
    chapter_scores = engine.chapter_score(user)
    on_progress = list(); untouched = list()
    for chapter in models.Chapter.objects.filter(name__in=const.QUICK_TEST_SYLLABUS):
        _ = list()
        if chapter in chapter_scores:
            _.append(chapter_scores[chapter])
        learner = lib_models.Learner.objects.filter(user=user, chapter=chapter)
        if learner.exists():
            _.append(learner.first().progress)
        prog = math.ceil(sum(_) / len(_)) if len(_) > 0 else 0
        progress = {
            'chapter': chapter,
            'progress': prog,
            'progress_css_str': f'width:{prog}%;'
        }
        if progress['progress']:
            on_progress.append(progress)
        else: untouched.append(progress)
    return {
        'on_progress': on_progress, 'untouched': untouched
    }