from .models import (
    AdmissionTest,
    University,
    QuestionMetaData,
    Appearance,
    Question,
    Passage,
    Chapter
)

class QBFilter:
    
    def __init__(
        self,
        chapter: Chapter = [chap for chap in Chapter.objects.all()],
        admission_test: AdmissionTest = [admtest for admtest in AdmissionTest.objects.all()],
        unit: list = list(),
        
    ) -> None:
        pass
