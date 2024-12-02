import time
from django.shortcuts import render, redirect
from . import engine, models, operations as ops
from utils import constants as const, decorators
from utils.global_context import Context
from .operations import authtenticate_participant


@decorators.login_required
@decorators.phone_number_required
def quick_test(request):
    chapters = ops.get_quick_syllabus_chapters()
    bulk = models.QuestionMetaData.objects.filter(chapter__in=chapters)
    participant = engine.start_exam(bulk, 20, request.user)
    return redirect('/test/'+participant.test.key)


@decorators.login_required
@decorators.phone_number_required
def test_handler(request, key: str):
    user = request.user
    participant = authtenticate_participant(user, key)
    if participant is not None:
        test = participant.test
        context = Context.get_context()
        context['participant'] = participant
        if not (participant.has_submitted or test.timer.has_ended()):
            timer: models.TestTimer = test.timer
            context['timer'] = timer 
            if timer.has_started:
                if request.POST:
                    participant.has_submitted = True
                    participant.save()
                else:
                    context['answer_paper'] = participant.get_answer_paper()
                    return render(request, 'tests/answer_paper.html', context)
            else: return render(request, 'tests/waiting_room.html', context)
        evaluator = engine.TestEvaluator(participant)
        context['short_report'] = evaluator.get_short_report_list()
        context['suggestions'] = evaluator.suggestions()
        return render(request, 'tests/result.html', context)
    return redirect('nope')      


@decorators.login_required
@decorators.phone_number_required
def all_tests(request):
    context = Context.get_context()
    timers = models.TestTimer.objects.filter(
        test__in=[part.test for part in models.TestParticipant.objects.filter(user=request.user) if part.has_ended]
        ).order_by('-start_datetime')
    context['timers'] = timers
    context['timers_count'] = timers.count()
    return render(request, 'tests/all_tests.html', context)


@decorators.login_required
@decorators.phone_number_required
def test_report(request, key: str):
    test = models.Test.objects.get(key=key)
    participant = models.TestParticipant.objects.get(test=test, user=request.user)
    evaluator = engine.TestEvaluator(participant)
    context = Context.get_context()
    context['short_report'] = evaluator.get_short_report_list()
    context['suggestions'] = evaluator.suggestions()
    return render(request, 'tests/result.html', context)