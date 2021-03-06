"""
relabel_annotations.py
Code for cleaning and sequentially relabelling figure eight annotations (universal)
run once for every base directory (cell type), runs on full sets
"""
# Import python packages
import numpy as np
from skimage.io import imsave, imread
import matplotlib.pyplot as plt
import os
from skimage.morphology import remove_small_holes, remove_small_objects

def relabel():
    set_path = input('Path to set you want relabeled: ')
    #montage_path = './annotations/'
    #list_of_montages = os.listdir(montage_path)
    #print(list_of_montages)
    output_path = os.path.join(set_path, 'relabelled_annotations')
    if os.path.isdir(output_path) is False:
        os.makedirs(output_path)
    list_of_montages = os.listdir(os.path.join(set_path, 'annotations'))
    for montage_name in list_of_montages:
        # get the image segment
        save_ind = os.path.splitext(montage_name)[0][len("annotation_"):]
        montage_file = os.path.join(set_path,'annotations', montage_name)
        img_array = imread(montage_file)[:,:,0]
        img_clean = clean_montage(img_array)
        seq_label = relabel_montage(img_clean)
        seq_img = "seq_annotation" + save_ind + ".tif"
        image_path = os.path.join(output_path, seq_img)
        imsave(image_path, seq_label.astype(np.uint8))

def clean_montage(img):
    clean_img = remove_small_holes(img, connectivity=1,in_place=False)
    clean_img = remove_small_objects(clean_img, min_size=10, connectivity=1, in_place=False)
    fixed_img = np.zeros(img.shape, dtype=np.uint8)
    # using binary clean_img, assign cell labels to pixels of new image
    # iterate through the entire image
    for x in range(1, img.shape[0]):
        for y in range(1, img.shape[1]):
            # if clean_img is true, that pixel should have a label in fixed_img
            if clean_img[x, y].any():
                # get possible labels from original image (exclude background)
                ball = img[x-1:x+1, y-1:y+1].flatten()
                ball = np.delete(ball, np.where(ball == 0))
                if len(ball) == 0: # if no possible labels
                    if x>1 and y>1:
                        # take a larger area for labels, if possible
                        ball = img[x-2:x+2, y-2:y+2].flatten()
                        ball = np.delete(ball,np.where(ball == 0))
                        if len(ball) != 0:
                            # if there are possible values, take the most common
                            pixel_val = np.argmax(np.bincount(ball))
                            fixed_img[x, y] = pixel_val
                        else:
                            # otherwise take the label of that pixel from the original img
                            #   output location & frame to for user reference
                            fixed_img[x,y] = img[x,y]
                            print("x, y: ", (x, y))
                    else:
                        # otherwise take the label of that pixel from the original img
                        #   output location & frame to for user reference
                        fixed_img[x,y] = img[x,y]
                        print("x, y: ", (x, y))
                else: # if there are possible values, take the most common
                    pixel_val = np.argmax(np.bincount(ball))
                    fixed_img[x, y] = pixel_val
    return fixed_img

def relabel_montage(y):
    # create new_y to save new labels to
    new_y = np.zeros(y.shape)
    unique_cells = np.unique(y) # get all unique values of y
    unique_cells = np.delete(unique_cells, np.where(unique_cells == 0)) # remove 0, as it is background
    relabel_ids = np.arange(1, len(unique_cells) + 1)
    # iterate through existing labels, and save those pixels as new id in new_y
    for cell_id, relabel_id in zip(unique_cells, relabel_ids):
        cell_loc = np.where(y == cell_id)
        new_y[cell_loc] = relabel_id
    return new_y

if __name__ == '__main__':
    relabel()
