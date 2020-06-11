# TrainAndTest.py

import cv2
import numpy as np
import operator
import os
import mainPrevious


# module level variables ##########################################################################
MIN_CONTOUR_AREA = 100

RESIZED_IMAGE_WIDTH = 20
RESIZED_IMAGE_HEIGHT = 30

validContoursWithData = []
imgTestingNumbers = cv2.imread("g.png")
imgThresh = imgTestingNumbers
kNearest = cv2.ml.KNearest_create()

result = ""

gx = 0
gy = 0
gw = 0
gh = 0

arrflag = []

###################################################################################################

class ContourWithData():

    # member variables ############################################################################
    npaContour = None           # contour
    boundingRect = None         # bounding rect for contour
    intRectX = 0                # bounding rect top left corner x location
    intRectY = 0                # bounding rect top left corner y location
    intRectWidth = 0            # bounding rect width
    intRectHeight = 0           # bounding rect height
    fltArea = 0.0               # area of contour

    def calculateRectTopLeftPointAndWidthAndHeight(self):               # calculate bounding rect info
        [intX, intY, intWidth, intHeight] = self.boundingRect
        self.intRectX = intX
        self.intRectY = intY
        self.intRectWidth = intWidth
        self.intRectHeight = intHeight

    def checkIfContourIsValid(self):                            # this is oversimplified, for a production grade program
        if self.fltArea < MIN_CONTOUR_AREA: return False        # much better validity checking would be necessary
        return True

###################################################################################################
###################################################################################################
    
