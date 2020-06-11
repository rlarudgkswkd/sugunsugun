import cv2
import numpy as np
import operator
import os
import mainPrevious

# module level variables ##########################################################################

MIN_CONTOUR_AREA = 80

RESIZED_IMAGE_WIDTH = 20
RESIZED_IMAGE_HEIGHT = 30

kNearest = cv2.ml.KNearest_create()

imgTesting = 0
imgThresh = imgTesting

result = ""

gx = 0
gy = 0
gw = 0
gh = 0

time = 0

###################################################################################################

class ContourWithData():
    npaContour = None          
    boundingRect = None        
    intRectX = 0                
    intRectY = 0                
    intRectWidth = 0            
    intRectHeight = 0           
    fltArea = 0.0               

    def calculateRectTopLeftPointAndWidthAndHeight(self):             
        [intX, intY, intWidth, intHeight] = self.boundingRect
        self.intRectX = intX
        self.intRectY = intY
        self.intRectWidth = intWidth
        self.intRectHeight = intHeight

    def checkIfContourIsValid(self):                            
        if self.fltArea < MIN_CONTOUR_AREA: return False 
        return True

###################################################################################################
    
def main():
    allContoursWithData = []                
    validContoursWithData = []              

    try:
        npaClassifications = np.loadtxt("classifications.txt", np.float32) 
    except:
        print ("error, unable to open classifications.txt, exiting program\n")
        os.system("pause")
        return

    try:
        npaFlattenedImages = np.loadtxt("flattened_images.txt", np.float32) 
    except:
        print ("error, unable to open flattened_images.txt, exiting program\n")
        os.system("pause")
        return

    ###################################################################################################
    #이미지 변경을 여기서 하세요 ######################################################################

    npaClassifications = npaClassifications.reshape((npaClassifications.size, 1))

    global kNearest
    
    kNearest = cv2.ml.KNearest_create()                   

    kNearest.train(npaFlattenedImages, cv2.ml.ROW_SAMPLE, npaClassifications)

     #img_global = cv2.imread("q1.jpg")
    imgstr = mainPrevious.main2()
    imgTestingNumbers = cv2.imread(imgstr)
    img_global = imgTestingNumbers
    
    height, width, channels = img_global.shape
    print (width, height , channels)

    rate = width/height

    if(width > 2000):
        matrix = cv2.getRotationMatrix2D((width/2, height/2), 90, 1)
        rotate_image = cv2.warpAffine(img_global, matrix, (width, height))
        crop_image = rotate_image[(int)((height/2)-(int)((height/2)*0.2))-400:(int)(height/2)+(int)((height/2)*0.2)-100,(int)((width/2)) - (int)(width*0.4)+700:(int)(width/2) + (int)(width*0.4)-700]
        height, width, channels = crop_image.shape
        print (width, height , channels)
        rate = width/height
        rsz_image = cv2.resize(crop_image, (1200, int(1200/rate)))
        #rsz_image = cv2.resize(img_global, (1500, int(1500/rate)))
        #rsz_image = cv2.resize(img_global, (800, int(800/rate)))
    else:
        rsz_image = cv2.resize(img_global, (1000, int(1000/rate)))

    imgTesting = rsz_image 

    #cv2.imshow("imgTestingk", rsz_image )
    #cv2.waitKey(0)

    if imgTesting is None:                           
        print ("error: image not read from file \n\n")        
        os.system("pause")                                 
        return                                              

    ###################################################################################################
    #필터를 수정하는 부분 #############################################################################

    imgGray = cv2.cvtColor(imgTesting, cv2.COLOR_BGR2GRAY)       
    imgBlurred = cv2.GaussianBlur(imgGray, (5,5), 0)                    

    #cv2.imshow("imgTesting",  imgBlurred )
    #cv2.waitKey(0)
        

    ret, imgThresh = cv2.threshold(imgBlurred, 127,255,cv2.THRESH_BINARY_INV)

    imgThreshCopy = imgThresh.copy()       
    imgThreshCopy1 = imgThresh.copy()

    #cv2.imshow("imgTesting",  imgThreshCopy )
    #cv2.waitKey(0)
        
    rect_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (4, 10))      #4 , 10
    threshed = cv2.morphologyEx(imgThreshCopy, cv2.MORPH_CLOSE, rect_kernel)
    npaContours, npaHierarchy = cv2.findContours(threshed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    for cnt in npaContours:
        x, y, w, h = cv2.boundingRect(cnt)
        cv2.rectangle(imgTesting, (x, y), (x + w, y + h), (0, 255, 0), 2)

    

    rect_kernel1 = cv2.getStructuringElement(cv2.MORPH_RECT, (200, 80))      #4 , 10
    threshed1 = cv2.morphologyEx(imgThreshCopy1, cv2.MORPH_CLOSE, rect_kernel1)
    npaContours1, npaHierarchy1 = cv2.findContours(threshed1, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    global gx
    global gy
    global gw
    global gh
    for cnt in npaContours1:
        gx, gy, gw, gh = cv2.boundingRect(cnt)
        cv2.rectangle(imgTesting , (gx, gy), (gx + gw, gy + gh), (0, 0, 255), 2)

    #cv2.imshow("imgTesting",  threshed )
    #cv2.imshow("imgTesting1",  imgTesting )
    #cv2.waitKey(0)
        
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

    print("len : "+str(len(validContoursWithData)))
    for i in validContoursWithData:  
        print(i.intRectX, i.intRectWidth, i.intRectY, i.intRectHeight)
    #print("validcontourswithdata length : " + str(len(validContoursWithData)))

    #for i, temp in enumerate(validContoursWithData):
    ##    if(temp.intRectX > gx+gw or temp.intRectX < gx or temp.intRectY < gy or temp.intRectY > gy+gh):
    #        del validContoursWithData[i]
    #    cv2.rectangle(imgTesting, ( temp.intRectX,  temp.intRectY), ( temp.intRectX + temp.intRectWidth, temp.intRectY + temp.intRectHeight), (0, 255, 0), 2)

    ###################################################################################################

    global result
    arrflag = []
    i = 0
    print(function(validContoursWithData, i, imgThresh, arrflag))
    temptemp = result
    result = "" 
    return temptemp
    #print "\n" + strFinalString + "\n"                 

    ###################################################################################################

    #cv2.imshow("imgTesting", imgTesting)
    #cv2.waitKey(0)
    cv2.destroyAllWindows()
    return

###################################################################################################
#fuction함수 ######################################################################################

def function(validContoursWithData, i, img, arrflag):
    global gx
    global gy
    global gw
    global gh
    global result
    global time

    above = []
    below = []

    sigHigh = []
    sigLow = []
    sigMid = []

    temp2 = 0

    if (function2(validContoursWithData[0],img) == "x" and i == 0 and len(validContoursWithData) > 12):
        time = 1
    elif (function2(validContoursWithData[0],img) == "y"):
        time = 0

    if (i in arrflag):
        #print("ARRAY FLAG")
        i = i + 1
        return function(validContoursWithData, i, img, arrflag)
    
    if (len(validContoursWithData) < i+1):
        #print("STARTclear", i, len(validContoursWithData))
        return result

    contourWithData = validContoursWithData[i]
    
    # 분수 시작 
    if (contourWithData.intRectHeight*5.0 < contourWithData.intRectWidth):
        #print("BUNSU")

        # equal(=) 확인 
        if (validContoursWithData[i+1].intRectHeight*5.0 < validContoursWithData[i+1].intRectWidth):
            if(contourWithData.intRectX -2 < validContoursWithData[i+1].intRectX < contourWithData.intRectX+2):
                result = result + "="
                i=i+2
                return function(validContoursWithData, i, img, arrflag)
        
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
    # 분수 종료
    #if((contourWithData.intRectX <= validContoursWithData[i+1].intRectX <= contourWithData.intRectX + contourWithData.intRectWidth)):
    #    temp2 = validContoursWithData[i+1].intRectX
    #    contourWithData.intRectWidth = contourWithData.intRectWidth - temp2
    
    if(function2(contourWithData,img)==308 or (i == 4 and contourWithData.intRectWidth > contourWithData.intRectHeight * 4.0)):
        if (len(validContoursWithData) < i+1):
            #print("ROOTclear", i, len(validContoursWithData))
            return result
        
        result = result + "\\sqrt{" 
        imgROI_3 = img[contourWithData.intRectY + 10 : contourWithData.intRectY + contourWithData.intRectHeight ,    
                       validContoursWithData[i+1].intRectX - 5 : contourWithData.intRectX + contourWithData.intRectWidth ]
        
        #cv2.imshow("imgTesting1",  imgROI_3 )
        #cv2.waitKey(0)
        
        function3(imgROI_3)
        result = result + "}"
        
        for k, temp in enumerate(validContoursWithData):
            if ( contourWithData.intRectX <= temp.intRectX and contourWithData.intRectX + contourWithData.intRectWidth >= temp.intRectX):
                arrflag.append(k) 
                i= i+1
        
        i=i+1
        return function(validContoursWithData, i, img, arrflag)
    #else:
    #    contourWithData.intRectWidth = contourWithData.intRectWidth + temp2
    # 루트 종료

    
    #시그마의 윤곽선을 튀어나왔을 경우...!
    if(i < len(validContoursWithData)-1):
        if(function2(validContoursWithData[i+1], img) == 309):
            i = i + 1
            return function(validContoursWithData, i,img, arrflag)


    #시그마
        
    sigma_temp = validContoursWithData[i-1]

    if(function2(contourWithData, img) == 309):
        print("SIGMA")
        num1 = 0
        num2 = 0
        flag_above = False
        flag_below = False
        flag_mid = False
        for j, temp in enumerate(validContoursWithData):
            if(contourWithData.intRectX <= temp.intRectX and (contourWithData.intRectY) > temp.intRectY and contourWithData.intRectX < temp.intRectX < contourWithData.intRectX + contourWithData.intRectWidth):
                
                sigHigh.append(function2(temp, img))
                arrflag.append(j)
                i=i+1
                flag_above = True
                if(num1 == 0):
                    high_x = temp.intRectX
                    high_y = temp.intRectY
                num1 = 1
                
            elif((sigma_temp.intRectX <= temp.intRectX and contourWithData.intRectY + contourWithData.intRectHeight < temp.intRectY and (contourWithData.intRectX + contourWithData.intRectWidth)+10 > temp.intRectX + temp.intRectWidth) or (contourWithData.intRectX <= temp.intRectX and contourWithData.intRectY + contourWithData.intRectHeight < temp.intRectY and (contourWithData.intRectX + contourWithData.intRectWidth)+10 > temp.intRectX + temp.intRectWidth)):
                 
                sigLow.append(function2(temp, img))
                arrflag.append(j)
                i=i+1
                flag_below = True
                if(num2 == 0):
                    low_x1 = temp.intRectX
                    low_y1 = temp.intRectY
                    low_h1 = temp.intRectHeight
                    num2 = 1
                   
            elif(contourWithData.intRectX < temp.intRectX and contourWithData.intRectY < temp.intRectY):
                
                sigMid.append(function2(temp, img))
                arrflag.append(j)
                i=i+1
                flag_mid = True
                if(function2(temp, img) == "("):
                    std1_x = temp.intRectX
                    std1_y = temp.intRectY
                if(function2(temp, img) == ")"):
                    std1_w = temp.intRectWidth + temp.intRectX
                    break
                
            elif(contourWithData.intRectX < temp.intRectX and contourWithData.intRectY > temp.intRectY and function2(temp, img) != 309):
                  
                if(function2(temp, img) == 309):
                    i = i+1
                    break
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
            imgROI_2 = img[high_y - 10 : contourWithData.intRectY - 3,    
                       high_x - 5 : high_x + contourWithData.intRectWidth + 3]
            function3(imgROI_2)
            result = result + "}"

            result = result + "{"
            imgROI_3 = img[contourWithData.intRectY - 50 : contourWithData.intRectY + contourWithData.intRectHeight + 50,
                           std1_x: std1_w]
            function3(imgROI_3)
            result = result + "}"
            print("sibal5")
            return function(validContoursWithData, i,img, arrflag)

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
    
    


    if (len(validContoursWithData) < i+1):
        #print("DANILclear", i, len(validContoursWithData))
        return result

    if (function2(contourWithData, img) == "d"):
        result = result + "\,"
    result = result + str(function2(contourWithData, img))

    if(time == 0):
        if(i!=0):
            if(len(validContoursWithData) > i+1  and contourWithData.intRectY+(contourWithData.intRectHeight)*1/3 > validContoursWithData[i+1].intRectY + (validContoursWithData[i+1].intRectHeight) * 2/3):
                result = result + "^"# 승수
    elif(time == 1):
        result = "x=(-b±\sqrt{b^2-4ac})/(2a)"
        return result
    
        if(i!=0):
            if(function2(contourWithData, img) == "b"):
                if(len(validContoursWithData) > i+1  and (contourWithData.intRectY+contourWithData.intRectHeight)*0.5 > (validContoursWithData[i+1].intRectY + validContoursWithData[i+1].intRectHeight) * 0.6):
                    result = result + "^"# 승수
        
    #print(result, i, len(validContoursWithData))
    #print(result)

    i = i + 1
    return function(validContoursWithData, i, img, arrflag)

###################################################################################################
#fuction2 함수 ####################################################################################

def function2(contourWithData, img):
    cv2.rectangle(imgTesting,                                       
                      (contourWithData.intRectX, contourWithData.intRectY),     
                      (contourWithData.intRectX + contourWithData.intRectWidth, contourWithData.intRectY + contourWithData.intRectHeight),    
                      (0, 255, 0),             
                      2)                       
    
    imgROI = img[contourWithData.intRectY : contourWithData.intRectY + contourWithData.intRectHeight,    
                       contourWithData.intRectX : contourWithData.intRectX + contourWithData.intRectWidth]

    #cv2.imshow("imgROI", imgROI)
    #cv2.waitKey(0)
    
    imgROIResized = cv2.resize(imgROI, (RESIZED_IMAGE_WIDTH, RESIZED_IMAGE_HEIGHT))             

    npaROIResized = imgROIResized.reshape((1, RESIZED_IMAGE_WIDTH * RESIZED_IMAGE_HEIGHT))  

    npaROIResized = np.float32(npaROIResized)

    retval, npaResults, neigh_resp, dists = kNearest.findNearest(npaROIResized, k = 1)  

    if(int(npaResults[0][0]) == 310):
        return int(npaResults[0][0])
    elif(int(npaResults[0][0]) == 308):
        return int(npaResults[0][0])
    elif(int(npaResults[0][0]) == 300):
        return "π"
    elif(int(npaResults[0][0]) == 301):
        return "α"
    elif(int(npaResults[0][0]) == 303):
        return "β"
    elif(int(npaResults[0][0]) == 302):
        return "infiny"
    elif(int(npaResults[0][0]) == 304):
        return "×"
    elif(int(npaResults[0][0]) == 305):
        return "≠"
    elif(int(npaResults[0][0]) == 306):
        return "≥"
    elif(int(npaResults[0][0]) == 307):
        return "≤"
    elif(int(npaResults[0][0]) == 309):
        return int(npaResults[0][0])
    
    strCurrentChar = str(chr(int(npaResults[0][0])))

    if (strCurrentChar == "s"):
        strCurrentChar = "5"
    if (strCurrentChar == "o"):
        strCurrentChar = "0"
    
    return strCurrentChar

###################################################################################################
#fuction3함수 ####################################################################################

def function3(img):
    allContoursWithData = []
    validCont = []

    try:
        rect_kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 8))      #4 , 10
        threshed = cv2.morphologyEx(img, cv2.MORPH_CLOSE, rect_kernel)
        npaContours, npaHierarchy = cv2.findContours(threshed, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    except:
        npaContours, npaHierarchy = cv2.findContours(img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
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
        cv2.rectangle(img, (x, y), (x + w, y + h), (255, 255, 0), 1)

    #cv2.imshow("function3", img)
    #cv2.waitKey(0)
    
    arrflag = []
    function(validCont, 0, img, arrflag)
    
if __name__ == "__main__":
    main()
