import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(
  api_key=os.environ.get("OPENAI_API_KEY")
)

response = client.responses.create(
    model="gpt-5-nano",
    input="Write a one-sentence bedtime story about a pegasus."
)

print(response.output_text)