def main():
    global validContoursWithData
    allContoursWithData = []                # declare empty lists,
    validContoursWithData = []              # we will fill these shortly

    try:
        npaClassifications = np.loadtxt("classifications.txt", np.float32)                  # read in training classifications
    except:
        print ("error, unable to open classifications.txt, exiting program\n")
        os.system("pause")
        return

    try:
        npaFlattenedImages = np.loadtxt("flattened_images.txt", np.float32)                 # read in training images
    except:
        print ("error, unable to open flattened_images.txt, exiting program\n")
        os.system("pause")
        return

    ###################################################################################################
    #이미지 변경을 여기서 하세요 ############################################################################################

    npaClassifications = npaClassifications.reshape((npaClassifications.size, 1))       # reshape numpy array to 1d, necessary to pass to call to train

    global kNearest
    kNearest = cv2.ml.KNearest_create()                   # instantiate KNN object

    kNearest.train(npaFlattenedImages, cv2.ml.ROW_SAMPLE, npaClassifications)

    global imgTestingNumbers
    #imgTestingNumbers = cv2.imread("g.png")
    imgstr = mainPrevious.main2()
    imgTestingNumbers = cv2.imread(imgstr)
    img_global = imgTestingNumbers
    
    height, width, channels = img_global.shape
    print (width, height , channels)

    rate = width/height

    if(width > 2000):
        matrix = cv2.getRotationMatrix2D((width/2, height/2), 90, 1)
        rotate_image = cv2.warpAffine(img_global, matrix, (width, height))
        crop_image = rotate_image[(int)((height/2)-(int)((height/2)*0.2))-300:(int)(height/2)+(int)((height/2)*0.2)-200,(int)((width/2)) - (int)(width*0.4)+700:(int)(width/2) + (int)(width*0.4)-700]
        height, width, channels = crop_image.shape
        print (width, height , channels)
        rate = width/height
        rsz_image = cv2.resize(crop_image, (1200, int(1200/rate)))
        #rsz_image = cv2.resize(img_global, (1500, int(1500/rate)))
        #rsz_image = cv2.resize(img_global, (800, int(800/rate)))
    else:
        rsz_image = cv2.resize(img_global, (800, int(800/rate)))

    imgTesting = rsz_image 
    imgTestingNumbers = imgTesting

    #imgTestingNumbers = img         # read in testing numbers image

    if imgTestingNumbers is None:                           # if image was not read successfully
        print ("error: image not read from file \n\n")        # print error message to std out
        os.system("pause")                                  # pause so user can see error message
        return                                              # and exit function (which exits program)
    # end if

    ###################################################################################################
    #필터를 수정하는 부분 ###################################################################################

    imgGray = cv2.cvtColor(imgTestingNumbers, cv2.COLOR_BGR2GRAY)       # get grayscale image
    imgBlurred = cv2.GaussianBlur(imgGray, (5,5), 0)                    # blur
    
    global imgThresh
    #imgThresh = cv2.Canny(imgBlurred, threshold1=100, threshold2=200)
    
    ret, imgThresh = cv2.threshold(imgBlurred, 127,255,cv2.THRESH_BINARY_INV)
    '''
    imgThresh = cv2.adaptiveThreshold(imgBlurred,                           # input image
                                      255,                                  # make pixels that pass the threshold full white
                                      cv2.ADAPTIVE_THRESH_GAUSSIAN_C,       # use gaussian rather than mean, seems to give better results
                                      cv2.THRESH_BINARY_INV,                # invert so foreground will be white, background will be black
                                      11,                                   # size of a pixel neighborhood used to calculate threshold value
                                      2)                                    # constant subtracted from the mean or weighted mean
    '''
    imgThreshCopy = imgThresh.copy()       

    #cv2.imshow("abcd", imgThresh )
    
    rect_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (4, 12))      #4 , 10
    threshed = cv2.morphologyEx(imgThreshCopy, cv2.MORPH_CLOSE, rect_kernel)
    
    npaContours, npaHierarchy = cv2.findContours(threshed,             
                                                 cv2.RETR_EXTERNAL  ,        #RETR_EXTERNAL RETR_LIST
                                                 cv2.CHAIN_APPROX_SIMPLE )   #CV_CHAIN_APPROX_TC89_KCOS   

    rect_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (200, 30))      #4 , 10
    threshed1 = cv2.morphologyEx(imgThreshCopy, cv2.MORPH_CLOSE, rect_kernel)

    npaContours1, npaHierarchy1 = cv2.findContours(threshed1 ,             # input image, make sure to use a copy since the function will modify this image in the course of finding contours
                                                 cv2.RETR_EXTERNAL,         # retrieve the outermost contours only
                                                 cv2.CHAIN_APPROX_SIMPLE)   # compress horizontal, vertical, and diagonal segments and leave only their end points

    for cnt in npaContours:
        x, y, w, h = cv2.boundingRect(cnt)
        cv2.rectangle(imgTestingNumbers , (x, y), (x + w, y + h), (0, 255, 0), 2)

    
        
    global gx
    global gy
    global gw
    global gh
    for cnt in npaContours1:
        gx, gy, gw, gh = cv2.boundingRect(cnt)
        cv2.rectangle(imgTestingNumbers , (gx, gy), (gx + gw, gy + gh), (255, 255, 0), 1)
        
    cv2.imshow("function12", imgTestingNumbers)
    #cv2.waitKey(0)
        
    ###################################################################################################
    ###################################################################################################

    for npaContour in npaContours:                         
        contourWithData = ContourWithData()                                          
        contourWithData.npaContour = npaContour                                         
        contourWithData.boundingRect = cv2.boundingRect(contourWithData.npaContour)    
        contourWithData.calculateRectTopLeftPointAndWidthAndHeight()                   
        contourWithData.fltArea = cv2.contourArea(contourWithData.npaContour)         
        allContoursWithData.append(contourWithData)                                    

    for contourWithData in allContoursWithData:               
        if contourWithData.checkIfContourIsValid():             
            validContoursWithData.append(contourWithData)       

    validContoursWithData.sort(key = operator.attrgetter("intRectX"))       

    strFinalString = ""
    
    print("validcontourswithdata length : " + str(len(validContoursWithData)))

    ###################################################################################################
    ###################################################################################################

    i = 0
    global result
    arrflag = []
    print(function(validContoursWithData, i, imgThresh, arrflag))

    return result

    #print "\n" + strFinalString + "\n"                 

    ###################################################################################################
    ###################################################################################################

    cv2.imshow("imgTestingNumbers", imgTestingNumbers)
    #cv2.waitKey(0)

    cv2.destroyAllWindows()             # remove windows from memory


###################################################################################################

