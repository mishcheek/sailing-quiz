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
QUESTION_LIMIT = 15  # Limit to 15 questions per session

@app.route("/")
def index():
    session.clear()
    session["score"] = 0
    session["question_index"] = 0
    session["questions"] = random.sample(all_questions, min(QUESTION_LIMIT, len(all_questions)))  # Limit to 15
    return render_template("index.html")

@app.route("/quiz", methods=["GET", "POST"])
def quiz():
    if "questions" not in session or session["question_index"] >= len(session["questions"]):
        return redirect(url_for("result"))

    current_question = session["questions"][session["question_index"]]
    
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
            index=session["question_index"] + 1,
            total=QUESTION_LIMIT,
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
        
        if session["question_index"] >= len(session["questions"]):
            return redirect(url_for("result"))
            
        # Get the new current question
        current_question = session["questions"][session["question_index"]]
        
        # Show the new question without evaluation
        return render_template(
            "question.html",
            question=current_question,
            index=session["question_index"] + 1,
            total=QUESTION_LIMIT,
            show_evaluation=False,
            options=current_question["options"]
        )

    # Initial question display
    return render_template(
        "question.html",
        question=current_question,
        index=session["question_index"] + 1,
        total=QUESTION_LIMIT,
        show_evaluation=False,
        options=current_question["options"]
    )

@app.route('/result', methods=['GET', 'POST'])
def result():
    score = session.get("score", 0)
    total = QUESTION_LIMIT
    return render_template('result.html', score=score, total=total, result_page=True)
if __name__ == "__main__":
    app.run(debug=True)