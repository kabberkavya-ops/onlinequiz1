from django.shortcuts import render, redirect
from django.contrib import messages
from bson import ObjectId
from quiz.models import Exam, Question, User, Result


def teacher_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.session.get('user_id') or request.session.get('user_role') != 'teacher':
            return redirect('login')
        return view_func(request, *args, **kwargs)
    wrapper.__name__ = view_func.__name__
    return wrapper


def get_teacher(request):
    return User.objects(id=ObjectId(request.session['user_id'])).first()


@teacher_required
def dashboard_view(request):
    teacher = get_teacher(request)
    exams = list(Exam.objects(teacher=teacher))
    total_questions = Question.objects(exam__in=exams).count()
    attempted_students = set()
    for exam in exams:
        for r in Result.objects(exam=exam):
            attempted_students.add(str(r.student.id))
    for exam in exams:
        exam._q_count = exam.question_count()
    return render(request, 'teacher/dashboard.html', {
        'teacher': teacher,
        'total_exams': len(exams),
        'total_questions': total_questions,
        'total_students': len(attempted_students),
        'exams': exams,
    })


@teacher_required
def add_exam_view(request):
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        duration = request.POST.get('duration', '').strip()
        if not title or not duration:
            messages.error(request, 'All fields required.')
        else:
            teacher = get_teacher(request)
            exam = Exam(title=title, duration=int(duration), teacher=teacher)
            exam.save()
            messages.success(request, f'Exam created!')
            return redirect('teacher-questions', exam_id=str(exam.id))
    return render(request, 'teacher/add_exam.html')


@teacher_required
def questions_view(request, exam_id):
    teacher = get_teacher(request)
    exam = Exam.objects(id=ObjectId(exam_id), teacher=teacher).first()
    if not exam:
        messages.error(request, 'Exam not found.')
        return redirect('teacher-dashboard')
    all_questions = list(Question.objects(exam=exam))
    section_data = {
        'A': [q for q in all_questions if q.section == 'A'],
        'B': [q for q in all_questions if q.section == 'B'],
        'C': [q for q in all_questions if q.section == 'C'],
    }
    total_marks = sum(q.marks for q in all_questions)
    return render(request, 'teacher/questions.html', {
        'exam': exam,
        'section_data': section_data,
        'total_marks': total_marks,
        'total_questions': len(all_questions),
    })


@teacher_required
def add_question_view(request, exam_id):
    teacher = get_teacher(request)
    exam = Exam.objects(id=ObjectId(exam_id), teacher=teacher).first()
    if not exam:
        messages.error(request, 'Exam not found.')
        return redirect('teacher-dashboard')
    if request.method == 'POST':
        question_text = request.POST.get('question_text', '').strip()
        option1 = request.POST.get('option1', '').strip()
        option2 = request.POST.get('option2', '').strip()
        option3 = request.POST.get('option3', '').strip()
        option4 = request.POST.get('option4', '').strip()
        correct_answer = request.POST.get('correct_answer', '')
        marks = int(request.POST.get('marks', 1))
        section = request.POST.get('section', 'A')
        if not all([question_text, option1, option2, option3, option4, correct_answer]):
            messages.error(request, 'All fields required.')
        else:
            Question(
                exam=exam, question_text=question_text,
                option1=option1, option2=option2, option3=option3, option4=option4,
                correct_answer=correct_answer, marks=marks, section=section,
            ).save()
            messages.success(request, 'Question added!')
            if request.POST.get('add_another'):
                return redirect('teacher-add-question', exam_id=exam_id)
            return redirect('teacher-questions', exam_id=exam_id)
    return render(request, 'teacher/add_question.html', {'exam': exam})


@teacher_required
def edit_question_view(request, question_id):
    question = Question.objects(id=ObjectId(question_id)).first()
    if not question or str(question.exam.teacher.id) != request.session['user_id']:
        messages.error(request, 'Question not found.')
        return redirect('teacher-dashboard')
    if request.method == 'POST':
        question.question_text = request.POST.get('question_text', '').strip()
        question.option1 = request.POST.get('option1', '').strip()
        question.option2 = request.POST.get('option2', '').strip()
        question.option3 = request.POST.get('option3', '').strip()
        question.option4 = request.POST.get('option4', '').strip()
        question.correct_answer = request.POST.get('correct_answer', '')
        question.marks = int(request.POST.get('marks', 1))
        question.section = request.POST.get('section', 'A')
        question.save()
        messages.success(request, 'Question updated!')
        return redirect('teacher-questions', exam_id=str(question.exam.id))
    return render(request, 'teacher/edit_question.html', {'question': question})


@teacher_required
def delete_question_view(request, question_id):
    question = Question.objects(id=ObjectId(question_id)).first()
    if question and str(question.exam.teacher.id) == request.session['user_id']:
        exam_id = str(question.exam.id)
        question.delete()
        messages.success(request, 'Question deleted.')
        return redirect('teacher-questions', exam_id=exam_id)
    messages.error(request, 'Question not found.')
    return redirect('teacher-dashboard')


@teacher_required
def delete_exam_view(request, exam_id):
    teacher = get_teacher(request)
    exam = Exam.objects(id=ObjectId(exam_id), teacher=teacher).first()
    if exam:
        Question.objects(exam=exam).delete()
        Result.objects(exam=exam).delete()
        exam.delete()
        messages.success(request, 'Exam deleted.')
    return redirect('teacher-dashboard')


@teacher_required
def exam_results_view(request, exam_id):
    teacher = get_teacher(request)
    exam = Exam.objects(id=ObjectId(exam_id), teacher=teacher).first()
    if not exam:
        messages.error(request, 'Exam not found.')
        return redirect('teacher-dashboard')
    results = list(Result.objects(exam=exam).order_by('-obtained_marks'))
    return render(request, 'teacher/exam_results.html', {'exam': exam, 'results': results})
