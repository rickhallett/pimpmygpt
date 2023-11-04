import os
import json
import threading
from urllib import request as py_request
from flask import Blueprint
from flask import render_template
from flask import request
from werkzeug.exceptions import abort

from pimpmygpt.auth import login_required
from pimpmygpt.db import get_db

bp = Blueprint("gpt", __name__)


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

        result = None
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
        pass

    def create_prompt_taxonomy(self):
        return self.prompt_taxonomy


def decode_200_res(res):
    json_res = None
    try:
        json_res = json.JSONDecoder().decode(
            res)['choices'][0]['message']['content']
    except BaseException as ex:
        print(ex)

    return json_res


def load_gpt_bg():
    with open(os.path.join(os.path.dirname(__file__), "prompt_taxonomy.txt")) as file:
        prompt_taxonomy = ''.join(file.readlines())

    with GPTRequestContextManager(prompt_taxonomy) as res:
        response = decode_200_res(res)
        print("load-gpt:", response)


@bp.route('/prompt')
@login_required
def prompt():
    """Show initial gpt page"""
    load_gpt_thread = threading.Thread(target=load_gpt_bg)
    load_gpt_thread.start()

    return render_template('gpt/prompt.html')


@bp.route('/')
def index():
    """Info on prompt engineering"""
    return render_template('gpt/index.html')


@bp.route('/enhance', methods=["POST"])
@login_required
def enhance():
    """Enhance prompt with GPT-3.5 Turbo"""
    prompt_input = request.form['prompt-input']
    prompt_category = request.form['main-category']
    prompt_subcategory = request.form['last-selected']

    initial_prompt = f"""Topic: {prompt_input}, category: {prompt_category}, subcategory: {prompt_subcategory}. 
    Please take the topic and create an enhanced prompt based on the category and subcategory. 
    Be as detailed as possible. In the response, do not include anything but the enhanced prompt.
    """

    with GPTRequestContextManager(initial_prompt) as res:
        enhanced_prompt = decode_200_res(res)

    return render_template('gpt/prompt.html',
                           initial_prompt=prompt_input,
                           category=prompt_category,
                           subcategory=prompt_subcategory,
                           enhanced_prompt=enhanced_prompt.strip(),
                           gpt_response=None)


@bp.route('/answer', methods=['POST'])
@login_required
def answer():
    """Handle enhanced response with GPT-3.5 Turbo"""
    prompt_input = request.form['prompt-input']
    prompt_category = request.form['main-category']
    prompt_subcategory = request.form['last-selected']
    enhanced_prompt = request.form['enhanced-prompt-input']

    with GPTRequestContextManager(enhanced_prompt) as res:
        gpt_response = decode_200_res(res)

    return render_template('gpt/prompt.html',
                           initial_prompt=prompt_input,
                           category=prompt_category,
                           subcategory=prompt_subcategory,
                           enhanced_prompt=enhanced_prompt,
                           gpt_response=gpt_response)
