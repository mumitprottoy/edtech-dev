import math
from datetime import datetime
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
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


class QGenParams:
    
    def __init__(self, *args, **kwargs): pass


class Test(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, default='')
    start_time = models.DateTimeField(auto_now_add=True)
    test_length_minute = models.BigIntegerField(default=12)
    question_quantity = models.BigIntegerField(default=15)
    marking_criterion = models.ForeignKey(
        MarkingCriterion, 
        on_delete=models.CASCADE, 
        default=1
        )
    has_ended = models.BooleanField(default=False)
    
    def get_time_left_in_seconds(self) -> int:
        start_time = self.start_time.astimezone(tz=timezone.get_current_timezone())
        current_time = datetime.today().astimezone(tz=timezone.get_current_timezone())
        seconds_left = (current_time - start_time).total_seconds()
        return seconds_left
    
    def generate_unique_test_name(self) -> str:
        keygen = KeyGen()
        return keygen.alphanumeric_key(5) + keygen.datetime_key()
    
    def gather_meta_data(self): pass
    
    def get_marked_ans_sheet(self) -> list:
        return [{
            'question': q.question,
            'answer': q.question.option,
            'mark': q.answer.get_mark(
                self.marking_criterion.marking_map())
        } for q in self.questions.all()]
    
    def get_total_mark(self) -> float:
        total_mark = sum([ans['mark'] for ans in self.get_marked_ans_sheet()])
        return total_mark if total_mark >= 0 else float(0)
    
    def get_short_report(self) -> dict:
        ans_sheet = [
            q.answer.get_marking_key() for q in self.questions.all()]
        return {
            'Correct': ans_sheet.count(True),
            'Wrong': ans_sheet.count(False),
            'Skipped': ans_sheet.count(None),
        }
    
    def get_all_metadata_ids(self): pass
        
    def get_renderable_test_report(self) -> list:
        return [{
            'question': q.question.text,
            'option': q.question.option.text,
            'explanation': q.question.explanation.text,
            'chapter': q.question.meta.chapter.name,
            'is_skipped': self.marking_criterion.skipped == q.answer.get_mark(
                self.marking_criterion.marking_map()),
            'is_correct': self.marking_criterion.correct == q.answer.get_mark(
                self.marking_criterion.marking_map()),
        } for q in self.questions.all()] 
    
    def chapter_wise_short_report(self): 
        pass
    
    def save(self, *args, **kwargs) -> None:
        if not self.name:
            self.name = self.generate_unique_test_name()
        min_time = math.floor(self.question_quantity * const.TIME_PERCENTAGE)
        self.test_length_minute = min_time
        if self.question_quantity < const.MIN_QUES_QTY:
            self.question_quantity = const.MIN_QUES_QTY 
        super().save(*args, **kwargs)


class TestQuestion(models.Model):
    test = models.ForeignKey(
        Test, on_delete=models.CASCADE, related_name='questions')
    metadata = models.ForeignKey(QuestionMetaData, on_delete=models.CASCADE)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)

    
class TestAnswer(models.Model):
    question = models.OneToOneField(
        TestQuestion, on_delete=models.CASCADE, related_name='answer')
    option_id = models.BigIntegerField(default=0)
    
    def option_is_valid(self) -> bool:
        return self.question.options.filter(
            id=self.option_id).exists()
           
    def get_option_object(self):
        if self.option_id and self.option_is_valid():
            return self.question.options.get(id=self.option_id)
        return None
    
    def get_marking_key(self):
        option = self.get_option_object()
        if option is not None:
            return option.is_correct
        return None
    
    def get_mark(self, marking_map: dict) -> float:
        return marking_map[self.get_marking_key()]