def function(validContoursWithData, i, img, arrflag):
    
    global gx
    global gy
    global gw
    global gh
    global result
    
    above = []
    below = []
    sigHigh = []
    sigLow = []
    sigMid = []
    
    #cv2.imshow("function1", img)
    #cv2.waitKey(0)

    if (i in arrflag):
        print("ARRAY FLAG")
        i = i + 1
        return function(validContoursWithData, i, img, arrflag)
    
    if (len(validContoursWithData) < i+1):
        print("STARTclear", i, len(validContoursWithData))
        return result


    contourWithData = validContoursWithData[i]
    
    # 분수일 때 
    if (contourWithData.intRectHeight*5.0 < contourWithData.intRectWidth):
        print("BUNSU")

        flag_above = False
        flag_below = False
        for j, temp in enumerate(validContoursWithData): 
            # 막대 범위 안에 있을 때 
            if (contourWithData.intRectX - 3 <= temp.intRectX <= contourWithData.intRectX + contourWithData.intRectWidth + 3):
                if (contourWithData.intRectY > temp.intRectY):  #막대 기준 위에 있을 때
                    arrflag.append(j)
                    i=i+1
                    flag_above = True
                if (contourWithData.intRectY < temp.intRectY):  #막대 기준 아래에 있을 때
                    arrflag.append(j)
                    i=i+1
                    flag_below = True
                    
        if(flag_above == True and flag_below == True):
            result = result + "("
            imgROI_1 = img[0: contourWithData.intRectY - 3,    
                       contourWithData.intRectX - 3 : contourWithData.intRectX + contourWithData.intRectWidth + 3]
            function3(imgROI_1)
            result = result + ")"
            result = result + "/"
            result = result + "("
            imgROI_2 = img[contourWithData.intRectY + contourWithData.intRectHeight+3: gy+gh,    
                       contourWithData.intRectX - 3 : contourWithData.intRectX + contourWithData.intRectWidth + 3]
            function3(imgROI_2)
            result = result + ")"
            
            if (len(validContoursWithData) < i+1):
                print("BUNSUclear", i, len(validContoursWithData))
                return result
        
            i=i+1
            return function(validContoursWithData, i, img, arrflag)

    #시그마의 윤곽선을 튀어나왔을 경우...!
    if(i < len(validContoursWithData)-1):
        if(function2(validContoursWithData[i+1], img) == 309):
            i = i + 1
            return function(validContoursWithData, i,img, arrflag)

    #시그마
    sigma_temp = validContoursWithData[i-1]

    if(function2(contourWithData, img) == 309):
        print("SIGMA")
        std1_x = 0
        std2_w = 0
        flag_above = False
        flag_below = False
        flag_mid = False
        for j, temp in enumerate(validContoursWithData):
            if(contourWithData.intRectX <= temp.intRectX and (contourWithData.intRectY) > temp.intRectY and contourWithData.intRectX < temp.intRectX < contourWithData.intRectX + contourWithData.intRectWidth):
                sigHigh.append(function2(temp, img))
                arrflag.append(j)
                i=i+1
                flag_above = True
            elif((sigma_temp.intRectX <= temp.intRectX and contourWithData.intRectY + contourWithData.intRectHeight < temp.intRectY and (contourWithData.intRectX + contourWithData.intRectWidth)+10 > temp.intRectX + temp.intRectWidth) or (contourWithData.intRectX <= temp.intRectX and contourWithData.intRectY + contourWithData.intRectHeight < temp.intRectY and (contourWithData.intRectX + contourWithData.intRectWidth)+10 > temp.intRectX + temp.intRectWidth)):
                sigLow.append(function2(temp, img))
                arrflag.append(j)
                i=i+1
                flag_below = True
            #기본적으로 시그마기호보다는 오른쪽에 위치
            elif(contourWithData.intRectX < temp.intRectX and contourWithData.intRectY < temp.intRectY):
                sigMid.append(function2(temp, img))
                arrflag.append(j)
                i=i+1
                flag_mid = True
                if(function2(temp, img) == "("):
                    std1_x = temp.intRectX
                    std1_y = temp.intRextY
                if(function2(temp, img) == ")"):
                    std1_w = temp.intRectWidth + temp.intRectX
                    break
            #분수같은 애들 넣으려고!
            elif(contourWithData.intRectX < temp.intRectX and contourWithData.intRectY > temp.intRectY and function2(temp, img) != 309):
                sigMid.append(function2(temp, img))
                arrflag.append(j)
                i=i+1
                flag_mid = True
        
        if(flag_above == True and flag_below == True ):
            result = result + "\\sum"
            print("gygygy: ", gy)
            result = result + "_{"
            imgROI_1 = img[contourWithData.intRectY + contourWithData.intRectHeight: gy+gh+10,    
                       contourWithData.intRectX - 10 : contourWithData.intRectX + contourWithData.intRectWidth + 8]
            function3(imgROI_1)
            result = result + "}"

            result = result + "^{"
            imgROI_2 = img[gy-20 : contourWithData.intRectY - 3,    
                       contourWithData.intRectX - 3 : contourWithData.intRectX + contourWithData.intRectWidth + 3]
            function3(imgROI_2)
            result = result + "}"

            result = result + "{"
            imgROI_3 = img[contourWithData.intRectY - 50 : contourWithData.intRectY + contourWithData.intRectHeight + 50,
                           std1_x: std1_w]
            function3(imgROI_3)
            result = result + "}"

            return function(validContoursWithData, i,img, arrflag)

    #시그마 종료


    # 인테그랄 시작
    if(function2(contourWithData, img) == 310):
        code = 0            # 끝지점 설정위한 변수
        integHigh = False   # 윗지수 여부
        integLow = False    # 밑지수 여부
        integMid = False    # 중간 여부
        
        for j, temp in enumerate(validContoursWithData):
            cntLow = 0
            cntMid = 0
            # 밑지수 확인
            if((contourWithData.intRectX < temp.intRectX) and ((contourWithData.intRectY + contourWithData.intRectHeight) > temp.intRectY) and ((contourWithData.intRectY + contourWithData.intRectHeight) < (temp.intRectY + temp.intRectHeight))):
                if cntLow == 0:
                    x1 = temp.intRectX
                    y1 = temp.intRectY
                    cntLow = cntLow + 1

                x2 = temp.intRectX + temp.intRectWidth
                y2 = temp.intRectY + temp.intRectHeight
                integLow = True
                arrflag.append(j)
                i=i+1

             # 윗지수 확인
            elif (contourWithData.intRectX < temp.intRectX and contourWithData.intRectY > temp.intRectY and temp.intRectY + (temp.intRectHeight/2)  < contourWithData.intRectY + 15):
                integHigh = True
                highX = temp.intRectX
                highY = temp.intRectY
                highH = temp.intRectHeight
                highW = temp.intRectWidth
                arrflag.append(j)
                i=i+1
                
            elif (contourWithData.intRectX < temp.intRectX):                    
                x3 = temp.intRectX + temp.intRectWidth
                y3 = temp.intRectY + temp.intRectHeight
                integMid = True
                arrflag.append(j)
                i=i+1
                if(code == 1):
                    break 
                if(function2(temp, img) == 'd'):
                    code = 1

        # 윗지수, 밑지수, 중간 있는 경우 
        if(integHigh == True and integLow == True and integLow == True):
            result = result + "\\int"
            result = result + "_{"
            
            imgROI_4 = img[y1:y2, x1:x2]
            function3(imgROI_4)
            
            result = result + "}"
            result = result + "^{"
            
            imgROI_5 = img[highY:highY+highH, contourWithData.intRectX + contourWithData.intRectWidth:highX+highW]
            function3(imgROI_5)
            
            result = result + "}"
            result = result + "{"
            
            imgROI_6 = img[highY:y2, highX+highW:x3]
            function3(imgROI_6)
            
            result = result + "}"
            
            print("finish")
            if (len(validContoursWithData) <= i):
                print("clear")
                return result

            i = i+1
            return function(validContoursWithData, i, img, arrflag)

        # 윗지수, 밑지수 없고, 중간만 있는 경우
        #elif (integHigh == False and integLow == False and integLow == True):
            

    if(function2(contourWithData,img)==308):


        result = result + "\\sqrt{" #루트 시작
        imgROI_3 = img[contourWithData.intRectY + 10 : contourWithData.intRectY + contourWithData.intRectHeight ,    
                       validContoursWithData[i+1].intRectX  : contourWithData.intRectX + contourWithData.intRectWidth ]
        #cv2.imshow("function3", imgROI_3)
        #cv2.waitKey(0)
        
        function3(imgROI_3)
        result = result + "}"
        
        for k, temp in enumerate(validContoursWithData):
            
            if ( contourWithData.intRectX <= temp.intRectX and contourWithData.intRectX + contourWithData.intRectWidth >= temp.intRectX):
                #rootMid.append(function2(temp)) #루트 안의 배열을 집어넘
                arrflag.append(k) #글자 확인했다는 표식, 중복검사, 출력하지 않게 하기위함
                i= i+1

        if (len(validContoursWithData) < i+1):
            print("ROOTclear", i, len(validContoursWithData))
            return result
        
        i=i+1
        return function(validContoursWithData, i, img, arrflag)

        


    if (len(validContoursWithData) < i+1):
        print("DANILclear", i, len(validContoursWithData))
        return result
        
    result = result + function2(contourWithData, img)

    if(len(validContoursWithData) > i+1  and contourWithData.intRectY+(contourWithData.intRectHeight)*2/5 > validContoursWithData[i+1].intRectY + (validContoursWithData[i+1].intRectHeight) * 2/3):
        result = result + "^"# 승수
        
    print(result, i, len(validContoursWithData))

    
    
    i = i + 1
    return function(validContoursWithData, i, img, arrflag)

