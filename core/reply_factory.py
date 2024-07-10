from .constants import BOT_WELCOME_MESSAGE, PYTHON_QUESTION_LIST

def generate_bot_responses(message, session):
    bot_responses = []

    current_question_id = session.get("current_question_id")
    if not current_question_id:
        bot_responses.append(BOT_WELCOME_MESSAGE)

    success, error = record_current_answer(message, current_question_id, session)

    if not success:
        return [error]

    next_question, next_question_id = get_next_question(current_question_id, session)

    if next_question_id != -1:
        bot_responses.append(next_question)
    else:
        final_response = generate_final_response(session)
        bot_responses.append(final_response)

    session["current_question_id"] = next_question_id
    session.save()

    return bot_responses


def record_current_answer(answer, current_question_id, session):
    '''
    Validates and stores the answer for the current question to django session.
    '''
    questions = session.get('questions', {})
    if current_question_id is None or current_question_id not in questions:
        return False, "Invalid question ID."

    correct_answer = questions[current_question_id]['correct_answer']
    
    if 'answer' not in session:
        session['answer'] = {}
    
    session['answer'][current_question_id] = answer

    if 'score' not in session:
        session['score'] = 0

    if answer == correct_answer:
        session['score'] += 1
        
    return True, None


def get_next_question(current_question_id, session):
    '''
    Fetches the next question from the PYTHON_QUESTION_LIST based on the current_question_id.
    '''
    questions = session.get('questions', {})
    question_ids = list(questions.keys())
    
    if current_question_id is None:
        next_index = 0
    else:
        next_index = question_ids.index(current_question_id) + 1

    if next_index < len(question_ids):
        next_question_id = question_ids[next_index]
        next_question = questions[next_question_id]['question']
        return next_question, next_question_id
    else:
        return None, -1


def generate_final_response(session):
    '''
    Creates a final result message including a score based on the answers
    by the user for questions in the PYTHON_QUESTION_LIST.
    '''
    questions = session.get('questions', {})
    total_questions = len(questions)
    score = session.get('score', 0)

    return f"Quiz completed! You scored {score} out of {total_questions}."
