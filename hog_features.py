import matplotlib.image as mpimg
import matplotlib.pyplot as plt
import numpy as np
import cv2
import glob
import time
import pickle
from sklearn.svm import LinearSVC
from sklearn.preprocessing import StandardScaler
from skimage.feature import hog
# NOTE: the next import is only valid for scikit-learn version <= 0.17
# for scikit-learn >= 0.18 use: 
from sklearn.model_selection import train_test_split
#from sklearn.cross_validation import train_test_split

def convert_color(image, cspace='RGB'):    
    # apply color conversion if other than 'RGB'
    feature_image = np.copy(image)  
    if cspace != 'RGB':
        if cspace == 'HSV':
            feature_image = cv2.cvtColor(image, cv2.COLOR_RGB2HSV)
        elif cspace == 'LUV':
            feature_image = cv2.cvtColor(image, cv2.COLOR_RGB2LUV)
        elif cspace == 'HLS':
            feature_image = cv2.cvtColor(image, cv2.COLOR_RGB2HLS)
        elif cspace == 'YUV':
            feature_image = cv2.cvtColor(image, cv2.COLOR_RGB2YUV)
        elif cspace == 'YCrCb':
            feature_image = cv2.cvtColor(image, cv2.COLOR_RGB2YCrCb)
    else: 
        print(image[0:10, 0:10, :])
        image *= 255
        print(image[0:10, 0:10, :])
        feature_image = np.copy(image)  
    return feature_image

# Define a function to compute binned color features  
def bin_spatial(img, size=(32, 32)):
    # Use cv2.resize().ravel() to create the feature vector
    features = cv2.resize(img, size).ravel() 
    # Return the feature vector
    return features
                        
def color_hist(img, nbins=32):    #bins_range=(0, 256)
    # Compute the histogram of the color channels separately
    channel1_hist = np.histogram(img[:,:,0], bins=nbins)
    channel2_hist = np.histogram(img[:,:,1], bins=nbins)
    channel3_hist = np.histogram(img[:,:,2], bins=nbins)
    # Concatenate the histograms into a single feature vector
    hist_features = np.concatenate((channel1_hist[0], channel2_hist[0], channel3_hist[0]))
    # Return the individual histograms, bin_centers and feature vector
    return hist_features

# Define a function to return HOG features and visualization
def get_hog_features(img, orient, pix_per_cell, cell_per_block, 
                        vis=False, feature_vec=True):
    # Call with two outputs if vis==True
    if vis == True:
        features, hog_image = hog(img, orientations=orient, pixels_per_cell=(pix_per_cell, pix_per_cell),
                                  cells_per_block=(cell_per_block, cell_per_block), transform_sqrt=True, 
                                  visualise=vis, feature_vector=feature_vec)
        return features, hog_image
    # Otherwise call with one output
    else:      
        features = hog(img, orientations=orient, pixels_per_cell=(pix_per_cell, pix_per_cell),
                       cells_per_block=(cell_per_block, cell_per_block), transform_sqrt=True, 
                       visualise=vis, feature_vector=feature_vec)
        return features

# Define a function to extract features from a list of images
# Have this function call bin_spatial() and color_hist()
def extract_features(imgs, cspace, orient=9, pix_per_cell=8, cell_per_block=2, hog_channel=0, vis=False, spatial_size=(32, 32), hist_bins=32):
    # Create a list to append feature vectors to
    features = []
    # Iterate through the list of images
    for file in imgs:
        file_features = []
        # Read in each one by one
        image = mpimg.imread(file)  
        feature_image = image 

        #for  cspace in cspaces:
        feature_image = convert_color(image, cspace)

        spatial_features = bin_spatial(feature_image, size=spatial_size)
        file_features.append(spatial_features)

        # Apply color_hist()
        hist_features = color_hist(feature_image, nbins=hist_bins)
        file_features.append(hist_features)
        
        # Call get_hog_features() with vis=False, feature_vec=True
        if hog_channel == 'ALL':
            hog_features = []
            for channel in range(feature_image.shape[2]):
                hog_features.append(get_hog_features(feature_image[:,:,channel], 
                                    orient, pix_per_cell, cell_per_block, 
                                    vis=False, feature_vec=True))
            hog_features = np.ravel(hog_features)        
        else:
            hog_features = get_hog_features(feature_image[:,:,hog_channel], orient, 
                        pix_per_cell, cell_per_block, vis=False, feature_vec=True)
        # Append the new feature vector to the features list
        file_features.append(hog_features)

        features.append(np.concatenate(file_features))
    # Return list of feature vectors
    return features

def plot_images(image_dict):
    fig = plt.figure()    
    plt.axis('off')
    image_count = len(image_dict)
    i = 1
    for key in sorted(image_dict):
        nrows, ncols, plot_number = (image_count + 1)//8, 8, i
        i+=1       
        plt.subplot(nrows, ncols, plot_number)
        plt.imshow(image_dict[key][0], cmap='gray')
        plt.title(image_dict[key][1], fontsize=8)
    #plt.tight_layout()
    plt.show()

