from __future__ import annotations

from django.db import transaction
from django.http import JsonResponse
from django.utils import timezone
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView

from apps.courses.models import (
    Course,
    CourseProgram,
    UserCourse,
    CourseComment,
    CourseProgramLessonTest,
    FinalTest,
    TestQuestion,
    TestQuestionOption,
    TestResult,
)
from django.db import connection
from rest_framework.exceptions import AuthenticationFailed, PermissionDenied


class IsAdmin(IsAuthenticated):
    """Permission class to check if user is admin"""

    def has_permission(self, request, view):
        if not request.user or not hasattr(request.user, "id"):
            raise AuthenticationFailed("Учетные данные не были предоставлены.")
        if not hasattr(request.user, "role"):
            raise PermissionDenied("Пользователь не имеет роли.")
        if request.user.role != "admin":
            raise PermissionDenied("Требуется роль администратора.")
        return True


class CoursesByStationView(APIView):
    permission_classes = [AllowAny]

    def get(self, _request, stationId: int):
        rows = list(
            Course.objects.filter(station_id=stationId, is_active=True)
            .order_by("-created_at")
            .values("id", "title", "description", "station_id", "duration_hours", "level", "is_active", "icon")
        )
        return JsonResponse({"data": rows})


class CourseDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, _request, courseId: str):
        course = Course.objects.filter(id=courseId).values().first()
        if not course:
            return JsonResponse({"error": "Course not found"}, status=404)
        programs = list(
            CourseProgram.objects.filter(station_id=course["station_id"]).order_by("order_index").values()
        )
        return JsonResponse({"course": course, "programs": programs})


class CourseProgramsView(APIView):
    permission_classes = [AllowAny]

    def get(self, _request, courseId: str):
        course = Course.objects.filter(id=courseId).values("station_id").first()
        if not course:
            return JsonResponse({"error": "Course not found"}, status=404)
        programs = list(CourseProgram.objects.filter(station_id=course["station_id"]).order_by("order_index").values())
        return JsonResponse({"data": programs})


class EnrollCourseView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, courseId: str):
        user_id = request.user.id
        now = timezone.now()
        with transaction.atomic():
            UserCourse.objects.get_or_create(
                user_id=user_id,
                course_id=courseId,
                defaults={
                    "progress_percent": 0,
                    "status": "in_progress",
                    "started_at": now,
                },
            )
        return JsonResponse({"success": True})


class MyEnrollmentsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user_id = request.user.id
        rows = list(
            UserCourse.objects.filter(user_id=user_id)
            .values("course_id", "progress_percent")
        )
        course_ids = [r["course_id"] for r in rows]
        course_map = {str(c["id"]): c for c in Course.objects.filter(id__in=course_ids).values("id", "title", "description", "station_id")}
        data = []
        for r in rows:
            c = course_map.get(str(r["course_id"]))
            if not c:
                continue
            data.append(
                {
                    "course_id": str(r["course_id"]),
                    "progress_percent": r["progress_percent"],
                    "title": c["title"],
                    "description": c["description"],
                    "station_id": c["station_id"],
                }
            )
        return JsonResponse({"data": data})


class CourseCommentsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        """Get comments for a specific lesson/topic/file"""
        station_id = request.GET.get("station_id")
        lesson_index = request.GET.get("lesson_index")
        topic_index = request.GET.get("topic_index")
        file_object_key = request.GET.get("file_object_key")

        if not station_id:
            return JsonResponse({"error": "station_id is required"}, status=400)

        query = CourseComment.objects.filter(station_id=station_id)

        if lesson_index is not None:
            query = query.filter(lesson_index=lesson_index)
        if topic_index is not None:
            query = query.filter(topic_index=topic_index)
        if file_object_key:
            query = query.filter(file_object_key=file_object_key)

        comments = list(
            query.values(
                "id",
                "user_id",
                "comment_text",
                "created_at",
                "updated_at",
                "file_object_key",
            )
            .order_by("-created_at")
        )
        
        # Get user info separately
        user_ids = list(set(str(c["user_id"]) for c in comments))
        from apps.accounts.models import User
        users_list = User.objects.filter(id__in=user_ids).values("id", "username", "full_name", "role")
        users = {str(u["id"]): u for u in users_list}

        # Format comments
        formatted_comments = []
        for comment in comments:
            user = users.get(str(comment["user_id"]), {})
            formatted_comments.append({
                "id": comment["id"],
                "userId": str(comment["user_id"]),
                "userName": user.get("full_name") or user.get("username", "Пользователь"),
                "userRole": user.get("role", "user"),
                "text": comment["comment_text"],
                "createdAt": comment["created_at"].isoformat() if comment["created_at"] else None,
                "fileObjectKey": comment["file_object_key"],
            })

        return JsonResponse({"data": formatted_comments})

    def post(self, request):
        """Create a new comment"""
        user_id = request.user.id
        station_id = request.data.get("station_id")
        lesson_index = request.data.get("lesson_index")
        topic_index = request.data.get("topic_index")
        file_object_key = request.data.get("file_object_key")
        comment_text = request.data.get("comment_text")

        if not station_id or not comment_text:
            return JsonResponse(
                {"error": "station_id and comment_text are required"}, status=400
            )

        comment = CourseComment.objects.create(
            user_id=user_id,
            station_id=station_id,
            lesson_index=lesson_index,
            topic_index=topic_index,
            file_object_key=file_object_key,
            comment_text=comment_text,
        )

        # Return created comment with user info
        from apps.accounts.models import User
        user = User.objects.filter(id=user_id).values("id", "username", "full_name", "role").first() or {}
        comment_data = CourseComment.objects.filter(id=comment.id).values(
            "id",
            "user_id",
            "comment_text",
            "created_at",
            "file_object_key",
        ).first()

        return JsonResponse({
            "data": {
                "id": comment_data["id"],
                "userId": str(comment_data["user_id"]),
                "userName": user.get("full_name") or user.get("username", "Пользователь"),
                "userRole": user.get("role", "user"),
                "text": comment_data["comment_text"],
                "createdAt": comment_data["created_at"].isoformat() if comment_data["created_at"] else None,
                "fileObjectKey": comment_data["file_object_key"],
            }
        }, status=201)


# ==================== Test Management Views ====================

class TestsListView(APIView):
    """List all tests (lesson and final) - Admin only"""
    permission_classes = [IsAdmin]

    def get(self, request):
        test_type = request.GET.get('type')  # 'lesson' or 'final' or None for all
        
        data = []
        
        try:
            if not test_type or test_type == 'lesson':
                # Get lesson tests with all fields
                lesson_tests = CourseProgramLessonTest.objects.all().values(
                    'id', 'title', 'questions_count', 'is_active', 'created_at', 'updated_at'
                )
                # Get additional fields and lesson_id using raw query
                from django.db import connection
                lesson_data_map = {}
                with connection.cursor() as cursor:
                    cursor.execute("""
                        SELECT id, course_program_lesson_id, 
                               COALESCE(description, '') as description,
                               COALESCE(passing_score, 70) as passing_score,
                               COALESCE(time_limit, 30) as time_limit,
                               attempts
                        FROM course_program_lesson_tests
                    """)
                    for row in cursor.fetchall():
                        lesson_data_map[row[0]] = {
                            'course_program_lesson_id': row[1],
                            'description': row[2] or '',
                            'passing_score': row[3] or 70,
                            'time_limit': row[4] or 30,
                            'attempts': row[5]
                        }
                
                for test in lesson_tests:
                    test_dict = dict(test)
                    additional_data = lesson_data_map.get(test['id'], {})
                    test_dict.update(additional_data)
                    test_dict['test_type'] = 'lesson'
                    test_dict['test_id'] = test['id']
                    data.append(test_dict)
            
            if not test_type or test_type == 'final':
                # Get final tests with all fields using raw query for consistency
                from django.db import connection
                final_tests_data = {}
                with connection.cursor() as cursor:
                    cursor.execute("""
                        SELECT id, course_program_id, title,
                               COALESCE(description, '') as description,
                               COALESCE(questions_count, 0) as questions_count,
                               COALESCE(passing_score, 70) as passing_score,
                               COALESCE(time_limit, 30) as time_limit,
                               attempts, is_active, created_at, updated_at
                        FROM final_tests
                    """)
                    for row in cursor.fetchall():
                        final_tests_data[row[0]] = {
                            'id': row[0],
                            'course_program_id': row[1],
                            'title': row[2],
                            'description': row[3] or '',
                            'questions_count': row[4] or 0,
                            'passing_score': row[5] or 70,
                            'time_limit': row[6] or 30,
                            'attempts': row[7],
                            'is_active': row[8],
                            'created_at': row[9],
                            'updated_at': row[10],
                            'test_type': 'final',
                            'test_id': row[0]
                        }
                
                data.extend(final_tests_data.values())
            
            return JsonResponse({'data': data})
        except Exception as e:
            import traceback
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"[TestsListView] Error: {e}", exc_info=True)
            from django.conf import settings
            error_response = {'error': str(e)}
            if settings.DEBUG:
                error_response['traceback'] = traceback.format_exc()
            return JsonResponse(error_response, status=500)


