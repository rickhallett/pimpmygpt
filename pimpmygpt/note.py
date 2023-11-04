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

bp = Blueprint("note", __name__, url_prefix='/note')


@bp.route("/")
def index():
    """Show all the notes, most recent first."""
    db = get_db()
    notes = db.execute(
        "SELECT p.id, title, body, created, author_id, username"
        " FROM note p JOIN user u ON p.author_id = u.id"
        " ORDER BY created DESC"
    ).fetchall()
    return render_template("note/index.html", notes=notes)


def get_note(id, check_author=True):
    """Get a note and its author by id.

    Checks that the id exists and optionally that the current user is
    the author.

    :param id: id of note to get
    :param check_author: require the current user to be the author
    :return: the note with author information
    :raise 404: if a note with the given id doesn't exist
    :raise 403: if the current user isn't the author
    """
    note = (
        get_db()
        .execute(
            "SELECT p.id, title, body, created, author_id, username"
            " FROM note p JOIN user u ON p.author_id = u.id"
            " WHERE p.id = ?",
            (id,),
        )
        .fetchone()
    )

    if note is None:
        abort(404, f"note id {id} doesn't exist.")

    if check_author and note["author_id"] != g.user["id"]:
        abort(403)

    return note


@bp.route("/create", methods=("GET", "POST"))
@login_required
def create():
    """Create a new note for the current user."""
    if request.method == "POST":
        title = request.form["title"]
        body = request.form["body"]
        error = None

        if not title:
            error = "Title is required."

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                "INSERT INTO note (title, body, author_id) VALUES (?, ?, ?)",
                (title, body, g.user["id"]),
            )
            db.commit()
            return redirect(url_for("note.index"))

    return render_template("note/create.html")


@bp.route("/<int:id>/update", methods=("GET", "POST"))
@login_required
def update(id):
    """Update a note if the current user is the author."""
    note = get_note(id)

    if request.method == "POST":
        title = request.form["title"]
        body = request.form["body"]
        error = None

        if not title:
            error = "Title is required."

        if error is not None:
            flash(error)
        else:
            db = get_db()
            db.execute(
                "UPDATE note SET title = ?, body = ? WHERE id = ?", (
                    title, body, id)
            )
            db.commit()
            return redirect(url_for("note.index"))

    return render_template("note/update.html", note=note)


@bp.route("/<int:id>/delete", methods=("POST",))
@login_required
def delete(id):
    """Delete a note.

    Ensures that the note exists and that the logged in user is the
    author of the note.
    """
    get_note(id)
    db = get_db()
    db.execute("DELETE FROM note WHERE id = ?", (id,))
    db.commit()
    return redirect(url_for("note.index"))
