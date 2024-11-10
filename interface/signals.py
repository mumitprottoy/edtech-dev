from django.dispatch import receiver
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from profiles import models as profile_models, operations
from stuff import models as stuff_models
from library import models as lib_models


@receiver(post_save, sender=User)
def add_profile_pic(instance: User, created: bool, *args, **kwargs):
    user = instance
    if created:
        profile_models.Picture(user=user).save()


@receiver(post_save, sender=User)
def assign_full_name(instance: User, created: bool, *args, **kwargs):
    user = instance
    if created and (not (user.first_name and user.last_name)):
        first_name, last_name = stuff_models.Name.get_random_name()
        user.first_name = first_name; user.last_name = last_name
        user.save()


@receiver(post_save, sender=lib_models.Learner)
def set_up_levels(instance: lib_models.Learner, created: bool, *args, **kwargs):
    learner = instance
    if created:
        for topic in learner.chapter.topics.all().order_by('id'):
            level = lib_models.Level(
                learner=learner, topic=topic)
            level.save()
            quiz = lib_models.Quiz(level=level); quiz.save()
            for question in topic.questions.all():
                lib_models.Answer(quiz=quiz, question=question).save()


# @receiver(post_save, sender=lib_models.Level)
# def update_learner_completion_status(instance: lib_models.Level, *args, **kwargs):
#     level = instance
#     if level.is_