class TestDetailView(APIView):
    """Get test with questions and options - Admin only"""
    permission_classes = [IsAdmin]

    def get(self, request, test_id, test_type):
        # Get test
        if test_type == 'lesson':
            test = CourseProgramLessonTest.objects.filter(id=test_id).values().first()
        elif test_type == 'final':
            test = FinalTest.objects.filter(id=test_id).values().first()
        else:
            return JsonResponse({'error': 'Invalid test_type'}, status=400)
        
        if not test:
            return JsonResponse({'error': 'Test not found'}, status=404)
        
        # Get questions with options
        questions = TestQuestion.objects.filter(
            test_id=test_id, test_type=test_type
        ).order_by('order_index', 'id').values()
        
        questions_list = []
        for q in questions:
            options = TestQuestionOption.objects.filter(
                question_id=q['id']
            ).order_by('order_index', 'id').values('id', 'option_text', 'is_correct', 'order_index')
            
            # Find correct answer index
            correct_answer = None
            options_list = []
            for idx, opt in enumerate(options):
                options_list.append(opt['option_text'])
                if opt['is_correct']:
                    correct_answer = idx
            
            questions_list.append({
                'id': q['id'],
                'question': q['question'],
                'options': options_list,
                'correctAnswer': correct_answer,
                'points': q['points'],
                'image': q['image'],
                'explanation': q['explanation'],
                'order_index': q['order_index']
            })
        
        return JsonResponse({
            'test': {
                **test,
                'test_type': test_type,
                'questions': questions_list
            }
        })


class TestCreateView(APIView):
    """Create test - Admin only"""
    permission_classes = [IsAdmin]

    def post(self, request):
        test_type = request.data.get('test_type')  # 'lesson' or 'final'
        if test_type not in ['lesson', 'final']:
            return JsonResponse({'error': 'test_type must be "lesson" or "final"'}, status=400)
        
        title = request.data.get('title')
        if not title:
            return JsonResponse({'error': 'title is required'}, status=400)
        
        with transaction.atomic():
            if test_type == 'lesson':
                lesson_id = request.data.get('lesson_id')
                if not lesson_id:
                    return JsonResponse({'error': 'lesson_id is required for lesson test'}, status=400)
                
                test = CourseProgramLessonTest.objects.create(
                    lesson_id=lesson_id,
                    title=title,
                    description=request.data.get('description', ''),
                    passing_score=request.data.get('passing_score', 70),
                    time_limit=request.data.get('time_limit', 30),
                    attempts=request.data.get('attempts'),
                    is_active=request.data.get('is_active', True)
                )
            else:  # final
                course_program_id = request.data.get('course_program_id')
                if not course_program_id:
                    return JsonResponse({'error': 'course_program_id is required for final test'}, status=400)
                
                test = FinalTest.objects.create(
                    course_program_id=course_program_id,
                    title=title,
                    description=request.data.get('description', ''),
                    passing_score=request.data.get('passing_score', 70),
                    time_limit=request.data.get('time_limit', 30),
                    attempts=request.data.get('attempts'),
                    is_active=request.data.get('is_active', True)
                )
        
        return JsonResponse({'data': {'id': test.id, 'test_type': test_type}}, status=201)


