from openai import OpenAI
import os


def test1():
    api_key = os.getenv("OPENAI_API_KEY")
    client = OpenAI(api_key=api_key)

    chat_completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "user", "content": "What is the capital of France?"},
        ]
    )
    print(chat_completion.choices[0].message.content)


if __name__ == '__main__':
    test1()
