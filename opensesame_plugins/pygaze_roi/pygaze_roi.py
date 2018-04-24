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


		objects = [name for name, element in canvas]

		samplenr = 0
		fixating = False
		x_prev, y_prev = 0,0
		aoi_prev = []
		fixation_prev = 0
		dwell = []
		fix_latency = []
		fix_dwell = 0
		fix_dwell_prev = 0
		fix_location = []
		time_fix = 0
		time_sacc = 0
		sample_n = self.var.duration/self.var.sampling_rate

		dwell_time_dict = {
			name: 0
			for name, elements in canvas
			if name != '__background__'
		}


		yield # End preparation ----------------------------------------------

		t_0 = self.clock.time()
		t_1 = 0

		while True:
			# Only collect data every once in a while so that we don't poll the
			# eyetracker infinitely fast:
			if not self.clock.once_in_a_while(self.var.sampling_rate):
				alive = yield
				if not alive:
					break
				continue

			# Get a sample and check in which elements it is:
			x,y = eyetracker.sample()
			if self.var.uniform_coordinates:
				x -= xc
				y -= yc

			# Check if gaze is stable with a VERY arbitrary constraint
			# of 5 points (x = current sample, xo = previous sample):
			if abs((x-x_prev)+(y-y_prev)) < 5:
				fixating = True
				time_fix += self.var.sampling_rate

				# Check in which canvas elements the fixation is:
				aoi = [
					name
					for name in canvas.elements_at(x, y)
					if name != '__background__'
				]

				for name in aoi:
					dwell_time_dict[name] += 1

			else:
				# If fixation is not stable, aoi = NA:
				fixating = False
				time_sacc += self.var.sampling_rate
				aoi = []

			# Check for the beginning of a fixation and calculate its onset
			# Fixation latencies relative to t_0 are stored in a list (fix_latency)
			# and so are fixation locations (fix_location):
			if not fixation_prev and fixating and aoi:
				t_1 = self.clock.time()
				fix_latency.append(t_1-t_0)
				fix_location.append(aoi[0])
			# Or, if fixation persists from last sample, start counting number of samples
			# spent fixating:
			elif fixation_prev and fixating and aoi:
				fix_dwell += 1
			else:
				pass

			# Append the accumulated fix_dwell samples once a saccade is initiated
			# after a period of aoi fixation:
			if not fixating and fixation_prev and fix_dwell and aoi_prev:
				dwell.append(fix_dwell)


			# Save the current sample's values for use in next iteration:
			x_prev, y_prev = x,y
			aoi_prev = aoi
			fixation_prev = fixating
			fix_dwell_prev = fix_dwell
			samplenr += 1

		for i, value in dwell_time_dict.items():
			self.experiment.var.set(
				u'dwell_time_%s' % i,
				value*self.var.sampling_rate
				)


		if len(fix_latency) != 0:
			self.experiment.var.set(
				u'first_fix_latency',
				fix_latency[0]
				)
		else:
			self.experiment.var.set(
				u'first_fix_latency',
				0
				)


		if len(fix_location) != 0:
			#fix_location = list(filter(None, fix_location))
			self.experiment.var.set(
				u'first_fix_location',
				str(fix_location[0])
				)
		else:
			self.experiment.var.set(
				u'first_fix_location',
				0
				)


		if len(dwell) != 0:
			self.experiment.var.set(
				u'first_fix_dwell',
				dwell[0]*self.var.sampling_rate
				)
		else:
			self.experiment.var.set(
				u'first_fix_dwell',
				0
				)

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
