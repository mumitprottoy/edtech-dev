from .models import QuestionSet, QuestionSetMember, QuestionMetaData

def create_question_set(name: str, quantity: int) -> QuestionSet:
    question_set = QuestionSet(**locals()); question_set.save()
    return question_set


def add_question_set_member(
    question_set_id: int, metadata_id: int) -> QuestionSetMember:
    question_set = QuestionSet.objects.get(id=question_set_id)
    metadata = QuestionMetaData.objects.get(id=metadata_id)
    if (not QuestionSetMember.objects.filter(metadata=metadata).exists()
        and QuestionSetMember.objects.count() < question_set.quantity):
        member = QuestionSetMember(question_set=question_set, metadata=metadata)
        member.save()
        return member

         
    