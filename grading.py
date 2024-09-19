import json

def load_answer_key():
    with open("assets/answer_key.json", "r") as file:
        answer_key = json.load(file)
    return answer_key

def grade_student(answers, answer_key):
    score = 0
    for question, answer in enumerate(answers, start=1):
        if answer == answer_key[str(question)]:
            score += 1
    return score

def save_results(student_id, score, total_questions=50):
    with open("outputs/results.csv", "a") as file:
        file.write(f"{student_id},{score}/{total_questions}\n")
