#!/bin/python

import os
import pandas as pd
import numpy as np
from keras.preprocessing.image import img_to_array, load_img
from keras.applications.vgg16 import preprocess_input
import scipy.misc

from steering.util import full_path

class OrigData(object):
	def __init__(self, batch_size=32):
		self.batch_size = batch_size
		data_folder = full_path("image_data")
		self.video_folders = [os.path.join(data_folder,child) for child in os.listdir(data_folder) if os.path.isdir(os.path.join(data_folder,child))]
		self.generators = self._generators()

	def _generators(self):
		return [VideoGenerator(video_folder, batch_size=self.batch_size) for video_folder in self.video_folders]

	def shape(self):
		return self.generators[0].image_shape()

class VideoGenerator(object):
	def __init__(self, video_folder, batch_size=32):
		self.name = video_folder.split("/")[-1]
		self.video_folder = video_folder
		self.batch_size = batch_size
		self.df = pd.read_csv(video_folder + "/interpolated.csv")

		self.batch_index = 0
		self.direction = 'left'

	def size(self):
		return len(self.df.index)//3

	def image_shape(self):
		return self.image(0).shape

	def image(self, index):
		i_width = 320
		i_height = 240
		path = self.video_folder + "/" + self.df['filename'][index]
		original_image = img_to_array(load_img(path))
		return scipy.misc.imresize(original_image, (i_height, i_width))

	def images(self, indices):
		return preprocess_input(np.array([self.image(i) for i in indices], dtype=np.float32))

	def set_direction(self, direction):
		self.direction = direction
		self.batch_index = 0

	def direction_index(self, index):
		return np.where(self.direction_indicies == self.direction)[0][0] + index

	def __next__(self):
		return self.next()

	def next(self):
		last_index = self.size()*3
		start_index = self.batch_index
		end_index = min(self.batch_index + (3 * self.batch_size), last_index)
		# reset index when we get to the end
		self.batch_index = end_index if end_index < last_index else 0 

		indices = [self.direction_index(i) for i in range(start_index, end_index, 3)]
		return self.images(indices)
