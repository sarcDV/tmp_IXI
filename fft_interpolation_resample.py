#!/usr/bin/python
import glob, os, subprocess, shutil
import numpy as np
import sys
import re
import scipy

import random
from sklearn import preprocessing
from scipy import misc
import nibabel as nib

import cv2
from PIL import Image
from skimage import io
from scipy import interpolate, signal
import numpy as np
import matplotlib.pyplot as plt
import cv2
import warnings
from scipy import ndimage
from skimage.filters import roberts, sobel, sobel_h, sobel_v, scharr#, \
from skimage.filters import prewitt


import progressbar
from time import sleep
import gc
from numba import jit, prange
#    scharr_h, scharr_v, prewitt, prewitt_v, prewitt_h, farid_v, farid_h
#ignore by message
warnings.filterwarnings("ignore", message="divide by zero encountered in divide")
#part of the message is also okay
warnings.filterwarnings("ignore", message="divide by zero encountered") 
warnings.filterwarnings("ignore", message="invalid value encountered")

def main():
    """ 

    downsampling / upsampling using scipy.signal.resample:
    sys.argv[1]: file to be processed
    sys.argv[2]: downsampling factor x
    sys.argv[3]: downsampling factor y
    sys.argv[4]: downsampling factor z

    """
    fft_interpolation(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
    return 


def from_res1_to_res2(img, factor_x, factor_y, factor_z):
    original_shape = len(img.shape)
    if len(img.shape)<=3:
        img = np.expand_dims(img, axis=3)
    nvols =  img.shape[3]
    interp3_ = np.zeros((img.shape[0],img.shape[1],int(img.shape[2]*factor_z),nvols))
    interp2_ = np.zeros((int(img.shape[0]*factor_x),int(img.shape[1]),int(img.shape[2]*factor_z),nvols))
    interp1_ = np.zeros((int(img.shape[0]*factor_x),int(img.shape[1]*factor_y),int(img.shape[2]*factor_z),nvols))
    print("\n ... interpolating ... \n")
    bar = progressbar.ProgressBar(maxval=nvols,widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
    bar.start()
    for vv in range(0, nvols): #img.shape[3]):
        # print((vv/img.shape[3])*100)
        ## xy 
        for ii in range(0, interp3_.shape[0]):
            for jj in range(0, interp3_.shape[1]):
                interp3_[ii,jj,:,vv]=signal.resample(img[ii,jj,:,vv],int(img.shape[2]*factor_z))
    
        ## yz       
        for ii in range(0, interp2_.shape[1]):
            for jj in range(0, interp2_.shape[2]):
                interp2_[:,ii,jj,vv]=signal.resample(interp3_[:,ii,jj,vv],int(img.shape[0]*factor_x))
        
        ## xz
        for ii in range(0, interp1_.shape[0]):
            for jj in range(0, interp1_.shape[2]):
                interp1_[ii,:,jj,vv]=signal.resample(interp2_[ii,:,jj,vv],int(img.shape[1]*factor_y))

        bar.update(vv+1)

    bar.finish()

    if original_shape<=3:
        interp1_ = np.squeeze(interp1_)

    return interp1_


def normalize_slice_by_slice(input_vol_):
    original_shape = len(input_vol_.shape)
    if len(input_vol_.shape)<=3:
        input_vol_ = np.expand_dims(input_vol_, axis=3)
    vol_ = np.zeros((input_vol_.shape))
    print("\n ... normalizing ... \n")
    bar = progressbar.ProgressBar(maxval=vol_.shape[3], widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
    bar.start()
    for jj in range(0, vol_.shape[3]):
        for ii in range(0,vol_.shape[2]):
            tmp_ = input_vol_[:,:,ii, jj]/input_vol_[:,:,ii,jj].max()
            where_are_nan = np.isnan(tmp_)
            tmp_[where_are_nan] = 0
            vol_[:,:,ii, jj] = tmp_
            #  ---------------------------------
        bar.update(jj+1)
        #sleep(0.005)
    bar.finish()

    if original_shape<=3:
        vol_ = np.squeeze(vol_)
    return vol_ 

def thresholding(input_vol_, valup_, valdown_):
    original_shape = len(input_vol_.shape)
    if len(input_vol_.shape)<=3:
        input_vol_ = np.expand_dims(input_vol_, axis=3)
    vol_ = np.zeros((input_vol_.shape))
    print("\n ... thresholding ... \n")
    bar = progressbar.ProgressBar(maxval=vol_.shape[3], widgets=[progressbar.Bar('=', '[', ']'), ' ', progressbar.Percentage()])
    bar.start()
    for jj in range(0, vol_.shape[3]):
        vol_[:,:,:,jj]=(input_vol_[:,:,:,jj]<valup_)*input_vol_[:,:,:,jj]
        vol_[:,:,:,jj]=(input_vol_[:,:,:,jj]>valdown_)*input_vol_[:,:,:,jj]
        bar.update(jj+1)
        #sleep(0.005)
    bar.finish()

    if original_shape<=3:
        vol_ = np.squeeze(vol_)
    return vol_


def fft_interpolation(file1, factor_x, factor_y, factor_z):
    print("                                            ")
    print("Upsampling / Downsampling image volume: " + str(file1)           )
    print("                                            ")
    
    
    a = nib.load(file1).get_fdata()
    head_info_ = (nib.load(file1)).header
    new_header =(nib.load(file1)).header.copy()
    orig_res_ = (head_info_['pixdim'])
    orig_size_ = (head_info_['dim'])
    print(" ... resolution of the input image volume:", orig_res_[1:4], " mm")
    print(" ... resolution of the output image volume:", orig_res_[1]/np.float64(factor_x),
                                                         orig_res_[2]/np.float64(factor_y),
                                                         orig_res_[3]/np.float64(factor_z), " mm")

    b = from_res1_to_res2(a, factor_x= np.float64(factor_x), 
                             factor_y  = np.float64(factor_y), 
                             factor_z = np.float64(factor_z))# from_iso_to_iso(a, factor=0.5)
    # b = normalize_slice_by_slice(b)
    ########################################
    #### change header information #########
    ########################################
    new_header['pixdim'] = [orig_res_[0], orig_res_[1]/np.float64(factor_x),
                                          orig_res_[2]/np.float64(factor_y),
                                          orig_res_[3]/np.float64(factor_z),
                                          orig_res_[4], orig_res_[5], orig_res_[6], orig_res_[7]]
    new_header['dim'] = [orig_size_[0], b.shape[0], b.shape[1], b.shape[2],
                                        orig_size_[4], orig_size_[5], orig_size_[6], orig_size_[7] ]
    ##################################################################
    #### SAVE NEW FILE ##############################################
    ##################################################################

    base=os.path.basename(file1)
    filedir_ = os.path.dirname(os.path.abspath(file1))

    # c_= nib.Nifti1Image(np.abs(b), np.eye(4), header=new_header)
    c_= nib.Nifti1Image(np.abs(b), None, header=new_header)
    nib.save(c_, str(filedir_)+'/interpolated-'+str(base))
    ################
    print("                                            ")
    print("Finished image interpolation: "+str(file1)    )
    print("                                            ")

if __name__ == "__main__":
    main()
