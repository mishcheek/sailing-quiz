from flask import Flask, render_template, request, redirect, url_for, session
import json
import random

app = Flask(__name__)
app.secret_key = "supersecretkey"

# Load quiz data
def load_questions():
    with open("questions.json", "r", encoding="utf-8") as file:
        return json.load(file)

questions_data = load_questions()
all_questions = [q for category in questions_data for q in category["questions"]]

@app.route("/")
def index():
    session.clear()
    session["score"] = 0
    session["question_index"] = 0
    session["questions"] = all_questions  # Use all questions instead of random sample
    return render_template("index.html")

@app.route("/quiz", methods=["GET", "POST"])
def quiz():
    if "questions" not in session:
        return redirect(url_for("index"))

    # Get current question using modulo to cycle through questions
    current_question = session["questions"][session["question_index"] % len(session["questions"])]
    
    if request.method == "POST":
        selected_answer = request.form.get("answer")
        correct_answer = current_question["answer"]
        is_correct = selected_answer == correct_answer

        if "answers" not in session:
            session["answers"] = []
        session["answers"].append({
            "question": current_question["question"],
            "selected_answer": selected_answer,
            "correct_answer": correct_answer,
            "is_correct": is_correct
        })

        if is_correct:
            session["score"] += 1
        session.modified = True

        # Show evaluation for the current question
        return render_template(
            "question.html",
            question=current_question,
            show_evaluation=True,
            selected_answer=selected_answer,
            correct_answer=correct_answer,
            is_correct=is_correct,
            options=current_question["options"]
        )

    # Handle next question
    if request.args.get('next'):
        session["question_index"] += 1
        session.modified = True
        
        # Get the new current question using modulo
        current_question = session["questions"][session["question_index"] % len(session["questions"])]
        
        # Show the new question without evaluation
        return render_template(
            "question.html",
            question=current_question,
            show_evaluation=False,
            options=current_question["options"]
        )

    # Initial question display
    return render_template(
        "question.html",
        question=current_question,
        show_evaluation=False,
        options=current_question["options"]
    )

@app.route('/result', methods=['GET', 'POST'])
def result():
    score = session.get("score", 0)
    total = session.get("question_index", 0)  # Use actual number of questions answered
    return render_template('result.html', score=score, total=total, result_page=True)
if __name__ == "__main__":
    app.run(debug=True)