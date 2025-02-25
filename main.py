import os
import struct
import wave

from openai import OpenAI
from pvrecorder import PvRecorder
from playsound import playsound
from IPython.display import Image, display

# silence deprecation warning
import warnings
import time
import csv
warnings.filterwarnings ( "ignore", category = DeprecationWarning )
client = OpenAI ( api_key = "" )


class Chatbot:
    def __init__(self, client,log_file='odpowiedzi.csv'):
        self.client = client
        self.context = [
            {"role": "system", "content": "assistant"},
        ]
        self.log_file = log_file
        self._init_log_file ( )

    def _init_log_file(self):
        if not os.path.isfile ( self.log_file ):
            with open ( self.log_file, mode = 'w' ) as csvfile:
                fieldnames=(
                    ['Model', 'Prompt', 'Response', 'Prompt Tokens', 'Completion Tokens', 'Total Tokens', 'Response Time (ms)'] )

                writer = csv.DictWriter ( csvfile,fieldnames=fieldnames )
                writer.writeheader ( )

    def chat(self, message,aimodel):
        self.context.append (
            {"role": "user", "content": message}
        )

        start_time = time.time ( )
        response = self.client.chat.completions.create (
            model = aimodel,
            messages = self.context
        )

        end_time = time.time ( )

        response_content = response.choices[0].message.content
        self.context.append (
            {"role": "assistant", "content": response_content}
        )

        prompt_tokens = response.usage.prompt_tokens
        completion_tokens = response.usage.completion_tokens
        total_tokens = response.usage.total_tokens
        response_time = (end_time - start_time) * 1000

        self._log_response(message, response_content, aimodel, prompt_tokens, completion_tokens, total_tokens, response_time)
        print ( f'{prompt_tokens} prompt tokens counted by the OpenAI API.' )
        print ( f'{completion_tokens} completion_tokens.' )
        print ( f'{total_tokens} total_tokens.' )
        print ( f'Response time: {response_time:.2f} milliseconds' )
        print ( f'created: {response.created:.2f} milliseconds' )
        self.print_chat()

    def print_chat(self):
        for message in self.context:
            if message["role"] == "user":
                print ( f'USER: {message["content"]}' )
            elif message["role"] == "assistant":
                print ( f'BOT: {message["content"]}' )

    def _log_response(self, prompt, response, model, prompt_tokens, completion_tokens, total_tokens, response_time):
        with open(self.log_file, mode='a', newline='') as file:
            fieldnames = ['Model', 'Prompt', 'Response', 'Prompt Tokens', 'Completion Tokens', 'Total Tokens', 'Response Time (ms)']
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writerow({
                'Model': model,
                'Prompt': prompt,
                'Response': response,
                'Prompt Tokens': prompt_tokens,
                'Completion Tokens': completion_tokens,
                'Total Tokens': total_tokens,
                'Response Time (ms)': response_time
            })

def load_questions_from_csv( csv_file):
        questions = []
        with open ( csv_file, mode = 'r', newline = '' ) as file:
            reader = csv.reader ( file )
            for row in reader:
                questions.append ( row[0] )  # assuming each row has a single question in the first column
        return questions


if __name__ == "__main__":
    model_list = ["gpt-4o", "gpt-4-turbo", "gpt-4", "gpt-3.5-turbo-0125"]


    questions = load_questions_from_csv ( 'questions.csv' )
    for question in questions:
        chatbot = Chatbot ( client )
        chatbot.chat ( question, model_list[0] )
        print("\n")