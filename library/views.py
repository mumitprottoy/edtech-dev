from django.shortcuts import render, redirect
from . import models, operations as ops
from utils import decorators, global_context

@decorators.login_required
def study(request, chapter_id: int):
    context = global_context.Context.get_context()
    chapter = models.Chapter.objects.filter(id=id(chapter_id))
    if chapter.exists():
        user = request.user
        chapter = chapter.first()
        context['chapter'] = chapter
        learner = models.Topic.objects.filter(
            user=user, chapter=chapter)
        if learner.exists():
            learner = learner.first()
            context['learner'] = learner
            level = ops.get_level(learner)
            if level is not None:
                context['level'] = level
                if not level.is_completed:
                    if request.POST:
                        level.is_completed = True; level.save()
                        return redirect(f'/study/{chapter_id}')
                    return render(request, 'library/study_topic.html', context)
                if request.POST:
                    return redirect(f'/study/{chapter_id}')
                context['question'] = level.quiz.get_next_question()
                return render(request, 'library/quiz.html', context)
            return render(request, 'library/chapter_completed.html', context)
    return redirect('nope')    
