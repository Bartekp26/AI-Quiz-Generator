import os
from dotenv import load_dotenv
from flask import Flask, render_template, request
from openai import OpenAI

# Load environment variables from .env file (OPENAI_API_KEY)
load_dotenv()

# Initialize OpenAI client with the API key
client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Create the Flask app
app = Flask(__name__)

# Function to generate quiz questions
def generate_quiz(topic, num_questions=3):
    prompt = f"""
        Create {num_questions} quiz question about: {topic}
        Format:
        Question: ...
        A) ...
        B) ...
        C) ...
        D) ...
        Correct: X
        Question: ...
        A) ...
        B) ...
        C) ...
        D) ...
        Question: ...
        A) ...
        B) ...
        C) ...
        D) ...
    """

    # Call the OpenAI API
    response = client.responses.create(
        model="gpt-5-nano",
        input=prompt
    )

    # Read the generated text and remove extra spaces/newlines
    text = response.output_text.strip()

    # Split into separate questions
    questions = text.split("Question: ")

    # List for parsed questions
    questions_list = []

    # Iterate over all questions
    for q in questions[1:]:
        lines = q.strip().split("\n")
        question = lines[0].strip()
        a = lines[1].replace("A) ", "").strip()
        b = lines[2].replace("B) ", "").strip()
        c = lines[3].replace("C) ", "").strip()
        d = lines[4].replace("D) ", "").strip()
        correct = lines[5].replace("Correct: ", "").strip()

        # Add the parsed question to the list
        questions_list.append({
            "question": question,
            "a": a,
            "b": b,
            "c": c,
            "d": d,
            "correct": correct
        })

    return questions_list


# Home Page
@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        topic = request.form.get("topic")
        quiz = generate_quiz(topic)
        return render_template("quiz.html", quiz=quiz, topic=topic.capitalize())
    return render_template("index.html")

# Results Page
@app.route("/results", methods=["POST"])
def results():
    total_questions = int(request.form.get("total_questions"))
    user_answers = []
    correct_answers = []
    questions_text = []
    options = []
    
    # Collect user answers, correct answers, and question texts
    for i in range(total_questions):
        user_answers.append(request.form.get(f"answer{i}"))
        correct_answers.append(request.form.get(f"correct{i}"))
        questions_text.append(request.form.get(f"question_text{i}"))
        
        # Collect options for each question
        options.append({
            "A": request.form.get(f"option_a{i}"),
            "B": request.form.get(f"option_b{i}"),
            "C": request.form.get(f"option_c{i}"),
            "D": request.form.get(f"option_d{i}")
        })
    
    # Calculate score
    score = 0
    for i in range(total_questions):
        if user_answers[i] == correct_answers[i]:
            score += 1
    
    # Prepare results for display
    results = []
    for i in range(total_questions):
        results.append({
            "question": questions_text[i],
            "user_answer": user_answers[i],
            "user_answer_text": options[i][user_answers[i]],
            "correct_answer": correct_answers[i],
            "correct_answer_text": options[i][correct_answers[i]],
            "is_correct": user_answers[i] == correct_answers[i]
        })
    
    return render_template("results.html", 
                         results=results, 
                         score=score, 
                         total_questions=total_questions)


# Run the app in debug mode
if __name__ == "__main__":
    app.run(debug=True)