def function2(contourWithData, img):
    cv2.rectangle(imgTestingNumbers,                                       
                      (contourWithData.intRectX, contourWithData.intRectY),     
                      (contourWithData.intRectX + contourWithData.intRectWidth, contourWithData.intRectY + contourWithData.intRectHeight),    
                      (0, 255, 0),             
                      2)                       
    
    imgROI = img[contourWithData.intRectY : contourWithData.intRectY + contourWithData.intRectHeight,    
                       contourWithData.intRectX : contourWithData.intRectX + contourWithData.intRectWidth]

    #cv2.imshow("function3", imgROI)
    #cv2.waitKey(0)
    
    imgROIResized = cv2.resize(imgROI, (RESIZED_IMAGE_WIDTH, RESIZED_IMAGE_HEIGHT))             

    npaROIResized = imgROIResized.reshape((1, RESIZED_IMAGE_WIDTH * RESIZED_IMAGE_HEIGHT))  

    npaROIResized = np.float32(npaROIResized)

    retval, npaResults, neigh_resp, dists = kNearest.findNearest(npaROIResized, k = 1)  

    if(int(npaResults[0][0]) == 310):
        return int(npaResults[0][0])
    elif(int(npaResults[0][0]) == 308):
        return int(npaResults[0][0])
    elif(int(npaResults[0][0]) == 309):
        return int(npaResults[0][0])

    strCurrentChar = str(chr(int(npaResults[0][0])))

    return strCurrentChar

