import json
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
    
    @classmethod
    def label_map(cls):
        labels = dict()
        for adm in AdmissionTest.objects.all():
            uni = University.objects.get(acronym=adm.acronym)
            if uni.acronym not in labels:
                labels[uni.acronym] = dict()
            for apr in Appearance.objects.filter(university=uni):
                unit = apr.unit; year = apr.year
                if not unit in labels[uni.acronym]:
                    labels[uni.acronym][unit] = [year]
                elif year not in labels[uni.acronym][unit]:            
                    labels[uni.acronym][unit].append(year)
        
        label_json = json.dumps(labels, indent=4, ensure_ascii=False)
        file = open('labels.txt','w', encoding='utf-8')
        file.write(label_json); file.close()