import logging
import threading

from flask import Flask
from greenlet import greenlet
from sqlalchemy.orm import scoped_session


class flask_scoped_session(scoped_session):
    """A :class:`~sqlalchemy.orm.scoping.scoped_session` whose scope is set to
    the Flask application context.
    """
    def __init__(self, session_factory, flask_app: Flask = None):
        def scope_func():
            try:
                return greenlet.getcurrent()
            except Exception as e:
                logging.debug(f"Can not retrieve greenlet.getcurrent: {e}")
                try:
                    return threading.get_ident()
                except Exception as e:
                    logging.debug(f"Can not retrieve threading.get_ident: {e}")
                    return "default"

        super(flask_scoped_session, self).__init__(session_factory, scopefunc=scope_func)

        if flask_app is not None:
            flask_app.scoped_session = self

            @flask_app.teardown_appcontext
            def remove_scoped_session(*_, **__):
                flask_app.scoped_session.remove()
