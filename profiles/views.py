from django.shortcuts import render
from utils import decorators, global_context
from . import models


@decorators.login_required
def add_phone_number(request):
    context = global_context.Context.get_context()
    if request.POST:
        phone_number = request.POST.get('phone_number')
        if hasattr(request.user, 'phone'):
            phone = models.Phone.objects.get(user=request.user)      
            phone.number = phone_number; phone.save()
        else: models.Phone(user=request.user, number=phone_number).save()
        context['success_msg'] = 'Phone number is saved.'
        return render(request, 'success_page.html', context)
    context['form_data'] = {
        'form_header': 'Add phone number',
        'input_type': 'tel',
        'input_name': 'phone_number',
        'input_placeholder': '01876XXXXXX',
        'submit_btn_text': 'Save'
    }
    return render(request, 'profiles/add_phone_number.html', context)
     