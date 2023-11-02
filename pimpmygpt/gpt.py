import os
import json
from urllib import request as py_request
from flask import Blueprint
from flask import flash
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from werkzeug.exceptions import abort

from pimpmygpt.auth import login_required
from pimpmygpt.db import get_db

bp = Blueprint("gpt", __name__, url_prefix="/gpt")


class GPTRequestContextManager():
    def __init__(self, prompt) -> None:
        self._prompt = prompt
        self._api_key = os.getenv("OPENAI_API_KEY")
        self._org = os.getenv("OPENAI_API_ORG")
        self._req_url = 'https://api.openai.com/v1/chat/completions'

    def __enter__(self):
        data = self.gen_request_data(self._prompt)
        headers = self.gen_headers()
        req = py_request.Request(self._req_url, data=data,
                                 headers=headers, method='POST')

        try:
            with py_request.urlopen(req) as response:
                result = response.read().decode()
        except BaseException as ex:
            print(ex)
        finally:
            py_request.urlcleanup()

        return result

    def __exit__(self, cls, value, tb):
        pass

    def gen_request_data(self, prompt):
        data = {
            "model": "gpt-4-0314",
            "messages": [{"role": "user", "content": f"{prompt}"}],
            "temperature": 0.7
        }

        return json.dumps(data).encode()

    def gen_headers(self):
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self._api_key}"
        }


class FileParser():
    def __init__(self) -> None:

        with open(os.path.join(os.path.dirname(__file__), "prepare_prompt.txt")) as file:
            self.prepare_prompt = ''.join(file.readlines())

    def convert_taxonomy_text_to_dict(self, lines):
        operations = {}
        current_category = None

        for line in lines:
            line = line.strip()
            if line.endswith(':'):
                current_category = line[:-1]
                operations[current_category] = {}
            elif line.startswith('-'):
                subcategory, description = line[1:].split(':', 1)
                operations[current_category][subcategory.strip()
                                             ] = description.strip()

        return operations


fp = FileParser()


def decode_200_res(res):
    return json.JSONDecoder().decode(res)['choices'][0]['message']['content']


def initial_request(initial_prompt):
    prompt = gen_prompt(initial_prompt)

    with GPTRequestContextManager(prompt) as result:
        return decode_200_res(result)


def gen_prompt(initial_prompt):
    topic, operation_type, subcategory_choice = initial_prompt
    return f"Topic: {topic}, category: {operation_type}, subcategory: {subcategory_choice}. Please take the topic and create an enhanced prompt based on the category and subcategory. Be as detailed as possible. In the response, do not include anything but the enhanced prompt."


def enhanced_request(enhanced_prompt):
    with GPTRequestContextManager(prompt=enhanced_prompt) as result:
        return decode_200_res(result)


@bp.route('/')
def index():
    """Show initial enhance page"""
    with GPTRequestContextManager(fp.prepare_prompt) as res:
        understood = decode_200_res(res)
        if understood == "understood":
            print("we're good to go")
    return render_template('gpt/index.html')


@bp.route('/enhance', methods=["POST"])
def enhance():
    """Enhance prompt with GPT-3.5 Turbo"""
    print(request.form)
    initial_prompt = gen_prompt(
        (request.form['prompt-input'], request.form['main_category'], request.form['last-selected']))
    print(initial_prompt)

    with GPTRequestContextManager(initial_prompt) as res:
        enhanced_request = decode_200_res(res)

    print(enhanced_request)

    with GPTRequestContextManager(enhanced_request) as res:
        final_response = decode_200_res(res)

    print(final_response)

    return render_template('gpt/index.html',
                           response=True,
                           initial_prompt=initial_prompt,
                           enhanced_category=request.form['main_category'],
                           enhanced_subcategory=request.form['last-selected'],
                           enhanced_prompt=enhanced_request,
                           enhanced_response=final_response)
