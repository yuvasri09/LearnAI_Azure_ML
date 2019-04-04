'''
Code for downloading and processing the UCSD Anomaly Detection Dataset (http://www.svcl.ucsd.edu/projects/anomaly/dataset.htm)

The download are sequence of video frames (stored as tif).

At this point we are not going to do any resizing or cropping, but will probably do that later. 

The output are binary archives for each of the train/test/validation splits
'''

import os
import numpy as np
from scipy.misc import imresize, imread
import hickle as hkl
from settings import DATA_DIR
import glob
from sklearn.model_selection import train_test_split
from PIL import Image

desired_im_sz = (152, 232) # orig image size in USCD data: h,w = (158, 238) 
folders = ['UCSDped1']
skip_frames = 0

# Recordings used for training and validation
recordings_parent_folder = os.path.join(DATA_DIR, folders[0])
recordings = sorted(glob.glob(os.path.join(recordings_parent_folder, 'Train', 'Train*[0-9]')))
n_recordings = len(recordings)
recordings = list(zip([folders[0]] * n_recordings, recordings))

# we split the training data into training and validation set randomly, but with fixed random_state, for reproducability
train_recordings, val_recordings = train_test_split(recordings, test_size=.2, random_state=123)

# Recordings used for testing
recordings_parent_folder = os.path.join(DATA_DIR, folders[0])
recordings = glob.glob(os.path.join(recordings_parent_folder, 'Test', 'Test*[0-9]'))
n_recordings = len(recordings)
test_recordings = sorted(list(zip([folders[0]] * n_recordings, recordings)))

def process_data():
    ''' Create image datasets. Processes images and saves them in train, val, test splits. For each split, this creates a numpy array w/ dimensions n_images, height, width, depth.
    '''

    splits = {s: [] for s in ['train', 'test', 'val']} # create a dictionary of lists for train/test/val datasets
    splits['val'] = val_recordings 
    splits['test'] = test_recordings
    splits['train'] = train_recordings

    for split in splits:
        im_list = [] # list of all images of a split
        source_list = []  # corresponds to recording that image came from
        i = 0
        for _, folder in splits[split]:
            files = sorted(glob.glob(os.path.join(folder, '*.tif'), recursive=False))
            for skip in range(0, skip_frames + 1):
                # print(skip)
                for c, f in enumerate(files):
                    if c % (skip_frames + 1) == skip:
                        # print(c, skip, f)
                        im_list.append(f)
                        source_list.append(os.path.dirname(f))
                        i+=1

        print('Creating ' + split + ' data set with ' + str(len(im_list)) + ' images')
        
        # X is 4D w/ axes: n_images, height, width, depth (e.g. rgb, grayscale)
        X = np.zeros((len(im_list),) + desired_im_sz + (3,), np.uint8)
        for i, im_file in enumerate(im_list):
            im = Image.open(im_file).convert(mode='RGB') #, mode='RGB')
            # X[i] = np.asarray(im)
            try:
                X[i] = np.asarray(process_im(im)) # scale and crop image
            except:
                print(im_file)
                raise

        hkl.dump(X, os.path.join(DATA_DIR, 'X_' + split + '.hkl')) # save all the data one split in one giant archive
        hkl.dump(source_list, os.path.join(DATA_DIR, 'sources_' + split + '.hkl'))


def process_im(im):
    '''resize Image
    
    Arguments:
        im {[PIL.Image.Image]} -- Image to resize
    '''
    im = im.resize((desired_im_sz[1], desired_im_sz[0]), resample=Image.BICUBIC)
    return im


if __name__ == '__main__':
    process_data()
