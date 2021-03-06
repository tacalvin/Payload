###################################################
##Name: Andrew Olguin
##
##Date: 1-1-15
##
##Functionality: This code is meant to match objects in an image to a objects in training set.
##it uses FLANN and surf features to match two images together. This code is still
##under development.
##See this link for documentation: http://bit.ly/1tH9a6P
##
##Version: 1
##
##Changes log: none
###################################################

import numpy as np
import cv2
from matplotlib import pyplot as plt


SZ=20
bin_n = 16 # Number of bins

svm_params = dict( kernel_type = cv2.SVM_LINEAR,
                    svm_type = cv2.SVM_C_SVC,
                    C=2.67, gamma=5.383 )

affine_flags = cv2.WARP_INVERSE_MAP|cv2.INTER_LINEAR

def nothing(x):
    pass

def Sobel(gray):
    scale = 1
    delta = 0
    ddepth = cv2.CV_16S

    # Gradient-X
    grad_x = cv2.Sobel(gray,ddepth,1,0,ksize = 3, scale = scale, delta = delta,borderType = cv2.BORDER_DEFAULT)
    #grad_x = cv2.Scharr(gray,ddepth,1,0)

    # Gradient-Y
    grad_y = cv2.Sobel(gray,ddepth,0,1,ksize = 3, scale = scale, delta = delta, borderType = cv2.BORDER_DEFAULT)
    #grad_y = cv2.Scharr(gray,ddepth,0,1)

    # converting back to uint8
    abs_grad_x = cv2.convertScaleAbs(grad_x)  
    abs_grad_y = cv2.convertScaleAbs(grad_y)

    dst = cv2.addWeighted(abs_grad_x,5,abs_grad_y,5,0)

    return dst

def deskew(img):
    m = cv2.moments(img)
    if abs(m['mu02']) < 1e-2:
        return img.copy()
    skew = m['mu11']/m['mu02']
    M = np.float32([[1, skew, -0.5*SZ*skew], [0, 1, 0]])
    img = cv2.warpAffine(img,M,(SZ, SZ),flags=affine_flags)
    return img

def Clust(img, K):
    Z = img.reshape((-1,3))

    # convert to np.float32
    Z = np.float32(Z)

    # define criteria, number of clusters(K) and apply kmeans()
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 10, 1.0)

    ret,label,center=cv2.kmeans(Z,K,None,criteria,10,cv2.KMEANS_RANDOM_CENTERS)
    #ret, label, center = cv2.kmeans(Z, K, criteria, 10, 0)

    # Now convert back into uint8, and make original image
    center = np.uint8(center)
    res = center[label.flatten()]
    res2 = res.reshape((img.shape))

    return res2

def hog(img):
    gx = cv2.Sobel(img, cv2.CV_32F, 1, 0)
    gy = cv2.Sobel(img, cv2.CV_32F, 0, 1)
    mag, ang = cv2.cartToPolar(gx, gy)

    # quantizing binvalues in (0...16)
    bins = np.int32(bin_n*ang/(2*np.pi))

    # Divide to 4 sub-squares
    bin_cells = bins[:10,:10], bins[10:,:10], bins[:10,10:], bins[10:,10:]
    mag_cells = mag[:10,:10], mag[10:,:10], mag[:10,10:], mag[10:,10:]
    hists = [np.bincount(b.ravel(), m.ravel(), bin_n) for b, m in zip(bin_cells, mag_cells)]
    hist = np.hstack(hists)
    return hist

#this function is meant to detect surf features in an image and uses an image pyramid to upscale an image
#it uses the image preprocessing methods show in the meanClust-1 script
#Parameters:
#K= number of colors in the clustered output
#lb/ub= the bounds for the canny edge detection
#surfVal= surf feature threshold, higher the number the less feautures
#img- input image
def SURFINPYR(img, K, lb, ub, srfVal):
    
    deskew(img)

    img1 = Clust(img, K)

    surf = cv2.SURF(srfVal)

    img1 = cv2.cvtColor(img1, cv2.COLOR_RGB2LUV)

    uv_img = img[:,:,1]+ img[:,:,2]

    img2 = cv2.pyrUp(uv_img)
    img2 = cv2.pyrUp(img2)

    grad = Sobel(img2)
    edges = cv2.Canny(grad,lb,ub)

    kp, des = surf.detectAndCompute(edges, None)

    return kp, des


#this function is meant to detect surf features in an image
#it uses the image preprocessing methods show in the meanClust-1 script
#Parameters:
#K= number of colors in the clustered output
#lb/ub= the bounds for the canny edge detection
#surfVal= surf feature threshold, higher the number the less feautures
#img- input image
def SURFIN(img, K, lb, ub, srfVal):
    img = Clust(img, K)

    surf = cv2.SURF(srfVal)

    img = cv2.cvtColor(img, cv2.COLOR_RGB2LUV)

    uv_img = img[:,:,1]+ img[:,:,2]

    grad = Sobel(img2)
    edges = cv2.Canny(grad,lb,ub)

    kp, des = surf.detectAndCompute(edges, None)

    return kp, des

###########################################################################################
test = cv2.imread('T.png',0)
train1 = cv2.imread('F.png',0)
train2 = cv2.imread('G.png',0)
#cells = [np.hsplit(row,100) for row in np.vsplit(img,50)]

# First half is trainData, remaining is testData
#train_cells = [ i[:50] for i in cells ]
#test_cells = [ i[50:] for i in cells]

######     Now training      ########################

train1 = hog(train1)
train2 = hog(train2)

#deskewed = [map(deskew,row) for row in train_cells]
#hogdata = [map(hog,row) for row in deskewed]
trainData1 = np.float32(train1).reshape(-1,64)
trainData2 = np.float32(train2).reshape(-1,64)
responses = np.float32(np.repeat(np.arange(2),1)[:,np.newaxis])

trainData = np.vstack((trainData1, trainData2))

print trainData.shape
print responses.shape

svm = cv2.SVM()
svm.train(trainData,responses, params=svm_params)
svm.save('svm_data.dat')


######     Now testing      ########################

#deskewed = [map(deskew,row) for row in test_cells]
#hogdata = [map(hog,row) for row in deskewed]

hogdata = hog(test)

testData = np.float32(hogdata).reshape(-1,bin_n*4)
result = svm.predict_all(testData)

print result

#######   Check Accuracy   ########################
mask = result==responses
correct = np.count_nonzero(mask)
print correct*100.0/result.size
