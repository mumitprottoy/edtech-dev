from .keygen import KeyGen
from stuff import models

class Context:
    
    def __init__(self) -> None: pass
    
    @classmethod
    def get_context(cls):
        context = {
            'version': KeyGen().datetime_key(),
            'logo_url': models.Logo.objects.last().url
        }
        return context
        
        