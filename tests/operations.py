from qb import models as qb_models
from utils import constants as const
from . import models

def get_quick_syllabus_chapters() -> list[qb_models.Chapter]:
    return list(qb_models.Chapter.objects.filter(
        name__in=const.QUICK_TEST_SYLLABUS))


def authtenticate_participant(user, key):
    test = models.Test.objects.filter(key=key)
    if test.exists():
        test = test.first()
        participant = models.TestParticipant.objects.filter(
            test=test, user=user)
        if participant.exists():
            participant = participant.first()
            return participant


def clear_test_db():
    if input('Are you sure? : ').lower() == 'yes':
        for model in [
            models.QuestionSet,
            models.QuestionSetMember,
            models.Test,
            models.TestTimer,
            models.TestParticipant,
            models.TestAnswer
        ]: model.objects.all().delete()