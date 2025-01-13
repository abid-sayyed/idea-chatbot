from flask import Flask, render_template, request, jsonify
import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# External AI API details
API_KEY = os.getenv("AI_API_KEY")

# Configure generative AI API
genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        user_input = request.form.get("user_input", "").strip()
        try:

            if request.is_json:  # Handle the detailed suggestions request
                selected_ideas = request.get_json().get("selected_ideas", [])
                return fetch_detailed_suggestions(selected_ideas)

            # Prepare the prompt for project idea generation
            if not user_input:
                data = (
                    "Generate 3 short and crisp project ideas. Each idea should be clear and concise, like:\n\n"
                    "1. A meditation app with rewards.\n"
                    "2. Grocery delivery for special diets.\n"
                    "3. Subscription service for AI-generated art.\n\n"
                )
            else:
                data = (
                    f"Generate 3 short and crisp project ideas based on the following input: '{user_input}'. "
                    "Each idea should be clear and concise, like:\n\n"
                    "1. A meditation app with rewards.\n"
                    "2. Grocery delivery for special diets.\n"
                    "3. Subscription service for AI-generated art.\n\n"
                )

            response = model.generate_content(data)

            if response.text:
                project_idea = response.text
            else:
                project_idea = "Sorry, no idea could be generated."
            return jsonify({"idea": project_idea})

        except Exception:
            return jsonify({"idea": "Apologies, we are experiencing a server issue. Please try again later."})

    return render_template("index.html")


def fetch_detailed_suggestions(selected_ideas):
    prompt = """Based on the following project ideas, generate a detailed suggestion for each project, adhering to a well-structured and readable format. Use the following guidelines for presentation:

- Project Title : Use a large and bold heading style.
- Description : Provide a clear, comprehensive description of the project, outlining its purpose and key features.
- Key Features : Use bullet points to list unique or important aspects of the project.
- Technologies/Tools : Include a section for suggested tools, frameworks, or technologies.
- Potential Challenges : Highlight potential difficulties and how they might be addressed.

"""

    for idea in selected_ideas:
        prompt += f"- {idea}\n"
    try:
        def generate():
            response = model.generate_content(prompt, stream=True)
            for chunk in response:
                yield chunk.text

        return generate(), {"Content-Type": "text/plain"}

    except Exception:
        return ["Apologies, we are experiencing a server issue. Please try again later."]


if __name__ == "__main__":
    app.run(debug=True)
