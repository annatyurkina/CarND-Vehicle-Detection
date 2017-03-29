
[//]: # (Image References)

[image1]: ./output_images/colorspaces.png "Colorspaces Comparison"
[image2]: ./output_images/orientations.png "Colorspaces Comparison"
[image3]: ./output_images/pixes_per_cell.png "Pixels per Cell Comparison"
[image4]: ./output_images/cells_per_block.png "Cells per Block Comparison"
[image5]: ./output_images/boxes_overlay.png "Subsampling Windows, test6"
[image6]: ./output_images/boxes_overlay1.png "Subsampling Windows, test1"
[image7]: ./output_images/boxes_overlay4.png "Subsampling Windows, test4"
[image8]: ./output_images/heatmap_boxes6.png "False Positives Elimination, test6"
[image9]: ./output_images/heatmap_boxes1.png "False Positives Elimination, test1"
[image10]: ./output_images/heatmap_boxes4.png "False Positives Elimination, test4"
[video1]: ./output.mp4 "Video"

##Vehicle Detection

#Histogram of Oriented Gradients (HOG)

HOG features, together with color histogram and spatial binning, are used to train a classifier to recognise images of other cars on the road.  The code for HOG features extraction is located in **get_hog_features** method of [hog_features.py](hog_features.py), lines 54-68. Spatial binning is in **bin_spatial** method of [hog_features.py](hog_features.py), lines 37-42 and color histogram features extraction is in **convert_color** method in lines 44-52. The features are afterwards combined in **extract_features** method, lines 72-188. 

The rough idea of features extraction parameters magnitude was given and tested in lecture quizzes. Fine-tuning on the real images was done in code in methods **visualise_hog** and **plot_images** of [hog_features.py](hog_features.py), lines 124-145. 

Below are the images obtained for random samples from given cars and not-cars training dataset that were used to pick optimal values for parameters color space, number of orientations, number of pixels per cell and cells per block.

![alt text][image1]

![alt text][image2]

![alt text][image3]

![alt text][image4]

To choose final parameters for feature extraction, I used comparison images above, accuracy of test/train split on a set of train images and try/error on the actual project video. The end result that was used to train classifier for creating the output video is the following: **YCrCb** colorspace used, **12** orientations, **6** pixels per cell and **2** cells per block, as well as **32 by 32** for spatial binning and **32** histogram bins. Accuracy obtained on **80%/20%** train test split of the training set was equal **0.995**.

Extracted features were then scaled to zero mean and unit variance and used to train LinearSVC classifier, the code of splitting training data, scaling, fitting and testing the classifier can be found in **train** method of [hog_features.py](hog_features.py), lines 201-224. The classifier itself, the scaler and feature extraction parameters used are then saved to a pickle file (lines 226-227) to be restored and used in [subsampling_window.py](subsampling_window.py). 

#Sliding Window Search

As continuous HOG features extraction can be slow, we extract HOG features for the whole image and then subsample them for the sliding windows. This happens in **find_cars** method in [subsampling_window.py](subsampling_window.py), lines 20-87. In this method we scale the bottom area of the input image and then apply **pix_per_cell** division of 64 pixel window and then slide it by 2 cells per step. The steps for choosing the best **pix_per_cell** are described in the above section. The choice of slide cells number and scales was made by trial and error on the test images. The scales chosen are **range(1, 2.5, 0.25)**.
![alt text][image5]
![alt text][image6]
![alt text][image7]

During fine-tuning the classifier on the test images given, I noticed that if we choose HOG parameters that give us the most fine-grained and clear picture on car examples we start obtaining many false positives, but if we choose HOG parameters that give vague pictures for car/noncar images we of corse start missing real vehicles, so the best parameters lie somewhere in between. Also, spatial binning and color histograms do not raise overall accuracy considerable but it is still better to keep them for the edge cases when we have to rely on color more than on the gradient. When we pick smaller sliding window sizes we also get numerous false positives as smaller images focus on smaller details on the road. 

#Video Implementation

The output for the project video can be found here:

[output.mp4](output.mp4)

The output video consists of the input video where each frame is overlayed with boxes around the detected vehicles as well as the list of found vehicles'centroids. The pipeline to produce the video is located in method **draw_boxes** of [false_positives.py](false_positives.py), lines 68-90.

As we can see in the previous section examples, the subsampling windows methods used mostly produce a set of overlapping windows over every vehicle that gets successfully detected. We use the fact that one vehicle usually produces multiple boxes and create a heatmap of these windows intersection. Then we threshold the heatmap to output a single and supposedly best box countoring the detected vehicle. see methods **add_heat**, **apply_threshold** and **draw_labeled_bboxes** in [false_positives.py](false_positives.py), lines 26-66.
![alt text][image8]
![alt text][image9]
![alt text][image10]

Also, we expect a vehicle to be present on a video in a similar position and size over several subsequent video frames. To enforce this behaviour a **cars** and **car_box** classes were created in [cars.py](cars.py) file. **car_box** class represents a single vehicle detected in a video; it holds history of this vehicle's box center,wigth and height over the last 12 frames. When we obtain a set of vehicle boxes after thresholded heatmap,we use the following threshold on distance between historical and new box center to identify we have detected the same vehicle: **max(150, 1.3 * (sum(widths) + sum(heights))/float(len(widths) + len(heights)))** where **widths** and **heights** are accumulated over the last 12 frames or over lesser number of frames if the car recently appeared, minimum of 60 pixels and 1.3 weight were chosen by experiment.

#Discussion 

The pipeline works relatively well on the project video but is prone to misdetect on videos taken in different sceneries/environments. That's mostly due to rather small training set that does not contain time series images but rather all images from extra dataset. Also, the solution given relies on car speed being more or less uniform and the path being flat (i.e. the road is always in the same part of the frame). Pipeline does not detect small vehicles in the distance and struggles to differentiate between two cars being too close to each other.

The pipeline would benefit from enlarging training dataset, both cars and not-cars, and from taking time series images that are different from each other. It also may improve if more image features are taken into account: maybe combining features from two color spaces like YCrCb + HSV, reducing cells per block and pixels per cell parameters, sliding windows by 1 cell, increasing number of histogram bins and spatial size.

In addition, we may take into account steering, speed and acceleration of our car to better predict detected vehicle centroid for the next frames, or use regression on previous frames detected centers. By intersecting our predictions with lane lines detected in previous project we may concentrate more on vehicles in front of the car.   





 



 
