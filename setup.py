#!/usr/bin/env python
# coding=utf-8

"""
This file is part of OpenSesame.

OpenSesame is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

OpenSesame is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with OpenSesame.  If not, see <http://www.gnu.org/licenses/>.
"""

from setuptools import setup

setup(
	name='opensesame-plugin-pygaze_roi',
	version='0.1.0',
	description='ROI analysis plugin for OpenSesame and PyGaze',
	author='Sebastiaan Mathot',
	author_email='s.mathot@cogsci.nl',
	url='https://github.com/smathot/opensesame-plugin-pygaze_roi',
	# Classifiers used by PyPi if you upload the plugin there
	classifiers=[
		'Intended Audience :: Science/Research',
		'Topic :: Scientific/Engineering',
		'Environment :: MacOS X',
		'Environment :: Win32 (MS Windows)',
		'Environment :: X11 Applications',
		'License :: OSI Approved :: Apache Software License',
		'Programming Language :: Python :: 2',
	],
	data_files=[
		(
			'share/opensesame_plugins/pygaze_roi',
			[
				'opensesame_plugins/pygaze_roi/pygaze_roi.png',
				'opensesame_plugins/pygaze_roi/pygaze_roi_large.png',
				'opensesame_plugins/pygaze_roi/pygaze_roi.py',
				'opensesame_plugins/pygaze_roi/info.yaml',
			]
		),
	]
)
