import numpy as np
import math

LATENCY_FRAMES = 12

class cars():
	def __init__(self):
		self.boxes = []

	def get_sensible_boxes(self, new_boxes):
		for prev_box in self.boxes:
			prev_box.current_frame = False
		for box in new_boxes:
			min_dist = 1000
			epsilon = 20
			closest_centroid = None
			new_car_box = car_box(box)
			print('ss{}'.format(box))
			for prev_box in self.boxes:
				dist = prev_box.dist(new_car_box.centroid) 
				if(dist < min_dist):
					print('dist ' + str(dist))
					min_dist = dist
					closest_centroid = prev_box
			if(closest_centroid != None):
				if(prev_box.current_frame == False):
					if(not closest_centroid.same_center(new_car_box)):
						self.boxes.append(new_car_box)
			else:
				print('append')
				print(new_car_box.box)
				self.boxes.append(new_car_box)
		for box in self.boxes:
			if(not box.current_frame):
				if(box.suspitious > 0):
					print('suspitious' + str(box.suspitious))
					if(box.suspitious >= LATENCY_FRAMES):
						print('remove')
						print(box.box)
						self.boxes.remove(box)
					box.suspitious += 1
				else:
					print('suspitious 1')
					print(box.box)
					box.suspitious = 1
		output_boxes = []		
		for box in self.boxes:
			#if(box.suspitious <= 0):
			output_boxes.append(box.get_output_box())
			print('centroid')
			print(box.centroid)
			print('prev_centroids')
			print(box.prev_centroids)
		return output_boxes

class car_box():
	def __init__(self, box):
		self.box = box
		self.centroid = car_box.get_center(box)
		self.width = abs(box[0][0] - box[1][0])
		self.height = abs(box[0][1] - box[1][1])
		self.prev_centroids = []
		self.prev_width = []
		self.prev_height = []
		self.current_frame = True
		self.suspitious = 1

	def same_center(self, box):
		widths = np.hstack((self.prev_width, [self.width]))
		heights = np.hstack((self.prev_height, [self.height]))
		epsilon = max(60, 1.3 * (sum(widths) + sum(heights))/float(len(widths) + len(heights)))
		if(self.dist(box.centroid) < epsilon):
			if(len(self.prev_centroids) >= LATENCY_FRAMES):
				self.prev_centroids.pop(0)
				self.prev_width.pop(0)
				self.prev_height.pop(0)
			self.prev_centroids.append(self.centroid)
			self.prev_width.append(self.width)
			self.prev_height.append(self.height)
			self.box = box.box
			self.centroid = box.centroid
			self.width = box.width
			self.height = box.height
			self.current_frame = True
			self.suspitious = 0
			return True
		return False
	
	@staticmethod
	def get_center(box):
		return ((box[0][0] + box[1][0])/2.0, (box[0][1] + box[1][1])/2.0)

	def dist(self, point):
		return math.sqrt(math.pow(point[0] - self.centroid[0], 2) + math.pow(point[1] - self.centroid[1], 2))

	def get_output_box(self):
		center = self.center_point(self.prev_centroids, self.centroid)
		width = np.hstack((self.prev_width, [self.width]))
		width = sum(width) / float(len(width))
		height = np.hstack((self.prev_height, [self.height]))
		height = sum(height) / float(len(height))
		result = ((int(round(center[0] - width / 2.0)), int(round(center[1] - height / 2.0))), (int(round(center[0] + width / 2.0)), int(round(center[1] + height / 2.0))))
		print('output')
		print(result)
		return result

	def center_point(self, points, another_point):
		xs = 0
		ys = 0
		for point in points:
			xs += point[0]
			ys += point[1]
		xs+=another_point[0]
		ys+=another_point[1]
		return (xs/(len(points) + 1), ys/(len(points) + 1))