class TestUpdateView(APIView):
    """Update test - Admin only"""
    permission_classes = [IsAdmin]

    def put(self, request, test_id, test_type):
        if test_type == 'lesson':
            test = CourseProgramLessonTest.objects.filter(id=test_id).first()
        elif test_type == 'final':
            test = FinalTest.objects.filter(id=test_id).first()
        else:
            return JsonResponse({'error': 'Invalid test_type'}, status=400)
        
        if not test:
            return JsonResponse({'error': 'Test not found'}, status=404)
        
        if 'title' in request.data:
            test.title = request.data['title']
        if 'description' in request.data:
            test.description = request.data.get('description', '')
        if 'passing_score' in request.data:
            test.passing_score = request.data['passing_score']
        if 'time_limit' in request.data:
            test.time_limit = request.data['time_limit']
        if 'attempts' in request.data:
            test.attempts = request.data.get('attempts')
        if 'is_active' in request.data:
            test.is_active = request.data['is_active']
        
        test.save()
        
        return JsonResponse({'data': {'id': test.id}})


class TestDeleteView(APIView):
    """Delete test - Admin only"""
    permission_classes = [IsAdmin]

    def delete(self, request, test_id, test_type):
        if test_type == 'lesson':
            test = CourseProgramLessonTest.objects.filter(id=test_id).first()
        elif test_type == 'final':
            test = FinalTest.objects.filter(id=test_id).first()
        else:
            return JsonResponse({'error': 'Invalid test_type'}, status=400)
        
        if not test:
            return JsonResponse({'error': 'Test not found'}, status=404)
        
        test.delete()
        return JsonResponse({'success': True})


class TestQuestionsUpdateView(APIView):
    """Update test questions - Admin only"""
    permission_classes = [IsAdmin]

    def put(self, request, test_id, test_type):
        questions = request.data.get('questions', [])
        
        if test_type not in ['lesson', 'final']:
            return JsonResponse({'error': 'Invalid test_type'}, status=400)
        
        with transaction.atomic():
            # Delete existing questions
            TestQuestion.objects.filter(test_id=test_id, test_type=test_type).delete()
            
            # Create new questions
            for q_idx, q_data in enumerate(questions):
                question = TestQuestion.objects.create(
                    test_id=test_id,
                    test_type=test_type,
                    question=q_data.get('question', ''),
                    points=q_data.get('points', 1),
                    image=q_data.get('image', ''),
                    explanation=q_data.get('explanation', ''),
                    order_index=q_idx
                )
                
                # Create options
                options = q_data.get('options', [])
                correct_answer = q_data.get('correctAnswer', 0)
                
                for opt_idx, opt_text in enumerate(options):
                    TestQuestionOption.objects.create(
                        question_id=question.id,
                        option_text=opt_text,
                        is_correct=(opt_idx == correct_answer),
                        order_index=opt_idx
                    )
            
            # Update questions_count
            questions_count = len(questions)
            if test_type == 'lesson':
                CourseProgramLessonTest.objects.filter(id=test_id).update(questions_count=questions_count)
            else:
                FinalTest.objects.filter(id=test_id).update(questions_count=questions_count)
        
        return JsonResponse({'success': True})


