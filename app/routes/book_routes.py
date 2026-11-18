from flask import Blueprint, render_template

book_bp = Blueprint("book", __name__)


@book_bp.route("/book")
def book():
    return render_template("book.html")