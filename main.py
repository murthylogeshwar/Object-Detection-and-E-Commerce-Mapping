import requests
import sys
import os
import cv2
import time
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from imageai.Detection import VideoObjectDetection
from imageai.Detection import ObjectDetection
from bs4 import BeautifulSoup

TIME_LIMIT = 100
HEADERS = ({'User-Agent':'Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36','Accept-Language': 'en-US, en;q=0.5'})


class Actions(QDialog):

    def __init__(self):
        
        super().__init__()
        self.initUI()       
        
    def initUI(self):
        
        self.setWindowTitle('Ecommerce Object Detection')
        self.setGeometry(200,200,300,200)

        
        self.b1 = QRadioButton(self)
        self.b1.setText("Video file")
        self.b1.move(100,40)
        self.b1.toggled.connect(self.b1_clicked)

        self.b2 = QRadioButton(self)
        self.b2.setText("Image file")
        self.b2.move(100,70)
        self.b2.toggled.connect(self.b2_clicked)
    
        self.b3 = QPushButton(self)
        self.b3.setText("Select file")
        self.b3.move(100,100)
        self.b3.clicked.connect(self.b3_clicked)
     
    
        self.b4 = QPushButton(self)
        self.b4.setText("Proceed")
        self.b4.move(100,130)
        self.b4.clicked.connect(self.b4_clicked)
        
        
        self.progress = QProgressBar(self)
        self.progress.setGeometry(50,170,200,15)
        self.progress.setMaximum(100)
        self.show()
        
    def b1_clicked(self,selected):
        if selected:       
            self.detector = VideoObjectDetection()
            self.flag=1

    def b2_clicked(self,selected): 
        if selected:
            self.detector = ObjectDetection()
            self.flag=2
    
    def b3_clicked(self):
        win = QDialog()    
        self.file = QFileDialog.getOpenFileName(win, 'Select file')[0]
        self.progress.setValue(0)
        
    def b4_clicked(self):
        
        count = 0
        window.detection_model()
        while count < TIME_LIMIT:
            count += 1
            self.progress.setValue(count)
        
    def price_link(self,item):    
        
        
          # Scrapping from Live page
            
        scrap_link = "https://www.amazon.in/s?k="+item
        page = requests.get(scrap_link, headers=HEADERS)
        soup = BeautifulSoup(page.content, features="lxml")
        print(soup)
        title = soup.find("span", attrs={"cel_widget_id":"MAIN-SEARCH_RESULTS-2"})
        temp_link=title.find("a", attrs={"class":"a-link-normal s-no-outline"})
        
        self.link =  'amazon.in'+temp_link.attrs['href']
        if(title.find("span", attrs={"class":"a-price-whole"})):
            
            self.price = title.find("span", attrs={"class":"a-price-whole"}).string
            
            if(self.price == None):
                
                self.price = "NA"    
        
        else:
            self.price = "NA"


        # # Scrapping from static_ page

        # scrap_link = os.getcwd()+'/html files/'+'Amazon.in _ '+ item +'.html'
        
        # soup = BeautifulSoup(open(scrap_link), features="lxml")
        # title = soup.find("span", attrs={"cel_widget_id":"MAIN-SEARCH_RESULTS-2"})
        # temp_link=title.find("a", attrs={"class":"a-link-normal s-no-outline"})
        
        # self.link = temp_link.attrs['href']
        
        # if(title.find("span", attrs={"class":"a-price-whole"})):
            
        #     self.price = title.find("span", attrs={"class":"a-price-whole"}).string
            
        #     if(self.price == None):
                
        #         self.price = "NA"    
        
        # else:
        #     self.price = "NA"
            
    def detection_model(self):
        
        self.detector.setModelTypeAsYOLOv3()
        self.model_path = os.getcwd() + "/yolo.h5"
        self.input_path = self.file
    
        temp = os.path.basename(self.file)
        temp = (os.path.splitext(temp))
        self.output_path = os.path.dirname(self.file)+"/"+temp[0]+"_processsed"+temp[1]
        self.detector.setModelPath(self.model_path)
        self.detector.loadModel()

        if self.flag == 2:
            
            self.detection = self.detector.detectObjectsFromImage(input_image=self.input_path, output_image_path=self.output_path)
                      
            for eachItem in self.detection:

                self.price_link(eachItem['name'])
                im = cv2.imread(self.output_path, 1)
                font = cv2.FONT_HERSHEY_SIMPLEX
                text_file = open(os.path.splitext(self.output_path)[0]+'.txt','a+')
                text_file.write(eachItem['name']+": Link : "+ self.link + '\n')
                text_file.close()
                cv2.putText(im,'Rs.'+ self.price, ((eachItem['box_points'][0]+eachItem['box_points'][2])//2,(eachItem['box_points'][1]+eachItem['box_points'][3])//2), font, 1, (255, 255, 255), 4)
                cv2.imwrite(self.output_path, im)
            
        else :
            
            cap=cv2.VideoCapture(self.input_path)
            self.fps = cap.get(cv2.CAP_PROP_FPS)
            total_frames = cap.get(cv2. CAP_PROP_FRAME_COUNT)
            self.img_array=list()
            self.frame_path = os.path.splitext(self.input_path)[0]+'_Video_Frames'
            os.makedirs(self.frame_path)
    
            def forFrame(frame_number, output_array, output_count,detected_frame):
                
                print('frame_number',frame_number,'out of',total_frames,'frames' )
                frame_location = self.frame_path+'/'+str(frame_number)+'.jpg'
                cv2.imwrite(frame_location,detected_frame)
                
                for eachItem in output_array:
                    
                    
                    self.price_link(eachItem['name'])
                    self.im = cv2.imread(frame_location, 1)
                    font = cv2.FONT_HERSHEY_SIMPLEX
                    text_file = open(os.path.splitext(frame_location)[0]+'.txt','a+')
                    text_file.write(eachItem['name']+": Link : "+ self.link + '\n')
                    text_file.close()
                    height, width, layers = self.im.shape
                    self.size = (width,height)
                    cv2.putText(self.im,'Rs.'+ self.price, ((eachItem['box_points'][0]+eachItem['box_points'][2])//2,(eachItem['box_points'][1]+eachItem['box_points'][3])//2), font, 1, (255, 255, 255), 4)
                    cv2.imwrite(frame_location,self.im)
                    
    
                self.img_array.append(self.im)  

            self.detector.detectObjectsFromVideo(input_file_path=self.input_path,output_file_path=self.output_path,frames_per_second=self.fps, per_frame_function=forFrame, minimum_percentage_probability=30,return_detected_frame=True)
 
            out = cv2.VideoWriter(self.output_path,cv2.VideoWriter_fourcc(*'DIVX'), self.fps, self.size)
 
            for i in range(len(self.img_array)):
        
                out.write(self.img_array[i])
            
            out.release()          
            os.remove(self.output_path+".avi")
            
if __name__ == "__main__":
    
    app = QApplication(sys.argv)
    
    app.setStyle("Fusion")
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(53, 53, 53))
    palette.setColor(QPalette.WindowText, Qt.white)
    app.setPalette(palette)
    
    window = Actions()
    sys.exit(app.exec_())