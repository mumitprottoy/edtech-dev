from django.shortcuts import render
from utils.global_context import Context

def payment_through_link(request, key:str):
    context = Context.get_context()
    if not request.user.is_authenticated:
        pass
    return render(request, 'payment/try.html', context)