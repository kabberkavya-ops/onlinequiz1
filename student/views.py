from django.shortcuts import render, redirect
from django.contrib import messages
from bson import ObjectId
from quiz.models import Exam, Question, Result, User


def student_required(view_func):
    def wrapper(request, *args, **kwargs):
        if not request.session.get('user_id') or request.session.get('user_role') != 'student':
            return redirect('login')
        return view_func(request, *args, **kwargs)
    wrapper.__name__ = view_func.__name__
    return wrapper


def get_student(request):
    return User.objects(id=ObjectId(request.session['user_id'])).first()


@student_required
def dashboard_view(request):
    student = get_student(request)
    results = list(Result.objects(student=student).order_by('-attempted_at'))
    attempted_exam_ids = [str(r.exam.id) for r in results]
    all_exams = Exam.objects()
    available_exams = sum(1 for e in all_exams if str(e.id) not in attempted_exam_ids)
    recent_results = results[:5]
    return render(request, 'student/dashboard.html', {
        'student': student,
        'available_exams': available_exams,
        'completed_exams': len(attempted_exam_ids),
        'recent_results': recent_results,
    })


@student_required
def exams_view(request):
    student = get_student(request)
    attempted_exam_ids = [str(r.exam.id) for r in Result.objects(student=student)]
    all_exams = list(Exam.objects())
    exams_data = []
    for exam in all_exams:
        questions = list(Question.objects(exam=exam))
        exams_data.append({
            'exam': exam,
            'attempted': str(exam.id) in attempted_exam_ids,
            'question_count': len(questions),
            'total_marks': sum(q.marks for q in questions),
        })
    return render(request, 'student/exams.html', {'exams_data': exams_data})


@student_required
def start_exam_view(request, exam_id):
    student = get_student(request)
    exam = Exam.objects(id=ObjectId(exam_id)).first()
    if not exam:
        messages.error(request, 'Exam not found.')
        return redirect('student-exams')
    if Result.objects(student=student, exam=exam).first():
        messages.error(request, 'You have already attempted this exam.')
        return redirect('student-exams')
    questions = list(Question.objects(exam=exam))
    total_marks = sum(q.marks for q in questions)
    section_counts = {
        'A': sum(1 for q in questions if q.section == 'A'),
        'B': sum(1 for q in questions if q.section == 'B'),
        'C': sum(1 for q in questions if q.section == 'C'),
    }
    return render(request, 'student/start_exam.html', {
        'exam': exam,
        'total_questions': len(questions),
        'total_marks': total_marks,
        'section_counts': section_counts,
    })


@student_required
def quiz_view(request, exam_id):
    student = get_student(request)
    exam = Exam.objects(id=ObjectId(exam_id)).first()
    if not exam:
        messages.error(request, 'Exam not found.')
        return redirect('student-exams')
    if Result.objects(student=student, exam=exam).first():
        messages.error(request, 'You have already attempted this exam.')
        return redirect('student-exams')
    questions = list(Question.objects(exam=exam).order_by('section'))

    if request.method == 'POST':
        obtained = 0
        section_marks = {'A': 0, 'B': 0, 'C': 0}
        total = sum(q.marks for q in questions)
        for q in questions:
            selected = request.POST.get(f'question_{str(q.id)}')
            if selected == q.correct_answer:
                obtained += q.marks
                section_marks[q.section] += q.marks
        Result(
            student=student, exam=exam,
            total_marks=total, obtained_marks=obtained,
            section_a_marks=section_marks['A'],
            section_b_marks=section_marks['B'],
            section_c_marks=section_marks['C'],
        ).save()
        return redirect('student-result', exam_id=exam_id)

    sections = {
        'A': [q for q in questions if q.section == 'A'],
        'B': [q for q in questions if q.section == 'B'],
        'C': [q for q in questions if q.section == 'C'],
    }
    return render(request, 'student/quiz.html', {
        'exam': exam,
        'questions': questions,
        'sections': sections,
        'duration_seconds': exam.duration * 60,
    })


@student_required
def result_view(request, exam_id):
    student = get_student(request)
    exam = Exam.objects(id=ObjectId(exam_id)).first()
    if not exam:
        messages.error(request, 'Exam not found.')
        return redirect('student-exams')
    result = Result.objects(student=student, exam=exam).first()
    if not result:
        return redirect('student-exams')
    return render(request, 'student/result.html', {'result': result, 'exam': exam})


@student_required
def my_results_view(request):
    student = get_student(request)
    results = list(Result.objects(student=student).order_by('-attempted_at'))
    return render(request, 'student/my_results.html', {'results': results, 'student': student})
