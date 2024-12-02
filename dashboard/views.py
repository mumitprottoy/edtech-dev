from django.shortcuts import render, redirect
from utils import decorators, global_context
from tests import models, engine
from . import operations as ops


@decorators.login_required
@decorators.phone_number_required
def dashboard(request):
    context = global_context.Context.get_context()
    participant = models.TestParticipant.objects.filter(user=request.user)
    if participant.exists():
        participant = participant.last()
        evaluator = engine.TestEvaluator(participant)
        context['short_report'] = evaluator.get_short_report_list()
        context['participant'] = participant
    context.update(ops.chapter_progress(request.user))
    return render(request, 'dashboard/dashboard.html', context)

                       
@decorators.login_required
@decorators.phone_number_required
def detailed_report(request, key: str):
    test = models.Test.objects.filter(key=key)
    if test.exists():
        test = test.first()
        participant = models.TestParticipant.objects.get(
            user=request.user, test=test)
        context = global_context.Context.get_context()
        context['participant'] = participant
        from tests import engine
        evaluator = engine.TestEvaluator(participant)
        context['solved_ans_sheet'] = evaluator.get_solved_ans_sheet()
        return render(request, 'dashboard/solved_ans_sheet.html', context)
    return redirect('nope')
                       
