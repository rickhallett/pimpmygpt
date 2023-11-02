from flask import Blueprint
from flask import flash
from flask import g
from flask import redirect
from flask import render_template
from flask import request
from flask import url_for
from werkzeug.exceptions import abort

from flaskr.auth import login_required
from flaskr.db import get_db

bp = Blueprint("gpt", __name__, url_prefix="/gpt")


@bp.route('/')
def index():
    """Show initial enhance page"""
    g.show = True
    return render_template('gpt/index.html')


@bp.route('/enhance', methods=["POST"])
def enhance():
    """Enhance prompt with GPT-3.5 Turbo"""
    return render_template('gpt/index.html', response=True, enhanced_category="reductive", enhanced_subcategory="summarization", enhanced_prompt="We improved you very much", enhanced_response="All your base are belong to us")