class LessonTestView(APIView):
    """Get lesson test by lesson_id - Authenticated users"""
    permission_classes = [IsAuthenticated]

    def get(self, request, lesson_id):
        try:
            # Get lesson test
            lesson_test = CourseProgramLessonTest.objects.filter(
                lesson_id=lesson_id,
                is_active=True
            ).order_by("id").first()
            
            if not lesson_test:
                return JsonResponse({'test': None})
            
            # Get questions with options
            questions = TestQuestion.objects.filter(
                test_id=lesson_test.id,
                test_type='lesson'
            ).order_by('order_index', 'id').values()
            
            questions_list = []
            for q in questions:
                options = TestQuestionOption.objects.filter(
                    question_id=q['id']
                ).order_by('order_index', 'id').values('id', 'option_text', 'is_correct', 'order_index')
                
                # Find correct answer index
                correct_answer = None
                options_list = []
                for idx, opt in enumerate(options):
                    options_list.append(opt['option_text'])
                    if opt['is_correct']:
                        correct_answer = idx
                
                questions_list.append({
                    'id': q['id'],
                    'question': q['question'],
                    'options': options_list,
                    'correctAnswer': correct_answer,
                    'points': q['points'] or 1,
                    'image': q['image'] or '',
                    'explanation': q['explanation'] or '',
                    'order_index': q['order_index']
                })
            
            # Format test data for TestQuiz component
            test_data = {
                'id': lesson_test.id,
                'title': lesson_test.title,
                'description': lesson_test.description or '',
                'questions': questions_list,
                'passingScore': lesson_test.passing_score or 70,
                'timeLimit': lesson_test.time_limit or 30,
                'attempts': lesson_test.attempts
            }
            
            return JsonResponse({'test': test_data})
        except Exception as e:
            import traceback
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"[LessonTestView] Error: {e}", exc_info=True)
            from django.conf import settings
            error_response = {'error': str(e)}
            if settings.DEBUG:
                error_response['traceback'] = traceback.format_exc()
            return JsonResponse(error_response, status=500)


class PublicTestView(APIView):
    """Get test by course_program_id - Public access"""
    permission_classes = [AllowAny]

    def get(self, request, course_program_id):
        try:
            # Get final test for course program
            final_test = FinalTest.objects.filter(
                course_program_id=course_program_id, 
                is_active=True
            ).order_by("id").first()
            
            if not final_test:
                return JsonResponse({'test': None})
            
            # Get questions with options
            questions = TestQuestion.objects.filter(
                test_id=final_test.id, 
                test_type='final'
            ).order_by('order_index', 'id').values()
            
            questions_list = []
            for q in questions:
                options = TestQuestionOption.objects.filter(
                    question_id=q['id']
                ).order_by('order_index', 'id').values('id', 'option_text', 'is_correct', 'order_index')
                
                # Find correct answer index
                correct_answer = None
                options_list = []
                for idx, opt in enumerate(options):
                    options_list.append(opt['option_text'])
                    if opt['is_correct']:
                        correct_answer = idx
                
                questions_list.append({
                    'id': q['id'],
                    'question': q['question'],
                    'options': options_list,
                    'correctAnswer': correct_answer,
                    'points': q['points'] or 1,
                    'image': q['image'] or '',
                    'explanation': q['explanation'] or '',
                    'order_index': q['order_index']
                })
            
            # Format test data for TestQuiz component
            test_data = {
                'id': final_test.id,
                'title': final_test.title,
                'description': final_test.description or '',
                'questions': questions_list,
                'passingScore': final_test.passing_score or 70,
                'timeLimit': final_test.time_limit or 30,
                'attempts': final_test.attempts
            }
            
            return JsonResponse({'test': test_data})
        except Exception as e:
            import traceback
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"[PublicTestView] Error: {e}", exc_info=True)
            from django.conf import settings
            error_response = {'error': str(e)}
            if settings.DEBUG:
                error_response['traceback'] = traceback.format_exc()
            return JsonResponse(error_response, status=500)


class TestResultsListView(APIView):
    """List test results - Admin only"""
    permission_classes = [IsAdmin]

    def get(self, request):
        test_id = request.GET.get('test_id')
        test_type = request.GET.get('test_type')
        user_id = request.GET.get('user_id')
        
        query = TestResult.objects.all()
        
        if test_id:
            query = query.filter(test_id=test_id)
        if test_type:
            query = query.filter(test_type=test_type)
        if user_id:
            query = query.filter(user_id=user_id)
        
        results = list(query.order_by('-completed_at').values(
            'id', 'test_id', 'test_type', 'user_id', 'score', 'is_passed',
            'correct_answers', 'total_questions', 'time_spent', 'completed_at'
        ))
        
        # Get user info
        from apps.accounts.models import User
        user_ids = list(set(str(r['user_id']) for r in results))
        users = {str(u['id']): u for u in User.objects.filter(id__in=user_ids).values('id', 'username', 'full_name')}
        
        # Format results
        formatted_results = []
        for r in results:
            user = users.get(str(r['user_id']), {})
            formatted_results.append({
                **r,
                'user_name': user.get('full_name') or user.get('username', 'Unknown')
            })
        
        return JsonResponse({'data': formatted_results})


