from django.contrib.auth.models import User
from django.db import models
from datetime import datetime


current_year = lambda: datetime.today().year


class AdmissionTest(models.Model):
    name = models.CharField(max_length=100, unique=True)
    acronym = models.CharField(max_length=20, unique=True)
    
    def __str__(self):
        return self.name


class University(models.Model):
    admission_test = models.ForeignKey(
        AdmissionTest, on_delete=models.CASCADE, default=1, related_name='universities')
    acronym = models.CharField(max_length=20, unique=True)
    
    def __str__(self):
        return self.acronym  


class Chapter(models.Model):
    name = models.CharField(max_length=100, unique=True)
    
    @classmethod
    def get_comp(cls):
        return cls.objects.get(name='Comprehension')
 

class QuestionMetaData(models.Model):
    has_appeared = models.BooleanField(default=False)
    has_passage = models.BooleanField(default=False)
    chapter = models.ForeignKey(Chapter, on_delete=models.CASCADE)
    
    def get_question_count(self):
        return self.questions.count()
    
    @classmethod
    def get_all_metadata_by_chapters(cls, chapters: list):
        return cls.objects.filter(chapter__in=chapters)
    
    @classmethod
    def get_all_non_comp(cls):
        return cls.objects.all().exclude(chapter=Chapter.get_comp())


class Appearance(models.Model):
    metadata = models.OneToOneField(QuestionMetaData, on_delete=models.CASCADE)
    YEAR_CHOICES = [(str(yr), str(yr)) 
                    for yr in range(current_year(), current_year()-41, -1)]
    university = models.ForeignKey(University, on_delete=models.CASCADE, default=1)
    unit = models.CharField(max_length=10)
    year = models.CharField(max_length=10, choices=YEAR_CHOICES)
    
    def appearance_label_str(self):
        return f'{self.admission_test.acronym} {{self.unit}} {self.year}'


class Passage(models.Model):
    metadata = models.OneToOneField(QuestionMetaData, on_delete=models.CASCADE)
    text = models.TextField(default='Passage Text')


class Question(models.Model):
    metadata = models.ForeignKey(
        QuestionMetaData, on_delete=models.CASCADE, related_name='questions')
    text = models.TextField(default='Question Text')
    
    def get_correct_answer(self):
        for option in self.options.all():
            if option.is_correct: 
                return option


class Option(models.Model):
    question = models.ForeignKey(
        Question, on_delete=models.CASCADE, related_name='options')
    text = models.TextField(default='Option Text')
    is_correct = models.BooleanField(default=False)


class Explanation(models.Model):
    question = models.OneToOneField(Question, on_delete=models.CASCADE)
    text = models.TextField(default='Explanation Text')
