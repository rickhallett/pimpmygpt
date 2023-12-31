import os
import json
import threading
from urllib import request as py_request
from flask import Blueprint
from flask import render_template
from flask import request
from flask import g
from flask import flash
from flask import jsonify
from werkzeug.exceptions import abort

from pimpmygpt.auth import login_required
from pimpmygpt.db import get_db
from pimpmygpt.pimp_scribbler import PimpScribbler

bp = Blueprint("gpt", __name__)
scribble = PimpScribbler()


class GPTRequestContextManager():
    def __init__(self, prompt, gpt_model) -> None:
        self._prompt = prompt
        self._api_key = os.getenv("OPENAI_API_KEY")
        self._org = os.getenv("OPENAI_ORG")
        self._req_url = 'https://api.openai.com/v1/chat/completions'
        self._gpt_model = gpt_model

    def __enter__(self):
        data = self.gen_request_data(self._prompt)
        headers = self.gen_headers()
        req = py_request.Request(self._req_url, data=data,
                                 headers=headers, method='POST')

        print("headers", headers)
        scribble.log.info((data, headers))
        result = None
        try:
            with py_request.urlopen(req) as response:
                result = response.read().decode()
                print(result)
        except BaseException as ex:
            print(ex)
            scribble.log.error(ex)
        finally:
            py_request.urlcleanup()

        return result

    def __exit__(self, cls, value, tb):
        pass

    def gen_request_data(self, prompt):
        data = {
            "model": f"{self._gpt_model}",
            "messages": [{"role": "user", "content": f"{prompt}"}],
            "temperature": 0.7
        }

        return json.dumps(data).encode()

    def gen_headers(self):
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self._api_key}",
            "OpenAI-Organization": f"{self._org}"
        }


def decode_200_res(res):
    json_res = None
    try:
        json_res = json.JSONDecoder().decode(
            res)['choices'][0]['message']['content']
    except BaseException as ex:
        scribble.log.error(ex)

    return json_res


def load_gpt_bg(gpt_model):
    with open(os.path.join(os.path.dirname(__file__), "prompt_taxonomy.txt")) as file:
        prompt_taxonomy = ''.join(file.readlines())

    with GPTRequestContextManager(prompt_taxonomy, gpt_model) as res:
        response = decode_200_res(res)


@bp.route('/prompt')
@login_required
def prompt():
    """Show initial gpt page"""
    gpt_model = "gpt-3.5-turbo"
    load_gpt_thread = threading.Thread(target=load_gpt_bg, args=[gpt_model])
    load_gpt_thread.start()

    return render_template('gpt/prompt.html')


@bp.route('/change-gpt-model', methods=["POST"])
@login_required
def load_gpt():
    gpt_model = request.json['gpt-model']
    load_gpt_thread = threading.Thread(target=load_gpt_bg, args=[gpt_model])
    load_gpt_thread.start()

    return jsonify("request received")


@bp.route('/prompts')
def prompts():
    """Show all the prompts as history"""
    db = get_db()
    prompts = db.execute(
        "SELECT p.id, model, initial, category, subcategory, created, enhanced, response, username"
        " FROM prompt p JOIN user u ON p.author_id = u.id"
        " ORDER BY created DESC"
    ).fetchall()
    return render_template('gpt/prompts.html', prompts=prompts)


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
    gpt_model = request.form['gpt-model']

    initial_prompt = f"""Topic: {prompt_input}, category: {prompt_category}, subcategory: {prompt_subcategory}. 
    Please take the topic and create an enhanced prompt based on the category and subcategory. 
    Be as detailed as possible. In the response, do not include anything but the enhanced prompt.
    """

    with GPTRequestContextManager(initial_prompt, gpt_model) as res:
        enhanced_prompt = decode_200_res(res)

    return render_template('gpt/prompt.html',
                           initial_prompt=prompt_input,
                           category=prompt_category,
                           subcategory=prompt_subcategory,
                           enhanced_prompt=enhanced_prompt,
                           gpt_model=gpt_model,
                           gpt_response=None)


@bp.route('/answer', methods=['POST'])
@login_required
def answer():
    """Handle enhanced response with GPT-3.5 Turbo"""
    prompt_input = request.form['prompt-input']
    prompt_category = request.form['main-category']
    prompt_subcategory = request.form['last-selected']
    enhanced_prompt = request.form['enhanced-prompt-input']
    gpt_model = request.form['gpt-model']

    with GPTRequestContextManager(enhanced_prompt, gpt_model) as res:
        gpt_response = decode_200_res(res)

    if gpt_response is not None:
        try:
            db = get_db()
            db.execute(
                "INSERT INTO prompt (model, initial, category, subcategory, enhanced, response, author_id) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (gpt_model, prompt_input, prompt_category, prompt_subcategory,
                 enhanced_prompt, gpt_response, g.user["id"])
            )
            db.commit()
        except db.Error as ex:
            flash(ex)

    return render_template('gpt/prompt.html',
                           initial_prompt=prompt_input,
                           category=prompt_category,
                           subcategory=prompt_subcategory,
                           enhanced_prompt=enhanced_prompt,
                           gpt_model=gpt_model,
                           gpt_response=gpt_response)
