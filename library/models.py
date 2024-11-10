import math, random
from django.db import models
from django.core import exceptions
from django.contrib.auth.models import User
from qb import models as qb_models
from utils.keygen import KeyGen


class Learner(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='studies')
    chapter = models.ForeignKey(
        qb_models.Chapter, on_delete=models.CASCADE)
    
    @classmethod
    def get_or_create(cls, user: User, chapter: qb_models.Chapter):
        learner = cls.objects.filter(user=user, chapter=chapter)
        if learner.exists(): learner = learner.first()
        else:
            learner = cls(user=user, chapter=chapter); learner.save()
        return learner
    
    @property
    def progress(self):
        total_topics = self.levels.count()
        comleted_count = 0
        for level in self.levels.filter(is_completed=True):
            if not level.quiz.is_passed:
                continue
            comleted_count += 1
        return math.floor((comleted_count / total_topics) * 100) if total_topics > 0 else 0
    
    @property
    def progress_css_str(self):
        return f'width: {self.progress}%;'
    
    @property
    def is_completed(self):
        last_level = self.levels.all().order_by('id').last()
        return last_level.is_completed and last_level.quiz.is_passed
    
    def get_next_level(self):
        for level in self.levels.all().order_by('id'):
            if level.is_completed:
                if level.quiz.is_passed:
                    continue
            return level
        return None


class Topic(models.Model):
    chapter = models.ForeignKey(
        qb_models.Chapter, on_delete=models.CASCADE, related_name='topics')
    title = models.CharField(max_length=200)
    content = models.TextField()
    
    def __str__(self):
        return f'{self.chapter.name} - {self.title}'


class Level(models.Model):
    learner = models.ForeignKey(
        Learner, on_delete=models.CASCADE, related_name='levels')
    topic = models.ForeignKey(Topic, on_delete=models.CASCADE)
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(auto_now=True)
    
    @classmethod
    def get_or_create(cls, **kwargs):
        obj = cls.objects.filter(**kwargs)
        if not obj.exists():
            _new = cls(**kwargs); _new.save()
            return _new
        return obj.first()


class Quiz(models.Model):
    level = models.OneToOneField(
        Level, on_delete=models.CASCADE, related_name='quiz')
    
    @property
    def progress(self):
        total = self.answers.count()
        corrected = 0
        for ans in self.answers.all():
            if ans.is_correct(): corrected += 1
        return math.floor((corrected / total) * 100) if total > 0 else 100
    
    @property
    def progress_css_str(self):
        return f'width: {self.progress}%;'
    
    @property
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
    
    def renderable_paper(self):
        validator = dict(); buddhi = dict()
        package = {
            'question': self.question,
            'options': list()
        }
        for option in self.question.options.all():
            key = KeyGen().alphanumeric_key() 
            package['options'].append({
                'text': option.text,
                'id': key
            })
            validator[key] = option.is_correct
            buddhi[key] = {'id': self.id, 'is_correct': option.is_correct}
        return validator, package, buddhi
        
    def is_correct(self):
        option = self.question.options.filter(id=self.option_id)
        return option.exists() and option.first().is_correct
