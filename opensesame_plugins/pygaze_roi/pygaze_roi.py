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

from libopensesame.py3compat import *
from libopensesame.item import item
from libopensesame.exceptions import osexception
from libqtopensesame.items.qtautoplugin import qtautoplugin
from libqtopensesame._input.item_combobox import item_combobox
from libqtopensesame.items.feedpad import feedpad
from libqtopensesame.misc.translate import translation_context
_ = translation_context(u'pygaze_roi', category=u'plugin')


class pygaze_roi(item):

	description = u'Perform a ROI analysis based on sketchpad elements'

	def reset(self):

		self.var.sampling_rate = 100
		self.var.duration = 5000
		self.var.linked_sketchpad = u''

	def run(self):

		t0 = self.set_item_onset()
		g = self.coroutines()
		g.send(None)
		while self.clock.time() - t0 < self.var.duration:
			g.send(True)
		try:
			g.send(False)
		except StopIteration:
			pass

	def coroutine(self, coroutines=None):

		try:
			eyetracker = self.experiment.pygaze_eyetracker
		except AttributeError:
			raise osexception(
				u'pygaze_init must initialize the eye tracker first'
			)
		xc = self.experiment.var.width / 2
		yc = self.experiment.var.height / 2
		try:
			canvas = self.experiment.items[self.var.linked_sketchpad].canvas
		except AttributeError:
			raise osexception(
				u'%s does not have a canvas attribute'
				% self.var.linked_sketchpad
			)
		yield # End preparation
		samplenr = 0
		while True:
			# Only collect data every once in a while so that we don't poll the
			# eyetracker infinitely fast.
			if not self.clock.once_in_a_while(self.var.sampling_rate):
				alive = yield
				if not alive:
					break
				continue
			# Get a sample and check in which elements it is.
			x, y = eyetracker.sample()
			if self.var.uniform_coordinates:
				x -= xc
				y -= yc
			fixated = canvas.elements_at(x, y)
			for name, element in canvas:
				self.experiment.var.set(
					u'fix_%s_%04d' % (name, samplenr),
					1 if name in fixated else 0
				)
			samplenr += 1


class qtpygaze_roi(pygaze_roi, qtautoplugin):

	def __init__(self, name, experiment, script=None):

		pygaze_roi.__init__(self, name, experiment, script)
		qtautoplugin.__init__(self, __file__)

	def init_edit_widget(self):

		qtautoplugin.init_edit_widget(self)
		self._combobox_sketchpad = item_combobox(
			self.main_window,
			filter_fnc=lambda item:
				item in self.experiment.items
				and isinstance(
					self.experiment.items[item],
					feedpad
				)
		)
		self._combobox_sketchpad.activated.connect(self.apply_edit_changes)
		self.auto_combobox[u'linked_sketchpad'] = self._combobox_sketchpad
		self.add_control(
			label=_(u'Linked sketchpad'),
			widget=self._combobox_sketchpad,
			info=_('Elements define regions of interest')
		)

	def edit_widget(self):

		self._combobox_sketchpad.refresh()
		qtautoplugin.edit_widget(self)