def function3(img):
    allContoursWithData = []
    validCont = []
    
    #cv2.imshow("function3", img)
    #cv2.waitKey(0)

    npaContours, npaHierarchy = cv2.findContours(img,             
                                                 cv2.RETR_EXTERNAL,        
                                                 cv2.CHAIN_APPROX_SIMPLE)
    
    for npaContour in npaContours:                         
        contourWithData = ContourWithData()                                          
        contourWithData.npaContour = npaContour                                         
        contourWithData.boundingRect = cv2.boundingRect(contourWithData.npaContour)    
        contourWithData.calculateRectTopLeftPointAndWidthAndHeight()                   
        contourWithData.fltArea = cv2.contourArea(contourWithData.npaContour)         
        allContoursWithData.append(contourWithData)                                    

    for contourWithData in allContoursWithData:               
        if contourWithData.checkIfContourIsValid():             
            validCont.append(contourWithData)       

    validCont.sort(key = operator.attrgetter("intRectX"))

    for cnt in npaContours:
        x, y, w, h = cv2.boundingRect(cnt)
        cv2.rectangle(img , (x, y), (x + w, y + h), (255, 255, 0), 1)
        
    #cv2.imshow("kkk", img)
    #cv2.waitKey(0)

    arrflag = []
    function(validCont, 0, img, arrflag)
    
if __name__ == "__main__":
    main()



# 만약 위아래에 무언가가 있을 시 넘어간다
# 예를 들어 시그마의 옵션 같은 작은 글씨 등 그것들을 대비하여 넘어감 
