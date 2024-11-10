import time
from django.shortcuts import render, redirect
from . import engine, models, operations as ops
from utils import constants as const, decorators
from utils.global_context import Context
from .operations import authtenticate_participant


@decorators.login_required
def quick_test(request):
    user = request.user
    if user.is_authenticated:
        chapters = ops.get_quick_syllabus_chapters()
        bulk = models.QuestionMetaData.objects.filter(chapter__in=chapters)
        participant = engine.start_exam(bulk, 20, user)
        return redirect('/test/'+participant.test.key)


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
        context['short_report'] = evaluator.get_short_report()
        context['suggestions'] = evaluator.suggestions()
        return render(request, 'tests/result.html', context)
    return redirect('nope')      
    
