# -*- code: utf-8 -*-
from __future__ import unicode_literals

import os
from flask import Flask 
from .helpers import versioning


__all__ = ['StudioFlask']


class StudioFlask(Flask):
	""" StudioFlask """
	def __init__(self, *args, **kwargs):
		super(StudioFlask, self).__init__(*args, **kwargs)
		config_path = os.path.join(self.root_path, 'config', 'development.pycfg')
		self.config.from_pyfile(config_path)

		# Function to easily find your assets
		# In your template use <link rel=stylesheet href="{{ static('filename') }}">
		self.jinja_env.globals['versioning'] = versioning
