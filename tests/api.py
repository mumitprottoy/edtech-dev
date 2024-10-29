from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from utils import decorators
from .operations import authtenticate_participant


@csrf_exempt
@decorators.api_login_required
def post_answer(request, key: str, answer_id: int, option_id: int) -> JsonResponse:
    try:
        user = request.user
        participant = authtenticate_participant(user, key)
        if participant is not None:
            answer = participant.answers.filter(id=answer_id)
            if answer.exists():
                answer = answer.first()
                if not participant.test.timer.has_ended():
                    if not answer.attempted:
                        answer.option_id = option_id
                        answer.save()
                        return JsonResponse({'success': True})
    except: pass
    return JsonResponse({'success': False})