# -*- code: utf-8 -*-
from __future__ import unicode_literals

import os
from flask import Flask 


__all__ = ['StudioFlask']


class StudioFlask(Flask):
	""" StudioFlask """
	def __init__(self, *args, **kwargs):
		super(StudioFlask, self).__init__(*args, **kwargs)
		config_path = os.path.join(self.root_path, 'config', 'development.pycfg')
		self.config.from_pyfile(config_path)
		self.secret_key = '\x94\xabM\x8c\xc8\r_x#\x06\x8ac\x99\xf5/\x83\xe7\xce\x04\x80XVs\xbe'

		# Function to easily find your assets
		# In your template use <link rel=stylesheet href="{{ static('filename') }}">

		with self.app_context():
			from . import filters  # noqa pyflakes:ignore
			from . import helpers

			self.jinja_env.globals.update(
					versioning=helpers.versioning,
				)
