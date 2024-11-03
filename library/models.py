import random
from django.db import models
from django.core import exceptions
from django.contrib.auth.models import User
from qb import models as qb_models


class Learner(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='studies')
    chapter = models.ForeignKey(
        qb_models.Chapter, on_delete=models.CASCADE)
    
    def get_next_level(self):
        for level in self.levels.all().order_by('id'):
            if not (level.is_completed and (not level.quiz.is_passed())):
                return level
        return None

class Topic(models.Model):
    chapter = models.ForeignKey(
        qb_models.Chapter, on_delete=models.CASCADE, related_name='topics')
    title = models.CharField(max_length=200)
    content = models.TextField()
    
    def __str__(self):
        return f'{self.chapter} - {self.title}'


class Level(models.Model):
    learner = models.ForeignKey(
        Learner, on_delete=models.CASCADE, related_name='levels')
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    is_completed = models.BooleanField(default=False)
    
    @classmethod
    def get_or_create(cls, **kwargs):
        obj = cls.objects.filter(**kwargs)
        if not obj.exists():
            _new = cls(**kwargs); _new.save()
            return _new
        return obj.first()


class Quiz(models.Model):
    level = models.ForeignKey(Level, on_delete=models.CASCADE, related_name='quiz')
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    
    def is_passed(self):
        for ans in self.answers.all():
            if not ans.is_correct():
                return False
        return True
    
    def get_question_paper(self):
        return [answer for answer in self.answers.all() if not answer.is_correct()]
    
    def get_next_question(self):
        ques_paper = self.get_question_paper()
        if ques_paper:
            return random.choice(ques_paper)


class Question(models.Model):
    topic = models.ForeignKey(
        Topic, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField()


class Option(models.Model):
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name='options')
    text = models.TextField()
    is_correct = models.BooleanField(default=False)


class Answer(models.Model):
    quiz = models.ForeignKey(
        Quiz, on_delete=models.CASCADE, related_name='answers')
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    option_id = models.BigIntegerField(default=0)
    
    def is_correct(self):
        option = self.question.options.filter(id=self.option_id)
        return option.exists() and option.first().is_correct
