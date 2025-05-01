from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.db.models import F
from .models import Exercise, Category
import json
from datetime import datetime



def exercise_list(request):
    """Display a list of all available exercises organized by categories."""
    # Get categories with their exercises
    categories = Category.objects.all().prefetch_related('exercises').order_by('order', 'name')
    
    # Get any exercises without a category
    uncategorized_exercises = Exercise.objects.filter(category__isnull=True).order_by('order', 'id')
    
    # Get solved exercise IDs from session
    solved_exercises = request.session.get('solved_exercises', [])
    
    # Initialize viewed_exercises in session if not exists
    if 'viewed_exercises' not in request.session:
        request.session['viewed_exercises'] = []
    
    # Calculate total exercises for progress display
    total_exercises = uncategorized_exercises.count()
    for category in categories:
        total_exercises += category.exercises.count()
    
    # Debug info
    print(f"Exercise list view - solved exercises: {solved_exercises}")
    print(f"Total exercises: {total_exercises}")
    
    context = {
        'categories': categories,
        'uncategorized_exercises': uncategorized_exercises,
        'solved_exercises': solved_exercises,
        'total_exercises': total_exercises,
    }
    return render(request, 'exercises/exercise_list.html', context)


def exercise_detail(request, pk):
    """Display a specific exercise to solve."""
    exercise = get_object_or_404(Exercise, pk=pk)
    
    # Get solved exercise IDs from session
    solved_exercises = request.session.get('solved_exercises', [])
    is_solved = pk in solved_exercises
    
    # Initialize viewed_exercises in session if not exists
    if 'viewed_exercises' not in request.session:
        request.session['viewed_exercises'] = []
    
    # Get solution if available
    solutions = request.session.get('solutions', {})
    solution = solutions.get(str(pk), None)
    
    # Get sanitizers for placeholders
    sanitizers = exercise.placeholder_set.all()
    
    context = {
        'exercise': exercise,
        'is_solved': is_solved,
        'solution': solution,
        'sanitizers': sanitizers,
    }
    return render(request, 'exercises/exercise_detail.html', context)


@require_http_methods(["POST"])
def mark_exercise_solved(request, pk):
    """Mark an exercise as solved in the session."""
    # Get the exercise
    exercise = get_object_or_404(Exercise, pk=pk)
    
    # Get or initialize the solved_exercises list in the session
    solved_exercises = request.session.get('solved_exercises', [])
    
    # Debug logging
    print(f"Marking exercise {pk} as solved")
    print(f"Current solved exercises: {solved_exercises}")
    print(f"Request method: {request.method}")
    
    # Add the exercise ID if not already present
    if pk not in solved_exercises:
        # Increment solve count
        exercise.solve_count += 1
        exercise.save(update_fields=['solve_count'])
        
        solved_exercises.append(pk)
        request.session['solved_exercises'] = solved_exercises
        
        # Store the solution if provided
        try:
            data = json.loads(request.body)
            print(f"Received data: {data}")
            
            if 'solution' in data:
                # Store solutions in the session (using a dictionary with exercise IDs as keys)
                solutions = request.session.get('solutions', {})
                solutions[str(pk)] = {
                    'inputs': data['solution'],
                    'solvedAt': datetime.now().isoformat()
                }
                request.session['solutions'] = solutions
                
                print(f"Stored solution for exercise {pk}")
        except (ValueError, KeyError, json.JSONDecodeError) as e:
            # If there's any error parsing the JSON, log it
            print(f"Error processing solution data: {str(e)}")
        
        # Ensure the session is saved
        request.session.modified = True
        print(f"Session saved. New solved exercises: {request.session.get('solved_exercises', [])}")
    else:
        print(f"Exercise {pk} was already marked as solved")
    
    return JsonResponse({
        'success': True, 
        'exerciseId': pk,
        'stats': {
            'views': exercise.view_count,
            'solves': exercise.solve_count
        }
    })


@require_http_methods(["POST"])
def mark_exercise_viewed(request, pk):
    """Track that an exercise was viewed (once per session)."""
    # Get the exercise
    exercise = get_object_or_404(Exercise, pk=pk)
    
    # Initialize viewed_exercises in session if not exists
    if 'viewed_exercises' not in request.session:
        request.session['viewed_exercises'] = []
    
    viewed_exercises = request.session['viewed_exercises']
    
    # Only increment the view count if this is the first view in this session
    if pk not in viewed_exercises:
        # Add to viewed exercises
        viewed_exercises.append(pk)
        request.session['viewed_exercises'] = viewed_exercises
        request.session.modified = True
        
        # Increment view count - using F() to avoid race conditions
        Exercise.objects.filter(pk=pk).update(view_count=F('view_count') + 1)
        
        # Get updated count
        exercise.refresh_from_db()
    
    return JsonResponse({
        'success': True,
        'exerciseId': pk,
        'stats': {
            'views': exercise.view_count,
            'solves': exercise.solve_count
        }
    })
