from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from . import models


@csrf_exempt
def amar_onek_buddhi(request, gibberish: str):
    message = 'hoyeche'
    try:
        data = request.session['buddhi']
        ans = models.Answer.objects.get(
            id=int(data[gibberish]['id']))
        if data[gibberish]['is_correct']:
            ans.option_id = ans.question.options.get(
                is_correct=True).id
            ans.save()
        request.session['buddhi'] = None
    except Exception as e: message = str(e)
    return JsonResponse({'message': message})
        