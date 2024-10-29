import math
from datetime import datetime
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.core import exceptions
from utils.keygen import KeyGen
from utils import constants as const
from qb.models import (
    QuestionMetaData,
    Question
)


class MarkingCriterion(models.Model):
    DEFAULT_NAME = 'MC__1_0__0_25__0_0'
    
    name = models.CharField(max_length=20, default=DEFAULT_NAME)
    correct = models.FloatField(default=1.0)
    wrong = models.FloatField(default=-0.25)
    skipped = models.FloatField(default=0.0)
    
    @classmethod
    def get_default(cls):
        _filter =  cls.objects.filter(name=cls.DEFAULT_NAME)
        if _filter.exists():
            return _filter.first()
        else:
            default_criterion = cls.objects.create(
                name=cls.DEFAULT_NAME)
            default_criterion.save()
            return default_criterion
    
    def marking_map(self):
        return {
            True: self.correct,
            False: self.wrong,
            None: self.skipped
        }
    
    def __str__(self) -> str:
        return self.name
    
    
class QuestionSet(models.Model):
    name = models.CharField(max_length=100, unique=True)
    quantity = models.IntegerField(default=15)
    
    @classmethod
    def get_or_create(cls, **kwargs):
        _object = cls.objects.filter(**kwargs)
        if not _object.exists():
            _object = cls(**kwargs); _object.save()
            return _object
        else: return _object.first()
    
    def save(self, *args, **kwargs):
        if not self.name:
            self.name = KeyGen().unique_name()
        super().save(*args, **kwargs)


class QuestionSetMember(models.Model):
    question_set = models.ForeignKey(
        QuestionSet, on_delete=models.CASCADE, related_name='members')
    metadata = models.ForeignKey(QuestionMetaData, on_delete=models.CASCADE)


class Test(models.Model):
    key = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=100, unique=True)
    question_set = models.ForeignKey(QuestionSet, on_delete=models.CASCADE)
    marking_criterion = models.ForeignKey(MarkingCriterion, on_delete=models.CASCADE) 
    
    def save(self, *args, **kwargs) -> None:
        if not self.name:
            self.name = KeyGen().unique_name()
        if not self.key:
            self.key = KeyGen().key()
        super().save(*args, **kwargs)
    

class TestTimer(models.Model):
    test = models.OneToOneField(Test, on_delete=models.CASCADE, related_name='timer')
    start_datetime = models.DateTimeField()
    test_time = models.IntegerField(default=0)
    
    def get_time_difference_in_seconds(self) -> int:
        time_now = datetime.now().astimezone(tz=timezone.get_current_timezone())
        start_time = self.start_datetime.astimezone(tz=timezone.get_current_timezone())
        return int((time_now - start_time).total_seconds())
    
    def get_test_time_remaining(self) -> int:
        diff = self.get_time_difference_in_seconds()
        test_time_sec = (self.test_time * 60)
        remaining = test_time_sec - diff if diff >= 0 else test_time_sec 
        return remaining if remaining > 0 else 0
    
    def get_test_time_remaining_script(self) -> str:
        time_left = self.get_test_time_remaining()
        return f'<script>const secsLeft = {time_left};</script>'
    
    def get_waiting_time_remaining(self) -> int:
        diff = self.get_time_difference_in_seconds()
        return abs(diff) if diff < 0 else 0
    
    def get_waiting_time_remaining_script(self) -> str:
        time_left = self.get_waiting_time_remaining()
        return f'<script>const secsLeft = {time_left};</script>'
    
    def has_started(self) -> bool:
        return self.get_time_difference_in_seconds >= 0
    
    def has_ended(self) -> bool:
        return self.get_time_difference_in_seconds() >= (self.test_time * 60)
    
    def save(self, *args, **kwargs) -> None:
        self.test_time = self.test.question_set.quantity - const.TEST_MIN_CUT
        if not self.start_datetime:
            self.start_datetime = datetime.now()
        self.start_datetime = self.start_datetime.astimezone(tz=timezone.get_current_timezone())
        super().save(*args, **kwargs)
    

class TestParticipant(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    test = models.ForeignKey(Test, on_delete=models.CASCADE, related_name='participants')
    has_submitted = models.BooleanField(default=False)
    
    def get_answer_paper(self) -> dict:
        answer_paper: list[dict] = list()
        for member in self.test.question_set.members.all():
            meta = member.metadata
            questions = list()
            for question in meta.questions.all():
                answer = self.answers.get(question=question)
                if not answer.attempted:
                    questions.append({
                        'answer_id': answer.id,
                        'question_id': question.id,
                        'text': question.text,
                        'options': [{
                            'id': option.id,
                            'text': option.text
                            } for option in question.options.all()]
                    })
            if questions:
                answer_paper.append({
                    'meta_id': f'meta-{meta.id}',
                    'passage': meta.passage if meta.has_passage else None,
                    'questions': questions
                })
        return answer_paper
    
    def get_total_answered(self) -> int:
        return self.answers.filter(attempted=1).count()
    
    def get_total_answerable(self) -> int:
        return self.answers.count()
    
    def test_progress(self) -> int:
        return int(self.get_total_answered() / self.get_total_answerable())
            
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'test'],
                name='duplicate_participant'
            )
        ]

   
class TestAnswer(models.Model):
    participant = models.ForeignKey(
        TestParticipant, on_delete=models.CASCADE, null=True, related_name='answers')
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE)
    option_id = models.BigIntegerField(default=0)
    attempted = models.IntegerField(default= -1)
    
    def option_is_valid(self) -> bool:
        return self.question.options.filter(
            id=self.option_id).exists()
           
    def get_option_object(self):
        if self.option_id and self.option_is_valid():
            return self.question.options.get(id=self.option_id)
        return None
    
    def is_correct(self):
        option = self.get_option_object()
        return option.is_correct if option is not None else False
    
    def get_marking_key(self):
        option = self.get_option_object()
        if option is not None:
            return option.is_correct
        return None
    
    def get_mark(self) -> float:
        marking_map = self.participant.test.marking_criterion.marking_map()
        return marking_map[self.get_marking_key()]
    
    def save(self, *args, **kwargs):
        self.attempted += 1
        if self.attempted > 1:
            raise exceptions.ValidationError('Already attempted.')
        super().save(*args, **kwargs)
