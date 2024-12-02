from django.shortcuts import render, redirect
from utils.global_context import Context
from utils import decorators
from stuff import models

@decorators.phone_number_required
def _home(request):
    context = Context.get_context()
    context['primary_copy_image'] = models.PrimaryImageCopy.objects.last()
    copies = list(models.MainCopy.objects.all())
    context.update({'copies': [{'n': str(i+1), 'copy': copies[i]} for i in range(len(copies))]}) 
    return render(request, 'home/home.html', context=context)

def pp(request):
    from stuff.models import ProfilePictureURL as URL
    context = {'urls': URL.objects.all()}
    return render(request, 'pics.html', context)


def test_json(request):
    if request.POST:
        _json = request.POST.get('json')
        import json
        _dict = json.loads(_json)
        print(type(_dict))
        print(_dict)
    return render(request, 'home/test_json.html')


def nope(request):
    return render(request, 'nope.html', context=Context.get_context())