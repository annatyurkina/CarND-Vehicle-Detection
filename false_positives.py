import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import numpy as np
import pickle
import cv2
from scipy.ndimage.measurements import label
import subsampling_window
from moviepy.editor import VideoFileClip
import cars

# Read in a pickle file with bboxes saved
# Each item in the "all_bboxes" list will contain a 
# list of boxes for one of the images shown above
box_list = pickle.load( open( "bbox_pickle.p", "rb" ))

cars_in_video = cars.cars()

# Read in image similar to one shown above 
image = mpimg.imread('./test_images/test1.jpg')
image1 = mpimg.imread('./test_images/test4.jpg')
image2 = mpimg.imread('./test_images/test5.jpg')
image3 = mpimg.imread('./test_images/test6.jpg')
heat = np.zeros_like(image[:,:,0]).astype(np.float)

def add_heat(heatmap, bbox_list):
    # Iterate through list of bboxes
    for box in bbox_list:
        # Add += 1 for all pixels inside each bbox
        # Assuming each "box" takes the form ((x1, y1), (x2, y2))
        heatmap[box[0][1]:box[1][1], box[0][0]:box[1][0]] += 1

    # Return updated heatmap
    return heatmap# Iterate through list of bboxes
    
def apply_threshold(heatmap, threshold):
    # Zero out pixels below the threshold
    heatmap[heatmap <= threshold] = 0
    # Return thresholded map
    return heatmap

def draw_labeled_bboxes(img, labels):
    indent = 50
    # Iterate through all detected cars
    bboxes = []
    for car_number in range(1, labels[1]+1):
        # Find pixels with each car_number label value
        nonzero = (labels[0] == car_number).nonzero()
        # Identify x and y values of those pixels
        nonzeroy = np.array(nonzero[0])
        nonzerox = np.array(nonzero[1])
        # Define a bounding box based on min/max x and y
        bbox = ((np.min(nonzerox), np.min(nonzeroy)), (np.max(nonzerox), np.max(nonzeroy)))
        print('RRREAL{}'.format(bbox))
        bboxes.append(bbox)

    #sensible_boxes = cars_in_video.get_sensible_boxes(bboxes)

    #for bbox in sensible_boxes:
        # Draw the box on the image
        cv2.rectangle(img, bbox[0], bbox[1], (0,0,255), 6)
        center = centroid(bbox)
        cv2.putText(img, '{},{}'.format(center[0], center[1]), (10, indent), cv2.FONT_HERSHEY_SIMPLEX, 1,(0,255,0),2)
        indent += 30
    # Return the image
    return img

def draw_boxes(image, vis=False):
    box_list = subsampling_window.get_boxes(image)    
    heat = np.zeros_like(image[:,:,0]).astype(np.float)
    # Add heat to each box in box list
    heat = add_heat(heat,box_list)    
    # Apply threshold to help remove false positives
    heat = apply_threshold(heat,1)
    # Visualize the heatmap when displaying    
    heatmap = np.clip(heat, 0, 255)
    # Find final boxes from heatmap using label function
    labels = label(heatmap)
    draw_img = draw_labeled_bboxes(np.copy(image), labels)
    if(vis):
        fig = plt.figure()
        plt.subplot(121)
        plt.imshow(draw_img)
        plt.title('Car Positions')
        plt.subplot(122)
        plt.imshow(heatmap, cmap='hot')
        plt.title('Heat Map')
        fig.tight_layout()
        plt.show()
    return draw_img

def centroid(box):
    return ((box[0][0] + box[0][1])/2.0, (box[1][0] + box[1][1])/2.0)


def fit_video():
    output = 'output.mp4'
    clip_input = VideoFileClip('project_video.mp4').subclip(9, 12)
    clip_output = clip_input.fl_image(draw_boxes)
    clip_output.write_videofile(output, audio=False)

fit_video()

#for img in (image, image1, image2, image3):
#    plt.imshow(draw_boxes(img, vis=True))

# plt.imshow(draw_boxes(image))
# plt.show()
# plt.imshow(draw_boxes(image1))
# plt.show()
# plt.imshow(draw_boxes(image2))
# plt.show()
# plt.imshow(draw_boxes(image3))
# plt.show()
# plt.imshow(draw_boxes(image4))
# plt.show()