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
QUESTION_LIMIT = 10  # Limit to 15 questions per session

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

    if request.method == "POST":
        selected_answer = request.form.get("answer")
        correct_answer = session["questions"][session["question_index"]]["answer"]

        # Store the answer in session to use in results
        if "answers" not in session:
            session["answers"] = []
        session["answers"].append({
            "question": session["questions"][session["question_index"]]["question"],
            "selected_answer": selected_answer,
            "correct_answer": correct_answer,
            "is_correct": selected_answer == correct_answer
        })

        if selected_answer == correct_answer:
            session["score"] += 1

        session["question_index"] += 1

        if session["question_index"] >= QUESTION_LIMIT:
            return redirect(url_for("result"))

        return redirect(url_for("quiz"))

    question = session["questions"][session["question_index"]]
    return render_template("question.html", question=question, index=session["question_index"] + 1, total=QUESTION_LIMIT)

@app.route('/result', methods=['GET', 'POST'])
def result():
    score = session.get("score", 0)
    total = QUESTION_LIMIT
    return render_template('result.html', score=score, total=total, result_page=True)
if __name__ == "__main__":
    app.run(debug=True)