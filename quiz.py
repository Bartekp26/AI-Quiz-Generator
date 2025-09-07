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

# Run the app in debug mode
if __name__ == "__main__":
    app.run(debug=True)
