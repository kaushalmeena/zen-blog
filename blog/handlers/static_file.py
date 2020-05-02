# static_file.py
"""Contains class defination for handler class StaticFileHandler."""

import logging

from webapp2 import RequestHandler
from mimetypes import guess_type
from os import getcwd
from os.path import join, isdir, abspath

# static directory
STATIC_DIR = './app/static'


class StaticFileHandler(RequestHandler):
    """Handler for static files required for the web app."""

    def get(self, path):
        """Serves static files in static folder."""

        file_path = abspath(join(STATIC_DIR, path))

        if isdir(file_path) or file_path.find(getcwd()) != 0:
            self.response.set_status(403)
            return

        try:
            file_type = guess_type(file_path)[0]
            file = open(file_path, 'r')
            self.response.headers['Content-Type'] = file_type
            self.response.out.write(file.read())
            file.close()
        except Exception:
            logging.exception(Exception)
            self.response.set_status(404)
