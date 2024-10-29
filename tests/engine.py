import random
from django.contrib.auth.models import User
from . import models
from qb import models as qb_models
from utils import constants as const
from django.db.models import QuerySet


class Filteration:
    
    def __init__(
        self, metadata_list: list[models.QuestionMetaData], qty: int, user: User) -> None:               
        self.metadata_list = metadata_list
        self.qty = qty
        self.user = user
        print('primary selection:', len(metadata_list))
    
    def is_meta_eligible(self, metadata: models.QuestionMetaData):
        for part in models.TestParticipant.objects.filter(user=self.user):
            quest_set = part.test.question_set
            member = quest_set.members.filter(metadata=metadata)
            if member.exists():
                for q in member.first().metadata.questions.all():
                    answer = models.TestAnswer.objects.filter(participant=part, question=q)
                    if (not answer.exists()) or (not answer.first().is_correct):
                        return True
                return False
        return True 
    
    def count_question(self, meta: models.QuestionMetaData) -> int:
        return meta.get_question_count()
    
    def count_question_from_metadata_list(
        self, metadata_list: list[models.QuestionMetaData]) -> int:
        count = 0
        for meta in metadata_list:
            count += self.count_question(meta)
            
        return count  
    
    def pick_meta(self, metadata_list, count, qty, index, n, attempt=0):
        index = random.choice(index, index+n)
        meta = metadata_list[index]
        if (attempt <= 5) or (self.count_question(meta) + count <= qty):
            return meta
        
        return self.pick_index()
    
    def update_list(
        self, source_list: list[models.QuestionMetaData], final_list: list[models.QuestionMetaData]) -> models.QuestionMetaData:
        if source_list:
            index = random.choice(range(len(source_list)))
            meta = source_list[index]
            final_list.append(meta)
            source_list.pop(index)
            
            return meta         
    
    def add_comp(self, comp_list, final_list, n):
        added = 0
        for _ in range(n):
            if comp_list:
                meta = self.update_list(comp_list, final_list)
                if meta:
                    added += meta.get_question_count()
                    
        return added
    
    def secondary_filteration(self) -> list[models.QuestionMetaData]:
        print('running secondary filteration')
        rejection_list: list[models.QuestionMetaData] = list()
        short_list: list[models.QuestionMetaData] = self.metadata_list
        # for meta in self.metadata_list:
        #     if self.is_meta_eligible(meta):
        #         short_list.append(meta)
        #     else: rejection_list.append(meta)
        difference = lambda: self.count_question_from_metadata_list(short_list) - self.qty
        if difference() >= 0:
            return short_list
        for meta in rejection_list:
            if difference() < 0: break
            short_list.append(meta)
            
        return short_list
    
    def final_selection(
        self, short_list: list[models.QuestionMetaData]) -> list[models.QuestionMetaData]:
        final_list: list[models.QuestionMetaData] = list()
        chapter = qb_models.Chapter.get_comp()
        comp_list = list(); rest_list = list()
        for meta in short_list:
            if meta.chapter.name == chapter.name:
                comp_list.append(meta)
            else: rest_list.append(meta)
        n = const.comp_meta_qty(self.qty)
        added = self.add_comp(comp_list, final_list, n)
        while len(rest_list) and added != self.qty:
            meta = self.update_list(rest_list, final_list)
            if meta:
                added += meta.get_question_count()
        if added < self.qty:
            if (self.qty - added) % 5 == 0:
                n = (self.qty - added) // 5
                added += self.add_comp(comp_list, final_list, n)
            index = 0; metadata_list = self.metadata_list
            while added != self.qty:
                if index == len(metadata_list):
                    index = 0
                    metadata_list = list(models.QuestionMetaData.get_all_non_comp())
                meta = metadata_list[index]
                if meta not in final_list:
                    if meta.get_question_count() + added <= self.qty:
                        final_list.append(meta)
                        added += meta.get_question_count()
                index += 1
                    
        return models.QuestionMetaData.objects.filter(id__in=[meta.id for meta in final_list])
    
    def get_filtered_bulk(self):
        return self.final_selection(self.secondary_filteration())


