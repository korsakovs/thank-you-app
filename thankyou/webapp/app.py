from flask import Flask, Response, render_template, request

from thankyou.dao import dao
from thankyou.utils.flask import flask_scoped_session


webapp = Flask(__name__, static_url_path='/app')
dao.set_scoped_session(flask_scoped_session(dao.session_maker, webapp))


@webapp.route("/app/status")
def webapp_status():
    return Response(
        status=200,
        response="IT WORKS!"
    )


@webapp.route("/app/image-uploading")
def image_uploading():
    return render_template("image-uploading-page.html")


@webapp.route("/app/image-uploading/file", methods=["POST"])
def image_uploading_file():
    if "file" not in request.files:
        raise Exception("File was not uploaded")
    file = request.files["file"]
    if file.filename == "":
        raise Exception("File was not uploaded - name was not found")
    return Response(status=200)


def wsgi():
    return webapp