def visualise_hog(image_dict, cars, notcars, cspace='RGB', orient=9, pix_per_cell=8, cell_per_block=2, hog_channel=0, car_index=-1, noncar_index=-1):
    if(car_index == -1):
        car_index =  np.random.randint(0, len(cars))
    if(noncar_index == -1):
        noncar_index = np.random.randint(0, len(notcars))
    vis_images = [cars[car_index], notcars[noncar_index]]
    for file in vis_images:
        # Read in each one by one
        image = mpimg.imread(file)  
        image_dict[len(image_dict)] = (image, 'Original')  
        feature_image = convert_color(image, cspace)
        # Call get_hog_features() with vis=False, feature_vec=True
        if hog_channel == 'ALL':
            for channel in range(feature_image.shape[2]):
                features, hog_image = get_hog_features(feature_image[:,:,channel], 
                                    orient, pix_per_cell, cell_per_block, 
                                    vis=True, feature_vec=False) 
                image_dict[len(image_dict)] = (hog_image, 'HOG:{}[{}],{},{},{}'.format(cspace, channel, orient, pix_per_cell, cell_per_block))
        else:
            features, hog_image = get_hog_features(feature_image[:,:,hog_channel], orient, 
                        pix_per_cell, cell_per_block, vis=True, feature_vec=False)
            image_dict[len(image_dict)] = (hog_image, 'HOG {} of {}'.format(hog_channel, cspaces))
    

def train():
    colorspace = 'YCrCb'#, 'YCrCb') # Can be RGB, HSV, LUV, HLS, YUV, YCrCb
    orient = 12
    pix_per_cell = 6
    cell_per_block = 2
    hog_channel = "ALL" # Can be 0, 1, 2, or "ALL"
    image_dict = {}
    spatial_size = (32, 32)
    hist_bins=32

    images = glob.glob('./train_images/*.png')
    cars = []
    notcars = []
    for image in images:
        if 'extra' in image:
            notcars.append(image)
        else:
            cars.append(image)
    car_index =  np.random.randint(0, len(cars))
    noncar_index = np.random.randint(0, len(notcars))
    if False:
        visualise_hog(image_dict, cars, notcars, cspace='YCrCb', orient=32, pix_per_cell=4, cell_per_block=8, hog_channel=hog_channel, car_index=car_index, noncar_index=noncar_index)
        visualise_hog(image_dict, cars, notcars, cspace='YCrCb', orient=32, pix_per_cell=4, cell_per_block=16, hog_channel=hog_channel, car_index=car_index, noncar_index=noncar_index)
        visualise_hog(image_dict, cars, notcars, cspace='YCrCb', orient=32, pix_per_cell=4, cell_per_block=16, hog_channel=hog_channel, car_index=car_index, noncar_index=noncar_index)
        visualise_hog(image_dict, cars, notcars, cspace='YCrCb', orient=32, pix_per_cell=4, cell_per_block=16, hog_channel=hog_channel, car_index=car_index, noncar_index=noncar_index)
        plot_images(image_dict)

    # Reduce the sample size because HOG features are slow to compute
    # The quiz evaluator times out after 13s of CPU time
    #sample_size = 500
    #cars = cars[0:sample_size]
    #notcars = notcars[0:sample_size]

    t=time.time()
    car_features = extract_features(cars, cspace=colorspace, orient=orient, 
                            pix_per_cell=pix_per_cell, cell_per_block=cell_per_block, 
                            hog_channel=hog_channel)
    notcar_features = extract_features(notcars, cspace=colorspace, orient=orient, 
                            pix_per_cell=pix_per_cell, cell_per_block=cell_per_block, 
                            hog_channel=hog_channel)
    t2 = time.time()
    print(round(t2-t, 2), 'Seconds to extract HOG features...')
    # Create an array stack of feature vectors
    X = np.vstack((car_features, notcar_features)).astype(np.float64)                        
    # Fit a per-column scaler
    X_scaler = StandardScaler().fit(X)
    # Apply the scaler to X
    scaled_X = X_scaler.transform(X)

    # Define the labels vector
    y = np.hstack((np.ones(len(car_features)), np.zeros(len(notcar_features))))


    # Split up data into randomized training and test sets
    rand_state = np.random.randint(0, 100)
    X_train, X_test, y_train, y_test = train_test_split(
        scaled_X, y, test_size=0.2, random_state=rand_state)

    print('Using:',orient,'orientations',pix_per_cell,
        'pixels per cell and', cell_per_block,'cells per block')
    print('Feature vector length:', len(X_train[0]))
    # Use a linear SVC 
    svc = LinearSVC()
    # Check the training time for the SVC
    t=time.time()
    svc.fit(X_train, y_train)
    t2 = time.time()
    print(round(t2-t, 2), 'Seconds to train SVC...')
    # Check the score of the SVC
    print('Test Accuracy of SVC = ', round(svc.score(X_test, y_test), 4))
    # Check the prediction time for a single sample
    t=time.time()
    n_predict = 10
    print('My SVC predicts: ', svc.predict(X_test[0:n_predict]))
    print('For these',n_predict, 'labels: ', y_test[0:n_predict])
    t2 = time.time()
    print(round(t2-t, 5), 'Seconds to predict', n_predict,'labels with SVC')

    svc_data = { "svc": svc, "scaler": X_scaler, "orient" : orient, "pix_per_cell" : pix_per_cell, "cell_per_block" : cell_per_block, "spatial_size" : spatial_size, "hist_bins" : hist_bins, "colorspace" : colorspace}
    pickle.dump( svc_data, open( "svc_pickle.p", "wb" ) )

#train()