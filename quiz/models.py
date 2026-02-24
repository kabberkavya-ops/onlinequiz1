from mongoengine import Document, StringField, IntField, DateTimeField, \
    ReferenceField, CASCADE
from datetime import datetime


class User(Document):
    name = StringField(max_length=100, required=True)
    email = StringField(max_length=200, required=True, unique=True)
    password = StringField(required=True)
    role = StringField(max_length=10, choices=['student', 'teacher'], required=True)
    created_at = DateTimeField(default=datetime.utcnow)

    meta = {'collection': 'users'}

    def __str__(self):
        return f"{self.name} ({self.role})"


class Exam(Document):
    title = StringField(max_length=200, required=True)
    duration = IntField(required=True, min_value=1)
    teacher = ReferenceField(User, reverse_delete_rule=CASCADE)
    created_at = DateTimeField(default=datetime.utcnow)

    meta = {'collection': 'exams'}

    def __str__(self):
        return self.title

    def get_questions(self):
        return Question.objects(exam=self)

    def question_count(self):
        return Question.objects(exam=self).count()

    def total_marks(self):
        return sum(q.marks for q in Question.objects(exam=self))

    def section_counts(self):
        questions = list(Question.objects(exam=self))
        return {
            'A': sum(1 for q in questions if q.section == 'A'),
            'B': sum(1 for q in questions if q.section == 'B'),
            'C': sum(1 for q in questions if q.section == 'C'),
        }


class Question(Document):
    exam = ReferenceField(Exam, reverse_delete_rule=CASCADE)
    question_text = StringField(max_length=1000, required=True)
    option1 = StringField(max_length=300, required=True)
    option2 = StringField(max_length=300, required=True)
    option3 = StringField(max_length=300, required=True)
    option4 = StringField(max_length=300, required=True)
    correct_answer = StringField(
        choices=['option1', 'option2', 'option3', 'option4'], required=True
    )
    marks = IntField(default=1, min_value=1)
    section = StringField(max_length=1, choices=['A', 'B', 'C'], default='A')

    meta = {'collection': 'questions'}

    def __str__(self):
        return self.question_text[:50]


class Result(Document):
    student = ReferenceField(User, reverse_delete_rule=CASCADE)
    exam = ReferenceField(Exam, reverse_delete_rule=CASCADE)
    total_marks = IntField(default=0)
    obtained_marks = IntField(default=0)
    section_a_marks = IntField(default=0)
    section_b_marks = IntField(default=0)
    section_c_marks = IntField(default=0)
    attempted_at = DateTimeField(default=datetime.utcnow)

    meta = {'collection': 'results'}

    def percentage(self):
        if self.total_marks == 0:
            return 0
        return round((self.obtained_marks / self.total_marks) * 100, 1)
