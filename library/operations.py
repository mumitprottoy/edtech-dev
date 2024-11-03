from . import models


def get_level(learner: models.Learner):
    if not learner.levels.exists():
        for topic in learner.chapter.topics.all().order_by('id'):
            models.Level.get_or_create(learner=learner, topic=topic)
    return learner.get_next_level()

def import_topics():
    pass