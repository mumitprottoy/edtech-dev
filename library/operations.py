import requests
from . import models
from qb import models as qb_models
    

def get_learner(user, chapter):
    learner = models.Learner.get_or_create(user, chapter)
    for topic in learner.chapter.topics.all().order_by('id'):
        level = models.Level.get_or_create(
            learner=learner, topic=topic)
        if not models.Quiz.objects.filter(level=level).exists():
            quiz = models.Quiz(level=level, topic=topic); quiz.save()
            for question in topic.questions.all():
                models.Answer(quiz=quiz, question=question).save()
    return learner


def current_level(user):
    learners = list(models.Learner.objects.filter(user=user))
    levels = models.Level.objects.filter(
        learner__in=learners, is_completed=True).order_by('-completed_at')
    last = None
    for level in levels:
        if not level.quiz.is_passed:
            return level
        last = level.learner.get_next_level()
        if last is not None: return last
    return last    


def get_chapter_lists_for_library(user):
    chapters = list(set([topic.chapter for topic in models.Topic.objects.all()]))
    completed = list(); on_progress = list(); untouched = list()
    
    while len(chapters) > 0:
        learner = models.Learner.objects.filter(user=user, chapter=chapters[0])
        if not learner.exists():
            untouched.append(chapters[0]); chapters.pop(0)
            continue
        learner = learner.first()
        if learner.is_completed:
            completed.append(learner.levels.first())
        else: on_progress.append(learner.levels.first())
        chapters.pop(0)
    return {
        'completed': completed, 'on_progress': on_progress, 'untouched': untouched 
    }


def import_topics():
    models.Topic.objects.all().delete()
    package = requests.get('https://edtechops.xyz/topics-api/oimamapls').json()['library']
    for pack in package:
        chapter = qb_models.Chapter.objects.get(name=pack['chapter'])
        print(chapter.name)
        print(len(pack['topics']), 'topics')
        for topic in pack['topics']:
            new_topic = models.Topic(
                chapter=chapter,
                title=topic['title'],
                content=topic['content']
            )          
            new_topic.save()
            if topic['mcqs']:
                print('adding mcqs')
                for _ in topic['mcqs']:
                    question = models.Question(
                       topic=new_topic,
                       text=_['text'] 
                    )
                    question.save()
                    for opt in _['options']:
                        models.Option(
                          question=question,
                          text=opt['text'],
                          is_correct=opt['is_correct']  
                        ).save()
            print('Completed:', new_topic.title)
            print('\n')