class QuestionSetMaker:
    
    def __init__(self, bulk: QuerySet, quantity: int) -> None:
        self.bulk = bulk
        self.quantity = quantity
        self.question_set = self.create_question_set()
    
    def create_question_set(
        self, name: str = str()) -> models.QuestionSet:
        question_set = models.QuestionSet(
            name=name, quantity=self.quantity)
        question_set.save()
        return question_set

    def add_question_set_member(
        self, metadata: models.QuestionMetaData) -> models.QuestionSetMember:
        member = models.QuestionSetMember.objects.filter(
            question_set=self.question_set, metadata=metadata)
        if not (member.exists() or self.question_set.members.count() == self.bulk.count()):
            models.QuestionSetMember(
                question_set=self.question_set, metadata=metadata).save()
            
    def add_all_members(self) -> None:
        for meta in self.bulk.all():
            self.add_question_set_member(meta)
    
    def make(self):
        self.add_all_members()
        return self.question_set


class TestSetter:
    
    def __init__(
        self, question_set: models.QuestionSet, marking_criterion: models.MarkingCriterion) -> None:
        self.question_set = question_set
        self.marking_criterion = marking_criterion
        self.test = self.create_test()
        
    def create_test(self):
        test = models.Test(
            question_set=self.question_set, marking_criterion=self.marking_criterion)
        test.save()
        return test 


class ParticipantSetter:
    
    def __init__(self, user: User, test: models.Test) -> None:
        self.user = user
        self.test = test
        self.participant = self.create_participant()
        
    def create_participant(self) -> models.TestParticipant:
        if not models.TestParticipant.objects.filter(
            test=self.test, user=self.user).exists():
            participant = models.TestParticipant(
                test=self.test, user=self.user)
            participant.save()
            return participant
    
    def create_test_answer(self, question: models.Question) -> None:
        if not models.TestAnswer.objects.filter(
            participant=self.participant, question=question).exists():
            models.TestAnswer(
                participant=self.participant, question=question).save()
    
    def create_answer_sheet(self) -> None:
        for member in self.test.question_set.members.all():
            for question in member.metadata.questions.all():
                self.create_test_answer(question)
    
    def set_participant(self) -> models.TestParticipant:
        self.create_answer_sheet()
        return self.participant


class TestInitiator:
    
    def __init__(self, test: models.Test, date_time=None) -> None:
        self.test = test
        self.datetime = date_time
        
    def create_timer(self) -> models.TestTimer:
        if not models.TestTimer.objects.filter(test=self.test).exists():
            timer = models.TestTimer(test=self.test)
            if self.datetime is not None:
                timer.start_datetime = self.datetime
            timer.save()
            return timer
        return self.test.timer 
    
    def initiate(self) -> models.Test:
        timer = self.create_timer()
        return timer


class TestEvaluator:
    
    def __init__(self, participant: models.TestParticipant) -> None:
        self.participant = participant
        self.test = self.participant.test
        self.answers = self.participant.answers    
    
    def get_total_mark(self) -> float:
        total_mark = sum([answer.get_mark() for answer in self.answers.all()])
        return total_mark if total_mark >= 0 else float(0)
    
    def get_total_mark_str(self) -> str:
        total_possible_mark = self.answers.count() * self.test.marking_criterion.correct
        return f'{self.get_total_mark()} / {total_possible_mark}'
    
    def get_answer_sheet(self) -> list:
        return [
            answer.get_marking_key() for answer in self.answers.all()]
    
    def get_short_report(self) -> dict:
        ans_sheet = self.get_answer_sheet()
        return {
            'correct': ans_sheet.count(True),
            'wrong': ans_sheet.count(False),
            'skipped': ans_sheet.count(None),
        }
    
    def get_correction_rate(self) -> float:
        ans_sheet = self.get_answer_sheet()
        return (ans_sheet.count(True) / len(ans_sheet)) * 100 if len(ans_sheet) > 0 else float(0)
    
    def get_correction_rate_str(self) -> float:
        return f'{self.get_correction_rate():.2f}%'
    
    def get_detailed_test_report(self) -> list:
        pass
    
    def chapter_wise_short_report(self): 
        pass
    

def start_exam(
    bulk: QuerySet, qty: int, user: User, marking_criterion=models.MarkingCriterion.get_default()) -> models.Test:
    filteration = Filteration(list(bulk), qty, user)
    filtered_bulk = filteration.get_filtered_bulk()
    qs_maker = QuestionSetMaker(bulk=filtered_bulk, quantity=qty)
    question_set = qs_maker.make()
    test_setter = TestSetter(
        question_set=question_set, marking_criterion=marking_criterion)
    test = test_setter.test
    participant_setter = ParticipantSetter(user=user, test=test)
    participant = participant_setter.set_participant()
    TestInitiator(test=test).initiate()
    return participant    
    