import math, random
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

    def get_total_mark(self, ans_sheet=None) -> float:
        ans_sheet = self.answers.all() if ans_sheet is None else ans_sheet
        total_mark = sum([answer.get_mark() for answer in ans_sheet])
        return total_mark if total_mark >= 0 else float(0)
    
    def total_answerable(self, ans_sheet=None):
        return self.answers.count() if ans_sheet is None else len(ans_sheet) 
    
    def get_total_mark_str(self, ans_sheet=None) -> str:
        ans_sheet = self.answers.all() if ans_sheet is None else ans_sheet
        total_count = self.total_answerable(ans_sheet)
        total_possible_mark = total_count * self.test.marking_criterion.correct
        return f'{self.get_total_mark(ans_sheet)} / {total_possible_mark}'
    
    def get_answer_sheet(self, ans_sheet=None) -> list:
        ans_sheet = self.answers.all() if ans_sheet is None else ans_sheet
        return [
            answer.get_marking_key() for answer in self.answers.all()]
    
    def get_short_report_dict(self, ans_sheet=None) -> dict:
        sheet = self.get_answer_sheet(ans_sheet)
        return {
            'score': self.get_total_mark_str(ans_sheet),
            'total': self.total_answerable(ans_sheet),
            'correct': sheet.count(True),
            'wrong': sheet.count(False),
            'skipped': sheet.count(None),
        }
        
    def get_short_report_list(self, ans_sheet=None) -> dict:
        sheet = self.get_answer_sheet(ans_sheet)
        return [
            {
            'name': 'Score',
            'value': self.get_total_mark_str(ans_sheet),
            'border': 'brd-l-bar-theme'
            },
            {
            'name': 'Total',
            'value': self.total_answerable(ans_sheet),
            'border': 'brd-l-bar-primary'
            },
            {
            'name': 'Correct',
            'value': sheet.count(True),
            'border': 'brd-l-bar-green'
            },
            {
            'name': 'Wrong',
            'value': sheet.count(False),
            'border': 'brd-l-bar-red'
            },
            {
            'name': 'Skipped',
            'value': sheet.count(None),
            'border': 'brd-l-bar-def'
            },
        ]
        
    def get_solved_ans_sheet(self) -> list:
        return [
            {'passage' : member.metadata.passage.text if member.metadata.has_passage else None,
            'questions': [{
                'question': question,
                'options' : [{
                        'option': option.text,
                        'is_correct': option.is_correct,
                        'has_answered': option.id == self.answers.get(
                            question=question).option_id 
                    } for option in question.options.all()]
                } for question in member.metadata.questions.all()]
            } for member in self.test.question_set.members.all()]
        
    def get_chapter_wise_ans_sheet(self): 
        chapter_map = dict()
        for ans in self.participant.answers.all():
            chapter = ans.question.metadata.chapter
            if not (chapter in chapter_map):
                chapter_map[chapter] = {'answers': [ans]}
            else: chapter_map[chapter]['answers'].append(ans)
        return chapter_map

    def get_chapter_wise_short_report(self):
        chapter_wise_ans_sheet = self.get_chapter_wise_ans_sheet()
        report = [{
            'chapter': chapter,
            'score': self.get_total_mark(chapter_wise_ans_sheet[chapter]['answers']),
            'short_report': self.get_short_report_dict(chapter_wise_ans_sheet[chapter]['answers'])
        } for chapter in chapter_wise_ans_sheet]
        return sorted(report, key=lambda x: x['score'])
        
    def suggestions(self):
        reports = self.get_chapter_wise_short_report()
        return reports[:3 if len(reports) <= 3 else len(reports)]
            

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


def chapter_score(user):
    _map = dict()
    for part in models.TestParticipant.objects.filter(user=user):
        for ans in part.answers.all():
            chapter = ans.question.metadata.chapter
            if chapter in _map:
                _map[chapter]['marks'].append(int(ans.is_correct()))
            else: _map[chapter] = {'marks' : [int(ans.is_correct())]}
    return [{
        'chapter': chapter,
        'score': math.floor((sum(_map[chapter]['marks']) / len(_map[chapter]['marks'])) * 100)
    } for chapter in _map]