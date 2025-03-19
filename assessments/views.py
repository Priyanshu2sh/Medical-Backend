import logging
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
from .models import MCQ


logger = logging.getLogger(__name__)

@csrf_exempt
def check_answers(request):
    """Check answers for multiple MCQs and return the final result"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)  # Parse JSON request
            selected_answers = data.get('answers', {})  # Get selected answers from frontend

            correct_answers_count = 0  # Track correct answers
            total_questions = len(selected_answers)  # Total submitted questions

            # Check each answer
            for mcq_id, selected_answer in selected_answers.items():
                try:
                    question = MCQ.objects.get(id=mcq_id)
                    if question.correct_answer == selected_answer:
                        correct_answers_count += 1  # Increase score if correct
                except MCQ.DoesNotExist:
                    logger.warning(f"Question ID {mcq_id} not found.")

            # Return result summary
            return JsonResponse({
                "total_questions": total_questions,
                "correct_answers": correct_answers_count,
                "score": f"{correct_answers_count}/{total_questions}"
            })

        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON data"}, status=400)

            
def get_mcq_questions(request):
    """API to get 40 random MCQ questions"""
    questions = MCQ.get_random_questions()
    logger.info(f"Fetched {len(questions)} random MCQs")

    data = [
        {
            "id": q.id,
            "question": q.question,
            "options": [q.option1, q.option2, q.option3, q.option4],
        }
        for q in questions
    ]
    return JsonResponse({"questions": data})


# def check_answer(request, mcq_id):
#     """Check if the selected answer is correct"""
#     if request.method == 'POST':
#         selected_answer = request.POST.get('selected_answer')
#         try:
#             question = MCQ.objects.get(id=mcq_id)
#             is_correct = question.correct_answer == selected_answer
#             return JsonResponse({"correct": is_correct})
#         except MCQ.DoesNotExist:
#             return JsonResponse({"error": "Question not found"}, status=404)



