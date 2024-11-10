import json
from django.shortcuts import render, redirect
from . import models, operations as ops
from qb import models as qb_models
from utils import decorators, global_context


@decorators.login_required
def chapter_library(request):
    context = global_context.Context.get_context()
    context['current_level'] = ops.current_level(request.user)
    context['chapters'] = ops.get_chapter_lists_for_library(request.user)
    return render(request, 'library/chapter_library.html', context)
        

@decorators.login_required
def study(request, chapter_id: int):
    context = global_context.Context.get_context()
    chapter = qb_models.Chapter.objects.filter(id=int(chapter_id))
    if chapter.exists():
        user = request.user
        chapter = chapter.first()
        if not models.Topic.objects.filter(chapter=chapter).exists():
            return redirect(f'/practise/{chapter.id}')
        context['chapter'] = chapter
        learner = ops.get_learner(
            user=user, chapter=chapter)
        context['learner'] = learner
        level = learner.get_next_level()
        if level is not None:
            context['level'] = level
            if not level.is_completed:
                if request.POST:
                    level.is_completed = True; level.save()
                    return redirect(f'/study/{chapter_id}')
                context['show_progress_bar'] = context['show_form'] = True
                return render(request, 'library/study_topic.html', context)
            next_question = level.quiz.get_next_question()
            validator, package, buddhi = next_question.renderable_paper()
            request.session['buddhi'] = buddhi
            context['json_validator'] = 'const v = ' + json.dumps(validator)
            context['package'] = package
            context['quiz'] = level.quiz
            return render(request, 'library/quiz.html', context)
        return render(request, 'library/chapter_completed.html', context)
    return redirect('nope')    


@decorators.login_required
def all_topics(request, chapter_id: int):
    chapter = qb_models.Chapter.objects.filter(id=int(chapter_id))
    if chapter.exists():
        if models.Topic.objects.filter(chapter=chapter.first()).exists():
            context = global_context.Context.get_context()
            chapter = chapter.first()
            learner = models.Learner.get_or_create(
                user=request.user, chapter=chapter)
            context['level'] = learner.get_next_level()
            context['levels'] = learner.levels.all()
            return render(request, 'library/chapter_levels.html', context)
    return redirect('library')


@decorators.login_required
def study_topic(request, level_id:int):
    level = models.Level.objects.filter(id=int(level_id))
    if level.exists():
        level = level.first()
        if level.learner.user == request.user:
            context = global_context.Context.get_context()
            context['level'] = level
            return render(request, 'library/study_topic.html', context)
    return redirect('library')


@decorators.login_required
def practise_chapters(request):
    context = global_context.Context.get_context()
    context['chapter'] = qb_models.Chapter.objects.get(name='Preposition')
    return render(request, 'library/practise_chapters.html', context)

    