class TestResultDetailView(APIView):
    """Get test result details - Admin only"""
    permission_classes = [IsAdmin]

    def get(self, request, result_id):
        result = TestResult.objects.filter(id=result_id).values().first()
        if not result:
            return JsonResponse({'error': 'Result not found'}, status=404)
        
        from apps.accounts.models import User
        user = User.objects.filter(id=result['user_id']).values('id', 'username', 'full_name').first() or {}
        
        return JsonResponse({
            'data': {
                **result,
                'user_name': user.get('full_name') or user.get('username', 'Unknown')
            }
        })


class TestResultCreateView(APIView):
    """Create test result - Authenticated users"""
    permission_classes = [IsAuthenticated]

    def post(self, request):
        test_id = request.data.get('test_id')
        test_type = request.data.get('test_type')
        score = request.data.get('score')
        is_passed = request.data.get('is_passed', False)
        correct_answers = request.data.get('correct_answers', 0)
        total_questions = request.data.get('total_questions', 0)
        time_spent = request.data.get('time_spent')  # in seconds
        answers_data = request.data.get('answers_data')  # JSON with user answers
        
        if not test_id or not test_type:
            return JsonResponse({'error': 'test_id and test_type are required'}, status=400)
        
        if test_type not in ['lesson', 'final']:
            return JsonResponse({'error': 'test_type must be "lesson" or "final"'}, status=400)
        
        if score is None:
            return JsonResponse({'error': 'score is required'}, status=400)
        
        # Get user ID from request
        user_id = request.user.id
        
        # Check if test exists
        if test_type == 'final':
            test = FinalTest.objects.filter(id=test_id, is_active=True).first()
        else:
            test = CourseProgramLessonTest.objects.filter(id=test_id, is_active=True).first()
        
        if not test:
            return JsonResponse({'error': 'Test not found or inactive'}, status=404)
        
        # Check attempts limit
        if test.attempts is not None:
            user_attempts = TestResult.objects.filter(
                test_id=test_id,
                test_type=test_type,
                user_id=user_id
            ).count()
            
            if user_attempts >= test.attempts:
                return JsonResponse({
                    'error': f'Превышен лимит попыток ({test.attempts}). Вы уже использовали все доступные попытки.'
                }, status=400)
        
        # Create test result
        result = TestResult.objects.create(
            test_id=test_id,
            test_type=test_type,
            user_id=user_id,
            score=score,
            is_passed=is_passed,
            correct_answers=correct_answers,
            total_questions=total_questions,
            time_spent=time_spent,
            answers_data=answers_data
        )
        
        return JsonResponse({
            'data': {
                'id': result.id,
                'test_id': result.test_id,
                'test_type': result.test_type,
                'score': result.score,
                'is_passed': result.is_passed,
                'correct_answers': result.correct_answers,
                'total_questions': result.total_questions,
                'time_spent': result.time_spent,
                'completed_at': result.completed_at.isoformat() if result.completed_at else None
            }
        }, status=201)


class UserTestResultsView(APIView):
    """Get user's test results for a specific test - Authenticated users"""
    permission_classes = [IsAuthenticated]

    def get(self, request, test_id, test_type):
        if test_type not in ['lesson', 'final']:
            return JsonResponse({'error': 'Invalid test_type'}, status=400)
        
        user_id = request.user.id
        
        results = TestResult.objects.filter(
            test_id=test_id,
            test_type=test_type,
            user_id=user_id
        ).order_by('-completed_at').values(
            'id', 'score', 'is_passed', 'correct_answers', 
            'total_questions', 'time_spent', 'completed_at'
        )
        
        return JsonResponse({
            'data': list(results),
            'total_attempts': len(results)
        })


