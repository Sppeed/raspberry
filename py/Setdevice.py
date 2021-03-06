# -*- coding: UTF-8 -*-
from importlib import reload

from PyQt5.QtSql import QSqlTableModel

from Ui_mainwindow import Ui_sysmainwindow

from newform import Ui_Newform
from logfile import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtMultimedia import *
from PyQt5.QtMultimedia import QCameraImageCapture
from time import sleep
from myThread import *

import shutil
#人脸处理
import face_recognition
from Devicetest import *
from time import sleep

import mainimg


import register
import exam
import login
import speech
import view
import configFTP
import configDB

stu_takepho_times=0 #全局变量：保存的照片命名
ident_takepho_times=0
speech_name=''
isCard = True
spkIs_end = False
Is_fin = 0
fin_same = 0


myport = ""

class setdevice(QMainWindow):
    tableviewsignal = pyqtSignal(str, str, str, int, int, bool)  # id, name, sclass, fingercount, stu_takepho_times, isCard

    def __init__(self, rights,parent=None):
        super(setdevice, self).__init__(parent)
        ##########线程#########
        self.Fpoperate = finoperation()
        self.Fpoperate.sinport.connect(self.receiveSlot)
        
        self.id = idthread()
        self.id.idport.connect(self.receiveIdslot)
        
        self.getStuid = getstuid()
        self.getStuid.getid.connect(self.matchId)
        
        self.ui = Ui_sysmainwindow()

        self.camera = None
        self.cameraDevice = None
        self.imageCapture = None
        self.mediaRecorder = None
        self.isCapturingImage = False

        self.ui.setupUi(self)

        self.setWindowFlags(Qt.FramelessWindowHint) #隐藏标签栏
        self.statusBar().setVisible(False) #隐藏状态栏 为啥没用为啥为啥 QWQ 嘤嘤嘤嘤 摔

        self.getrights(rights)#给权限
        self.setimg()#贴图

        self.spe_id_local=0


    def getrights(self, rights):
        self.ui.Teach_buttn.setVisible(rights & 0x02)  # 给权限
        self.ui.Offic_buttn.setVisible(rights & 0x04)
        self.ui.Newstu_buttn.setVisible(rights & 0x01)
        self.ui.Updata_buttn.setVisible(rights & 0x20)
        self.ui.Ident_buttn.setVisible(rights & 0x08)
        self.ui.Spk_buttn.setVisible(rights & 0x10)
        self.ui.Log_buttn.setVisible(rights & 0x40)
        self.ui.updataDeiniti_buttn.setVisible(rights & 0x40)

    def setimg(self):
        self.ui.welcome_label.setPixmap(QPixmap("./img/welcome.jpg"))

        self.ui.stu_fingers.setPixmap(QPixmap("./img/fingerscan.png"))
        self.ui.stu_idcard.setPixmap(QPixmap("./img/identimg.png"))
        self.ui.stu_photoimg.setPixmap(QPixmap("./img/noface.png"))
        self.ui.stu_fingerimg.setPixmap(QPixmap("./img/nofinger.png"))
        self.ui.stu_idimg.setPixmap(QPixmap("./img/identinotok.png"))
        self.ui.pissucc_label.setPixmap(QPixmap("./img/nosure.png"))
        self.ui.fissucc_label.setPixmap(QPixmap("./img/nosure.png"))

        self.ui.ident_fingers.setPixmap(QPixmap("./img/fingerscan.png"))
        self.ui.ident_idcard.setPixmap(QPixmap("./img/identimg.png"))
        self.ui.ident_photoimg.setPixmap(QPixmap("./img/noface.png"))
        self.ui.ident_fingerimg.setPixmap(QPixmap("./img/nofinger.png"))
        self.ui.ident_idimg.setPixmap(QPixmap("./img/identinotok.png"))

        self.ui.spkcard_label.setPixmap(QPixmap("./img/card.png"))

        self.ui.nocard_buttn.setPixmap(QPixmap("./img/card.png"))
        self.ui.nocard_buttn_2.setPixmap(QPixmap("./img/card.png"))

    def receiveSlot(self,choice,str):
        if choice==1:
            if str == '1':
                self.ui.fissucc_label.setPixmap(QPixmap("./img/sure.png"))
            else:
                print(str)
        elif choice==2:
            if str != '3':
                self.ui.ident_samebar_fin.setValue(int(str))
                print(str)

    def matchId(self,stuid):
        global ident_takepho_times

        self.Fpoperate.setvalue(2, stuid)

        #####人脸比对####
        if ident_takepho_times >0:
            pwd = os.getcwd()
            up_pwd = os.path.abspath(os.path.dirname(pwd) + os.path.sep + ".")
            resource_dir = up_pwd + '/files/examStudent/' + stuid + '_0.jpg'
            ident_dir = up_pwd + '/match_file/ident_unuser_' + str(ident_takepho_times) + '.jpg'
            #文件存在 待做
            if os.path.exists(ident_dir) and os.path.exists(resource_dir):
                # Load some images to compare against
                resource_image = face_recognition.load_image_file(resource_dir)
                ident_image = face_recognition.load_image_file(ident_dir)

                # Get the face encodings for the known images
                resource_face_encoding = face_recognition.face_encodings(resource_image)[0]
                ident_face_encoding = face_recognition.face_encodings(ident_image)[0]

                known_encodings = [
                    resource_face_encoding
                ]

                # Load a test image and get encondings for it
                # image_to_test = face_recognition.load_image_file("obama2.jpg")
                # image_to_test_encoding = face_recognition.face_encodings(image_to_test)[0]

                # See how far apart the test image is from the known faces
                face_distances = face_recognition.face_distance(known_encodings, ident_face_encoding)
                for i, face_distance in enumerate(face_distances):
                    print("The test image has a distance of {:.2} from known image #{}".format(face_distance, i))
                    print("- With a normal cutoff of 0.6, would the test image match the known image? {}".format(
                        face_distance < 0.6))
                    print("- With a very strict cutoff of 0.5, would the test image match the known image? {}".format(
                        face_distance < 0.5))
                    print()

                self.ui.ident_samebar_pho.setValue((1 - face_distances) * 100)
            else:
                #self.ui.ident_samebar_pho.setFormat("未获取到照片信息")
                self.ui.ident_samebar_pho.setValue(0)

    def receiveIdslot(self,idnum,choice):
        print("Attain IDcard:",idnum)
        if choice == 1:#new_stu
            self.ui.newstuShowname_label.setText("TestStu")
            self.ui.newstuShowclass_label.setText("000000")
            self.ui.newstuShowid_label.setText("000000")
        elif choice == 2: #ident
            self.ui.showname.setText("TestStu")
            self.ui.showclass.setText("000000")
            self.ui.showId.setText("000000")
        elif choice ==3:#spk
            self.ui.spk_stackedWidget.setCurrentIndex(3)
            self.ui.spkshowName_label.setText("TestStu")
            self.ui.spkshowClass_label.setText("000000")
            self.ui.spkshowId_label.setText("000000")
        elif choice ==4:#tea
            self.ui.newtea_stackedWidget.setCurrentIndex(1)
            self.ui.name_lineEdit.setText("000000")
        elif choice ==5:#off
            self.ui.newoff_stackedWidget.setCurrentIndex(1)
            self.ui.name_lineEdit_2.setText("000000")




    #############################无标签栏下的拖动窗口##################################
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragPosition = event.globalPos() - self.frameGeometry().topLeft()
            QApplication.postEvent(self, QEvent(174))
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            self.move(event.globalPos() - self.dragPosition)
            event.accept()

    ###########################最小化以及关闭窗口#######################################
    def minimize(self):
        self.setWindowState(Qt.WindowMinimized)

    def closewindow(self):
        #待做：警告#
        self.clearData()
        self.close()

    ###############################点击侧边栏中的按钮#####################################
    def newstushow(self):
        
        self.id.setvalue(1)
        self.ui.welcome_label.hide()
        self.ui.stackedWidget.setCurrentIndex(0)
        self.ui.newstu_tabWidget.setCurrentIndex(0)
        self.ui.text_label.setPixmap(QPixmap("./img/text.jpeg"))
        self.Fpoperate.setvalue(1,"")
        
        self.ui.centralwidget.setStyleSheet("QWidget#centralwidget{border-image: url(./img/new_bg.jpg);}")
        self.setCamera(1)
    
     

    def idenshow(self):
        
        self.id.setvalue(2)
        self.ui.welcome_label.hide()
        self.ui.stackedWidget.setCurrentIndex(1)
        self.ui.ident_tab.setCurrentIndex(0)

        self.ui.ident_samebar_pho.setValue(0)
        self.ui.ident_samebar_fin.setValue(0)

        self.ui.text_label.setPixmap(QPixmap(" "))
        self.initiUpload()
        self.examIds()
        
        self.ui.centralwidget.setStyleSheet("QWidget#centralwidget{border-image: url(./img/exam_bg.jpg);}")
        self.setCamera(2)
        

    def spkshow(self):
        
        if self.camera:
            print(¨¨
            sleep(0.2)
            self.camera.stop()
            sleep(0.2)
            self.camera.unload()
            sleep(0.2)

        self.id.setvalue(3)
        self.ui.welcome_label.hide()
        self.ui.text_label.setPixmap(QPixmap(" "))
        self.ui.stackedWidget.setCurrentIndex(2)
        self.ui.spk_stackedWidget.setCurrentIndex(0)
        self.ui.centralwidget.setStyleSheet(S
    def updatashow(self):
        
        if self.camera:
            sleep(0.2)
            self.camera.stop()
            sleep(0.2)
            self.camera.unload()
            sleep(0.2)

        self.id.setvalue(0)
        self.ui.welcome_label.hide()
        self.ui.ident_samebar_fin.setValue(0)
        self.ui.ident_samebar_fin.setValue(0)
        self.ui.text_label.setPixmap(QPixmap(" "))
        self.initiUpdata()
        self.ui.updata_tabWidget.setCurrentIndex(0)
        self.ui.stackedWidget.setCurrentIndex(3)
        self.ui.centralwidget.setStyleSheet("QWidget#centralwidget{border-image: url(./img/log_bg.jpg);}")


    def logshow(self):
        
        if self.camera:
            sleep(0.2)
            self.camera.stop()
            sleep(0.2)
            self.camera.unload()
            sleep(0.2)

        self.id.setvalue(0)
        self.ui.welcome_label.hide()
        self.ui.text_label.setPixmap(QPixmap(" "))
        self.ui.centralwidget.setStyleSheet("QWidget#centralwidget{border-image: url(./img/log_bg.jpg);}")
        str = rlogfile()
        self.ui.textBrowser.setText(str)


    def teashow(self):
        
        if self.camera:
    
            sleep(0.2)
            self.camera.stop()
            sleep(0.2)
            self.camera.unload()
            sleep(0.2)

        self.id.setvalue(4)
        self.ui.welcome_label.hide()
        self.ui.text_label.setPixmap(QPixmap(" "))
        self.ui.stackedWidget.setCurrentIndex(5)
        self.ui.newtea_stackedWidget.setCurrentIndex(0)
        self.ui.centralwidget.setStyleSheet("QWidget#centralwidget{border-image: url(./img/new_bg.jpg);}")

    def offshow(self):
        
        if self.camera:
        
            sleep(0.2)
            self.camera.stop()
            sleep(0.2)
            self.camera.unload()
            sleep(0.2)
        
        self.id.setvalue(5)
        self.ui.welcome_label.hide()
        self.ui.text_label.setPixmap(QPixmap(" "))
        self.ui.stackedWidget.setCurrentIndex(6)
        self.ui.newoff_stackedWidget.setCurrentIndex(0)
        self.ui.centralwidget.setStyleSheet("QWidget#centralwidget{border-image: url(./img/new_bg.jpg);}")

########################是否架设相机################################
    def setCamera(self,i):
       
       # if cameraDevice.isEmpty():
      #      self.camera = QCamera()
     #   else:
    #        self.camera = QCamera(cameraDevice)
    
        self.camera = QCamera()   
        if self.camera.state() == QCamera.ActiveState:
            sleep(0.2)
            self.camera.stop()
            sleep(0.2)
            self.camera.unload()
            sleep(0.2)
            #self.camera.load()
    
        #self.camera.load()
        self.camera.error.connect(self.displayCameraError)
        self.imageCapture = QCameraImageCapture(self.camera)

        if i==1:
            self.camera.setViewfinder(self.ui.viewfinder2)
            self.imageCapture.imageCaptured.connect(self.processCapturedImage_1)
            self.imageCapture.imageSaved.connect(self.imageSaved)

        elif i==2:
            self.camera.setViewfinder(self.ui.viewfinder)
            self.imageCapture.imageCaptured.connect(self.processCapturedImage_2)
            self.imageCapture.imageSaved.connect(self.imageSaved_2)

        #sizeList = self.camera.supportedViewfinderResolutions()
        #print("支持的大小：", sizeList)
        viewfindersettings = QCameraViewfinderSettings()
        viewfindersettings.setResolution(352, 288)
        viewfindersettings.setPixelFormat(4)#set format like jpeg/h.264 etc.
        self.camera.setViewfinderSettings(viewfindersettings)
        
        self.camera.start()


    
            
##############################静态图像捕捉######################################

    ############新生注册#############
    def processCapturedImage_1(self, requestId, img):
        scaledImage = img.scaled(self.ui.viewfinder.size(), Qt.KeepAspectRatio,
                                 Qt.SmoothTransformation)
        self.ui.stu_photoimg.setPixmap(QPixmap.fromImage(scaledImage))
        self.ui.pissucc_label.setPixmap(QPixmap("./img/sure.png"))


    ##########监考模式#############
    def processCapturedImage_2(self, requestId, img):
        scaledImage = img.scaled(self.ui.viewfinder.size(), Qt.KeepAspectRatio,
                                 Qt.SmoothTransformation)
        self.ui.ident_photoimg.setPixmap(QPixmap.fromImage(scaledImage))


    def captureImage(self):
        self.isCapturingImage = True
        self.imageCapture.capture()

    def displayCameraError(self):
        QMessageBox.warning(self, "Camera error", self.camera.errorString())

    ############相片存储：新生注册####################
    def imageSaved(self):
        pixmap = self.ui.stu_photoimg.pixmap()
        pwd = os.getcwd()  # 当前文件路径
        img_pwd = os.path.abspath(os.path.dirname(pwd) + os.path.sep + ".")
        img_pwd = img_pwd + '/files/registerStudent'
        os.chdir(img_pwd)
        os.getcwd()
        global stu_takepho_times
        stu_takepho_times += 1

        savename = 'stu_unuser_' + str(stu_takepho_times) + '.jpg'
        print(savename)
        if (pixmap):
            pixmap.save(savename)
        os.chdir(pwd)
        os.getcwd()

    ############相片存储：监考模式####################
    def imageSaved_2(self):
        pixmap = self.ui.ident_photoimg.pixmap()
        pwd = os.getcwd()  # 当前文件路径
        up_pwd = os.path.abspath(os.path.dirname(pwd) + os.path.sep + ".")
        img_pwd = up_pwd
        img_pwd = img_pwd + '/match_file'
        os.chdir(img_pwd)
        os.getcwd()
        global ident_takepho_times
        ident_takepho_times += 1

        savename = 'ident_unuser_' + str(ident_takepho_times) + '.jpg'
        print(savename)
        if (pixmap):
            pixmap.save(savename)
            stuid = self.ui.showId.text()
            if stuid != '':
                #人脸比对
                resource_dir = up_pwd + '/files/examStudent/' + stuid + '_0.jpg'
                ident_dir = up_pwd + '/match_file/ident_unuser_' + str(ident_takepho_times) + '.jpg'
                if os.path.exists(ident_dir) and os.path.exists(resource_dir):
                    # Load some images to compare against
                    resource_image = face_recognition.load_image_file(resource_dir)
                    ident_image = face_recognition.load_image_file(ident_dir)

                    # Get the face encodings for the known images
                    resource_face_encoding = face_recognition.face_encodings(resource_image)[0]
                    ident_face_encoding = face_recognition.face_encodings(ident_image)[0]

                    known_encodings = [
                        resource_face_encoding
                    ]

                    # Load a test image and get encondings for it
                    # image_to_test = face_recognition.load_image_file("obama2.jpg")
                    # image_to_test_encoding = face_recognition.face_encodings(image_to_test)[0]

                    # See how far apart the test image is from the known faces
                    face_distances = face_recognition.face_distance(known_encodings, ident_face_encoding)
                    for i, face_distance in enumerate(face_distances):
                        print("The test image has a distance of {:.2} from known image #{}".format(face_distance, i))
                        print("- With a normal cutoff of 0.6, would the test image match the known image? {}".format(
                            face_distance < 0.6))
                        print(
                            "- With a very strict cutoff of 0.5, would the test image match the known image? {}".format(
                                face_distance < 0.5))
                        print()

                    self.ui.ident_samebar_pho.setValue((1 - face_distances) * 100)
                else:
                    # self.ui.ident_samebar_pho.setFormat("未获取到照片信息")
                    self.ui.ident_samebar_pho.setValue(0)

        os.chdir(pwd)
        os.getcwd()
##########################新生注册+监考模式：无卡用户填写表单#############################

    #####################新生注册###################
    def shownew_newstu(self):
        # 记录是否使用学生卡
        global isCard
        isCard = False

        new_window = Ui_Newform(parent=self)

        # 居中弹出
        new_window.move((QApplication.desktop().width() - new_window.width())/2,(QApplication.desktop().height() - new_window.height())/2)

        new_window.setWindowTitle("填写表格")

        if new_window.exec_():
            self.ui.newstuShowname_label.setText(new_window.get_name())
            self.ui.newstuShowclass_label.setText(new_window.get_class())
            self.ui.newstuShowid_label.setText(new_window.get_id())

            new_window.destroy()

    #####################监考模式###################
    def shownew_ident(self):
        # 记录是否使用学生卡
        global isCard
        isCard = False

        new_window = Ui_Newform(parent=self)

        # 居中弹出
        new_window.move((QApplication.desktop().width() - new_window.width()) / 2, (QApplication.desktop().height() - new_window.height()) / 2)

        new_window.setWindowTitle("填写表格")

        if new_window.exec_():
            self.ui.showname.setText(new_window.get_name())
            self.ui.showclass.setText(new_window.get_class())
            self.ui.showId.setText(new_window.get_id())

            self.getStuid.setstuid(self.ui.showId.text())

            new_window.destroy()

#!!!!DB->本地数据库!!!!!#############新生录入的"完成录入"按钮###############################################
    def finish_stu(self):
        '''#test
        global Finger
        global Idcard
        if Finger==-1:
            QMessageBox.information(self, "错误", "缺少指纹信息", QMessageBox.Ok)
            return

        if Idcard==-1:
            QMessageBox.information(self, "错误", "缺少磁卡信息", QMessageBox.Ok)
            return
        '''
        # is_finger() # 等待硬件部分ing
        # is_card() # 等待硬件部分ing

        global isCard
        global stu_takepho_times


        name = self.ui.newstuShowname_label.text()
        sclass = self.ui.newstuShowclass_label.text()
        id = self.ui.newstuShowid_label.text()

        if name and sclass and id:
            #判断学号和班级是否均由数字组成
            if id.isdigit() and sclass.isdigit():

                fingercount = self.renameFP(1)  # 返回指纹数量
                #fingercount=1#test
                if fingercount == 0:
                    QMessageBox.information(self, "错位", "未录入指纹信息", QMessageBox.Ok)
                    return

                if self.renamephoto(1):  # 用户确认录入信息，检测并更改照片的命名方式，参数'1'表示：新生注册模式

                    ##################################################################################
                    ####################DB：本地数据库， <插入> 当前采集的 -新生- 信息#####################
                    ##################################################################################
                    # stu_takepho_times  新生注册照片数量                                              #
                    #                                                                                #
                    #                                                                                #
                    ##################################################################################
                    stu_takepho_times = 0
                    register.registerStudentInsert(id, name, sclass, fingercount, stu_takepho_times, isCard)
                    #configFTP.registerStudentCreateFiles(id,1,0)
#                    self.tableviewsigna.emit(id, name, sclass, fingercount, stu_takepho_times, isCard)
                    QMessageBox.information(self, "成功", "已完成当前录入", QMessageBox.Ok)
                    self.ui.newstu_tableview.filter('', '', '', 'All', 'All')

                    # 重置，等待下一位录入者
                    isCard = True
                    self.ui.stu_photoimg.setPixmap(QPixmap("./img/noface.png"))
                    self.ui.pissucc_label.setPixmap(QPixmap("./img/nosure.png"))
                    self.ui.fissucc_label.setPixmap(QPixmap("./img/nosure.png"))
                    self.ui.newstuShowname_label.clear()
                    self.ui.newstuShowclass_label.clear()
                    self.ui.newstuShowid_label.clear()
                    stu_takepho_times = 0

                    return
                else:
                    QMessageBox.information(self, "未完成录入", "照片信息未录入", QMessageBox.Ok)

            else:
                QMessageBox.information(self, "未完成录入", "学号或班级输入不合法", QMessageBox.Ok)

        else:
            QMessageBox.information(self,"未完成录入","磁卡信息未录入",QMessageBox.Ok)

    def finish_ident(self):
        '''#test
        global Finger
        global Idcard
        # is_finger()
        if Finger == -1:
            QMessageBox.information(self, "错误", "缺少指纹信息", QMessageBox.Ok)
            return
        # is_card()
        if Idcard == -1:
            QMessageBox.information(self, "错误", "缺少磁卡信息", QMessageBox.Ok)
            return
        #else :将Id卡解析的信息写入showlabel
        '''
        global isCard
        global ident_takepho_times
        name = self.ui.showname.text()
        sclass = self.ui.showclass.text()
        id = self.ui.showId.text()
        exam_id = self.ui.identchoiceexam_comboBox.currentText()  # 考场信息
        fingercount = 2  # 指纹数量finger
        sfinger = 80  # 相似度sim_figer
        sface = self.ui.ident_samebar_pho.value() # 相似度sin_face
        print(sface)
        imatched = True  # 是否匹配is_matched

        if exam_id:
            if name and sclass and id:
                if id.isdigit() and sclass.isdigit():
                    if self.renamephoto(2) :# 用户确认录入信息，检测并更改照片的命名方式，参数'1'表示 监考模式
                        ##################################################################################
                        ####################DB：本地数据库， <插入> 当前采集的 -考生- 信息#####################
                        ##################################################################################
                        # ident_take                                                                     #
                        # ident_takepho_times照片数量                                                     #
                        # isCard 是否是有卡                                                               #
                        ##################################################################################
                        info = (exam_id,id)
                        print(*info)
                        attribute = exam.examRecordGetAttribute(*info)
                        configFTP.examRecordCreateFiles(*info,1,0)
                        if attribute == 'Empty':
                            if QMessageBox.Yes == QMessageBox.question(self, "question", "您不在当前考表中,如果确认考试信息无误,请继续...",
                                                                       QMessageBox.No,QMessageBox.Yes):
                                exam.examStudentAppend(info[1],name,sclass)
                                exam.examRecordInsert(info[0], info[1], fingercount, 0, ident_takepho_times, 0, isCard, 'True', 'False')

                        elif attribute == 'Appended':
                            exam.examRecordInsert(info[0], info[1], fingercount, 0, ident_takepho_times, 0, isCard, 'True', 'False')

                        elif attribute == 'Normal':
                            exam.examRecordInsert(info[0], info[1], fingercount, sfinger, ident_takepho_times, sface, isCard, 'False', imatched)

                        self.ui.tableView.filter('', '', '', '', 'All', 'All', 'All', 'All', 'All')
                        self.ui.ident_photoimg.setPixmap(QPixmap("./img/noface.png"))
                        # ！待做：进度条重制
                        isCard = True
                        self.ui.showname.clear()
                        self.ui.showclass.clear()
                        self.ui.showId.clear()
                        ident_takepho_times=0
                        QMessageBox.information(self, "成功", "已完成当前录入", QMessageBox.Ok)

                    else:
                        QMessageBox.information(self, "未完成录入", "照片信息未录入", QMessageBox.Ok)

                else:
                    QMessageBox.information(self, "未完成录入", "学号或班级输入不合法", QMessageBox.Ok)

            else:
                QMessageBox.information(self, "未完成录入", "磁卡信息未录入",QMessageBox.Ok)
        else:
            QMessageBox.information(self, "未完成录入", "未选择考场", QMessageBox.Ok)
        return

    def newstutableview(self):
        self.ui.newstu_tableview.filter('', '', '', 'All', 'All')

    def renameFP(self,choice):
        pwd = os.getcwd()
        fp_pwd = os.path.abspath(os.path.dirname(pwd) + os.path.sep + ".")

        is_fp = 0
        '''新生注册，只保留最后一次指纹，并以学号_0命名，保存格式：.txt'''

        if choice == 1:
            fp_pwd = fp_pwd + '/files/registerStudent'
            oldpex = 'FP'
            ltime = -1  # 获取文件最后修改时间
            lastfile = ''
            for parent, dirnames, filenames in os.walk(fp_pwd):
                for filename in filenames:
                    if filename.find(oldpex) != -1:
                        is_fp +=1
                        ft = os.stat(fp_pwd + "/" + filename)
                        fltime = int(ft.st_mtime)  # 获取文件最后修改时间
                        if fltime>ltime :
                            ltime = fltime
                            if lastfile != '':
                                if os.path.exists(fp_pwd + "/" + lastfile) :#指定路径（文件或者目录）是否存在
                                   os.remove(os.path.join(parent, lastfile))

                            lastfile = filename
                        else:
                            os.remove(os.path.join(parent, filename))

                        newName = self.ui.newstuShowid_label.text() + "_0.txt"
                        print(filename, "---->", newName)
                        os.rename(os.path.join(parent, filename), os.path.join(parent, newName))
        return is_fp


    #########相片重命名###########
    def renamephoto(self, choice):
        global stu_takepho_times
        global ident_takepho_times
        pwd = os.getcwd()
        img_pwd = os.path.abspath(os.path.dirname(pwd) + os.path.sep + ".")

        is_photo = False
        '''新生注册，只保留最后一张照片，并以学号命名，保存格式：.jpg'''

        if choice == 1:
            img_pwd = img_pwd + '/files/registerStudent'
            oldpex = "stu_unuser_" + str(stu_takepho_times)
            newpex = self.ui.newstuShowid_label.text() + "_0"
            resume = oldpex + '.jpg'

            for parent, dirnames, filenames in os.walk(img_pwd):
                for filename in filenames:
                    if filename != resume  :
                        if filename.find("stu_unuser_") != -1:
                            os.remove(os.path.join(parent, filename))
                    else:
                        if filename.find(oldpex) != -1:
                            is_photo = True
                            newName = filename.replace(oldpex, newpex)
                            print(filename, "---->", newName)  # test
                            os.rename(os.path.join(parent, filename), os.path.join(parent, newName))



        elif choice == 2:
            examid = self.ui.identchoiceexam_comboBox.currentText()
            store_pwd = img_pwd +'/files/examRecord/'+examid
            img_pwd = img_pwd + '/match_file'

            oldpex = "ident_unuser"
            newpex = self.ui.showId.text()
            for parent, dirnames, filenames in os.walk(img_pwd):
                for filename in filenames:
                    if filename.find(oldpex) != -1:
                        is_photo = True
                        newName = filename.replace(oldpex, newpex)
                        print(filename, "---->", newName)  # test
                        os.rename(os.path.join(parent, filename), os.path.join(parent, newName))
                        movefile=img_pwd+'/'+newName
                        if os.path.exists(store_pwd):
                            storefin_pwd = store_pwd + '/' + newName
                            shutil.move(movefile, storefin_pwd)
                            print(movefile, '----->', store_pwd)
                        else:
                            print("考场目录不存在")
                            QMessageBox.information(self,"错误",'考场目录缺失',QMessageBox.Ok)
                            return



        return is_photo


#!!!!DB:本地数据库查询!!!!!!#########新生注册：查看按钮#######################################
    def newstuFind(self):
        name=self.ui.newstuName_lineEdit.text()
        sclass=self.ui.newstuClass_lineEdit.text()
        id=self.ui.newstuId_lineEdit.text()
        is_fin=self.ui.newstuFinger_combox.currentText()
        is_fac=self.ui.newstuFinger_combox_2.currentText()
        ##################################################################################
        ####################DB：本地数据库， <查询> 当前记录的 -新生- 信息#####################
        ##################################################################################
        # 并显示在表单里面                                                                 #
        #                                                                                #
        #                                                                                #
        ##################################################################################
        self.ui.newstu_tableview.filter(id,name,sclass,is_fin,is_fac)


#!!!!DB:本地数据库上传至服务器!!!!!!#########新生注册：上传按钮#######################################
    def newstuUpload(self):
        ##################################################################################
        ####################DB：本地数据库， <上传> 当前适配的 -新生- 信息#####################
        ##################################################################################
        #表单中选中的新生信息                                                               #
        #                                                                                #
        #                                                                                #
        ##################################################################################
        newstu = self.ui.newstu_tableview.getKeys()
        print(*newstu)
        if newstu:
            try:
                register.registerStudentUpload(*newstu)
                self.ui.newstu_tableview.filter('', '', '', 'All', 'All')
                QMessageBox.information(self, "成功", "上传成功", QMessageBox.Ok)
            except:
                QMessageBox.information(self, "错误", "用户名暂不支持中文", QMessageBox.Ok)
                print(TypeError)
        else:
            QMessageBox.information(self, "错误", "请选择上传对象", QMessageBox.Ok)
        #register.registerStudentUpload("")
#!!!!!DB:本地数据库，将考场信息添加到combox中##############################################
    def initiUpload(self):
        ##################################################################################
        ####################DB：本地数据库， 将考场信息添加到identExamnum_comboBox中 ##########
        ##################################################################################
        # 添加到self.ui.identExamnum_comboBox中                                           #
        #                                                                                #
        #                                                                                #
        ##################################################################################
        #self.ui.identExamnum_comboBox.addItem("1")
        if exam.examExamShow():
            self.ui.identExamnum_comboBox.clear()
            for row in exam.examExamShow():
                self.ui.identExamnum_comboBox.addItem(str(*row))
                print(str(row))
        else:
            self.ui.identExamnum_comboBox.clear()


        #self.ui.identExamnum_comboBox.Items.Add()

    def examIds(self):
        if exam.examExamShow():
            self.ui.identchoiceexam_comboBox.clear()
            for row in exam.examExamShow():
                self.ui.identchoiceexam_comboBox.addItem(str(*row))
                print(str(row))
        else:
            self.ui.identchoiceexam_comboBox.clear()

#!!!!!!DB:本地数据库<查询>!!!!!!############监考模式：比对的学生信息###########################
    def identFind(self):
        examId = self.ui.identExamnum_comboBox.currentText()
        stuId = self.ui.identId_lineEdit.text()
        name = self.ui.identName_lineEdit.text()
        stuclass = self.ui.identClass_lineEdit.text()
        is_fin = self.ui.identFinger_combox.currentText()
        is_photo = self.ui.identFace_combox.currentText()
        is_iccard = self.ui.identIC_combox.currentText()
        is_match = self.ui.identIsmatch_comboBox.currentText()
        is_append = self.ui.identIsappend_comboBox.currentText()
        ##################################################################################
        ####################DB：本地数据库， 查询考试记录中     ##############################
        ##################################################################################
        # 添加到table界面中                                                                #
        #                                                                                #
        #                                                                                #
        ##################################################################################
        self.ui.tableView.filter(examId,stuId,name,stuclass,is_fin,is_photo,is_iccard,is_match,is_append)


#!!!DB:本地数据库上传到服务器!!!!!########监考模式：上传选中的信息###############################
    def identUpload(self):
        examstu = self.ui.tableView.getKeys()
        print(*examstu)
        if examstu:
            try:
                exam.examRecordUpload(*examstu)
                self.ui.tableView.filter('', '', '', '', 'All', 'All', 'All', 'All', 'All')
                QMessageBox.information(self, "成功", "上传成功", QMessageBox.Ok)
            except:
                QMessageBox.information(self, "错误", "用户名暂不支持中文", QMessageBox.Ok)
                print(TypeError)
        else:
            QMessageBox.information(self, "错误", "请选择上传对象", QMessageBox.Ok)
        ##################################################################################
        ####################DB：本地数据库上传到考试记录中     ###############################
        ##################################################################################
        #上传选中的数据                                                                    #
        #全选按钮：identChoicall_checkbox                                                 #
        #                                                                                #
        ##################################################################################

    #################################讲座模式####################################
    def spkbackhome(self):
        self.ui.spk_stackedWidget.setCurrentIndex(0)

    def spkstart(self):
        self.ui.spk_stackedWidget.setCurrentIndex(4)

    def submitSpeechname(self):
        global speech_name
        global spkIs_end
        speech_name = self.ui.spkSubmit_lineEdit.text()
        speech_room = self.ui.spkSubmitroom_lineEdit.text()
        if speech_name and speech_room :
            spkIs_end=True
            self.spe_id_local = speech.speechSpeechInsert(speech_name, speech_room)
            self.ui.spk_stackedWidget.setCurrentIndex(1)
            text="当前正在 【入场】 签到的讲座是："+speech_name
            self.ui.spkCurspeech_label.setText(text)
            self.ui.spkSubmit_lineEdit.clear()
            self.ui.spkSubmitroom_lineEdit.clear()
        else:
            QMessageBox.information(self, "表单未填写完整", "请输入表单的所有选项", QMessageBox.Ok)

    def spkcon(self):
        global speech_name
        if speech_name  == "":
            QMessageBox.information(self,"错误","没有进行中的讲座，请先开始一个讲座",QMessageBox.Ok)
            self.ui.spk_stackedWidget.setCurrentIndex(0)
        else:
            self.ui.spk_stackedWidget.setCurrentIndex(1)

    def spkend(self):
        global speech_name
        global spkIs_end
        if speech_name == '':
            QMessageBox.information(self, "错误", "没有进行中的讲座，请先开始一个讲座", QMessageBox.Ok)
            self.ui.spk_stackedWidget.setCurrentIndex(0)
            return
        else:
            text = "当前正在 【离场】 签到的讲座是：" + speech_name
            self.ui.spkCurspeech_label.setText(text)
            spkIs_end = False
            self.ui.spk_stackedWidget.setCurrentIndex(1)
            return

    def spksubmitinfo(self):
        count_id = len(self.ui.spkn_id_lineEdit.text())
        count_class = len(self.ui.spkn_class_lineEdit.text())
        if not self.ui.spk_name_lineEdit.text() or not self.ui.spkn_class_lineEdit.text() or not self.ui.spkn_id_lineEdit.text():
            QMessageBox.information(self, "错误", "未填写完所有表项，请检查")
        elif count_id > 10:
            QMessageBox.information(self, "错误", "学号位数错误", QMessageBox.Ok)
        elif count_class > 10:
            QMessageBox.information(self, "错误", "班级位数错误", QMessageBox.Ok)
        else:
            global spkIs_end
            speechname = self.ui.spkSubmit_lineEdit.text()
            speechclass = self.ui.spkSubmitroom_lineEdit.text()
            id = self.ui.spkn_id_lineEdit.text()
            self.ui.spk_tableView.filter('')

            ##################################################################################
            #############DB：本地数据库， <插入> 当前采集的 -讲座签到的学生- 信息###################
            ##################################################################################
            # 全局变量：spkIs_end=Ture 讲座开始 （入场）                                         #
            #         spkIs_end=False 讲座结束 （离场）                                        #
            #         speech_name 讲座名称                                                    #
            ##################################################################################

            if spkIs_end:
                speech.speechRecordInsertFirst(self.spe_id_local, id)
                self.ui.spk_tableView.filter('')
            else:
                speech.speechRecordInsertSecond(self.spe_id_local, id)
                self.ui.spk_tableView.filter('')
            self.ui.spk_stackedWidget.setCurrentIndex(3)
            self.ui.spkshowName_label.setText(self.ui.spk_name_lineEdit.text())
            self.ui.spkshowClass_label.setText(self.ui.spkn_class_lineEdit.text())
            self.ui.spkshowId_label.setText(self.ui.spkn_id_lineEdit.text())
            self.ui.spk_name_lineEdit.clear()
            self.ui.spkn_class_lineEdit.clear()
            self.ui.spkn_id_lineEdit.clear()

    def spkback(self):
        self.ui.spk_stackedWidget.setCurrentIndex(1)
        self.ui.spk_name_lineEdit.clear()
        self.ui.spkn_class_lineEdit.clear()
        self.ui.spkn_id_lineEdit.clear()

    def spkNocard(self):
        self.ui.spk_stackedWidget.setCurrentIndex(2)
#!!!!DB:本地数据库!!!!!!!##################讲座签到 <插入> 学生信息###################################

    def spkDB(self):
        self.ui.spk_stackedWidget.setCurrentIndex(1)
        self.ui.spkshowName_label.clear()
        self.ui.spkshowClass_label.clear()
        self.ui.spkshowId_label.clear()
#!!!!DB:本地数据库<查询>################讲座上传-根据讲座名称查询############################
    def spkFind(self):
        spkFindspeech=self.ui.spkspeech_lineEdit.text()#查询输入的讲座名字
        ##################################################################################
        #############DB：本地数据库， <查询> 当前输入的 -讲座名称- 信息########################
        ##################################################################################
        #将查询到的信息显示出来                                                             #
        #                                                                                #
        ##################################################################################
        self.ui.spk_tableView.filter(spkFindspeech)
##!!!!!!!DB:服务器<——本地数据库 <上传>################讲座上传-上传按钮############################
    def spkUpload(self):
        ##################################################################################
        #############DB：本地数据库-->服务器， <上传> 适配的讲座信息###########################
        ##################################################################################
        #                                                                                #
        #                                                                                #
        ##################################################################################
        spkRecord = self.ui.spk_tableView.getKeys()
        print(spkRecord)
        if spkRecord:
            try:
                speech.speechSpeechUpload(*spkRecord)
                self.ui.spk_tableView.filter('')
                QMessageBox.information(self, "成功", "上传成功", QMessageBox.Ok)
            except:
                QMessageBox.information(self, "错误", "用户名暂不支持中文", QMessageBox.Ok)
                print(TypeError)
        else:
            QMessageBox.information(self, "错误", "请选择上传对象", QMessageBox.Ok)
    def newtea_nocard(self):
        self.ui.newtea_stackedWidget.setCurrentIndex(1)

    def newoff_nocard(self):
        self.ui.newoff_stackedWidget.setCurrentIndex(1)

    def newoffback(self):
        self.ui.newoff_stackedWidget.setCurrentIndex(0)

    def newteacontinue(self):
        self.ui.newtea_stackedWidget.setCurrentIndex(0)
        self.ui.name_lineEdit.clear()
        self.ui.pass_lineEdit.clear()
        self.ui.secpasswd_lineEdit.clear()

    def newoffcontinue(self):
        self.ui.newoff_stackedWidget.setCurrentIndex(0)
        self.ui.name_lineEdit_2.clear()
        self.ui.pass_lineEdit_2.clear()
        self.ui.secpasswd_lineEdit_2.clear()


#!!!!DB：本地数据库UserAdd！##########教师与管理员"确认"按钮##########################################
    def tea_success(self):
        name = self.ui.name_lineEdit.text()
        passwd = self.ui.pass_lineEdit.text()
        secpass = self.ui.secpasswd_lineEdit.text()
        count_id = len(self.ui.name_lineEdit.text())
        if count_id<=10:
            if name and passwd and secpass:
                if name.isdigit():
                    if passwd == secpass:
                        ##################################################################################
                        #############DB：本地数据库， <插入> 当前采集的 -用户（useradd)- 信息##################
                        ##################################################################################
                        #教师权限                                                                         #
                        #                                                                                #
                        #                                                                                #
                        ##################################################################################
                        login.loginUserInsert(name,passwd,"24")
                        self.ui.newtea_stackedWidget.setCurrentIndex(2)
                        self.ui.newtea_tableView.filter(24)
                        self.ui.newtea_tableView.selectAll()
                    else:
                        QMessageBox.information(self, "错误", "两次输入的密码不同，请重新输入", QMessageBox.Ok)
                else:
                    QMessageBox.information(self, "错误", "用户名不合规范，请重新输入", QMessageBox.Ok)
            else:
                QMessageBox.information(self, "未完成录入", "请填写所有表项", QMessageBox.Ok)
        else:
            QMessageBox.information(self, "错误", "用户id位数错误，请重新输入", QMessageBox.Ok)


    def off_success(self):

        name = self.ui.name_lineEdit_2.text()
        passwd = self.ui.pass_lineEdit_2.text()
        secpass = self.ui.secpasswd_lineEdit_2.text()
        count_id = len(self.ui.name_lineEdit_2.text())
        if count_id <= 10:
            if name and passwd and secpass:
                if name.isdigit():
                    if passwd == secpass:
                        ##################################################################################
                        ##############DB：本地数据库， <插入> 当前采集的 -用户（useradd)- 信息#################
                        ##################################################################################
                        #管理员权限                                                                       #
                        #                                                                                #
                        #                                                                                #
                        ##################################################################################
                        login.loginUserInsert(name,passwd,"35")
                        self.ui.newoff_stackedWidget.setCurrentIndex(2)
                        self.ui.newoff_tableView.filter(35)
                        self.ui.newoff_tableView.selectAll()
                    else:
                        QMessageBox.information(self, "错误", "两次输入的密码不同，请重新输入", QMessageBox.Ok)
                else:
                    QMessageBox.information(self, "错误", "用户名不合规范，请重新输入", QMessageBox.Ok)
            else:
                QMessageBox.information(self, "未完成录入", "请填写所有表项", QMessageBox.Ok)
        else:
            QMessageBox.information(self, "错误", "用户id位数错误，请重新输入", QMessageBox.Ok)

#!!!!!DB:上传至服务器！！！！###############用户上传（教师与管理员的上传函数）##########################
    def newteaUpload(self):
        ##################################################################################
        ##############DB：上传至服务器， <上传> 当前采集的 -教师（useradd)- 信息#################
        ##################################################################################
        #                                                                                #
        #                                                                                #
        #                                                                                #
        ##################################################################################
        #self.ui.newtea_tableView.selectAll()
        newtea = self.ui.newtea_tableView.getKeys()
        print(*newtea)
        login.loginUserUpload(*newtea)
        QMessageBox.information(self, "成功", "上传成功", QMessageBox.Ok)

    def newoffUpload(self):
        ##################################################################################
        ##############DB：上传至服务器， <上传> 当前采集的 -教务处（useradd)- 信息#################
        ##################################################################################
        #                                                                                #
        #                                                                                #
        #                                                                                #
        ##################################################################################
        #self.ui.newoff_tableView.selectAll()
        newoff = self.ui.newoff_tableView.getKeys()
        login.loginUserUpload(*newoff)
        QMessageBox.information(self, "成功", "上传成功", QMessageBox.Ok)

#!!!!!DB:从服务下载数据!!!!!###########数据更新：自动显示#########################################
    def initiUpdata(self):
        pass
        ##################################################################################
        ##############DB：从服务器自动显示数据， 显示在tableview 中           #################
        ##################################################################################
        # self.ui.upexam_tableView #考场信息表                                              #
        # self.updata_tableView  #用户信息表                                                #
        #                                                                                #
        ##################################################################################

 #!!!!!DB:从服务下载到本地数据库与!!!!!###########数据更新：考试信息更新#########################################
    def updataUpeaxm(self):
        updataExam = self.ui.upexam_tableView.getKeys()
        print(*updataExam)
        if updataExam:
            exam.examExamDownload(*updataExam)
            exam.examMemberDownload(*updataExam)
            exam.examStudentDownload(*updataExam)
            self.ui.upexam_tableView.filter('','','','')
            QMessageBox.information(self, "成功", "下载成功", QMessageBox.Ok)
        else:
            QMessageBox.information(self, "错误", "请选择考场", QMessageBox.Ok)
        ##################################################################################
        ##############DB：根据服务器自动显示数据，下载表（这个是有选择性的下载） #################
        ##################################################################################
        # self.ui.upexam_tableView #考场信息表                                             #
        # self.ui.upexamAll_checkBox #全选按钮                                            #
        #                                                                                #
        ##################################################################################

#!!!!!DB:从服务下载到本地数据库与!!!!!###########数据更新：用户信息跟新#########################################
    def updataUpuser(self):
        #updata = upuserthread()
        #updata.start()
        login.loginUserDownload()
        self.ui.updata_tableView.filter()
        QMessageBox.information(self, "成功", "下载成功", QMessageBox.Ok)
        ##################################################################################
        ##############DB：根据服务器自动显示数据，下载表（这个是全部下载）#######################
        ##################################################################################
        # self.updata_tableView  #用户信息表                                              #
        #                                                                                #
        #                                                                                #
        ##################################################################################

    def updataDel(self):

        if QMessageBox.Yes==QMessageBox.question(self,"question", "确定清空本地数据？",QMessageBox.No,QMessageBox.Yes):
            configDB.clearLocalDB()
            self.ui.newstu_tableview.filter('', '', '', 'All', 'All')
            self.ui.tableView.filter('', '', '', '', 'All', 'All', 'All', 'All', 'All')
            self.ui.spk_tableView.filter('')
            self.ui.upexam_tableView.filter('', '', '', '')
            self.ui.updata_tableView.filter()
            self.ui.newtea_tableView.filter(24)
            self.ui.newoff_tableView.filter(35)
            ###加入清空文件夹
            self.clearAllfiles()
            QMessageBox.information(self, "成功", "清空本地数据库成功", QMessageBox.Ok)

           # print("哈哈哈哈")
        ##################################################################################
        #################################DB：清除本地数据库的信息############################
        ##################################################################################
        #                                                                                #
        #                                    要修改！！！！！！！！！！！！！                 #
        #                                                                                #
        ##################################################################################

    def newstuChoicall(self):
        ##################################################################################
        ##############################DB：全选按钮（新生注册界面）###########################
        ##
        #
        ##################################################################################
        self.ui.newstu_tableview.selectAll()
        print(self.ui.newstu_tableview.getKeys())

    def identChoicall(self):
        ##################################################################################
        ##############################DB：全选按钮（考试界面）###########################
        ##
        #
        ##################################################################################
        self.ui.tableView.selectAll()
        print(self.ui.tableView.getKeys())

    def upexamAll(self):
        ##################################################################################
        ##############################DB：全选按钮（考场下载界面）###########################
        ##
        #
        ##################################################################################
        self.ui.upexam_tableView.selectAll()


    #单击新生注册table表单，在photo_label上显示照片
    def new_showphoto(self):
        id = self.ui.newstu_tableview.getKeys()
        print("已选学生的ID：", id)
        last = len(id)
        if last>0 :
            pwd = os.getcwd()
            img_pwd = os.path.abspath(os.path.dirname(pwd) + os.path.sep + ".")
            img_pwd = img_pwd + '/files/registerStudent'
            print("最后选中的学生的ID：", id[last - 1])
            resume = str(id[last - 1]) + "_0" + '.jpg'
            for parent, dirnames, filenames in os.walk(img_pwd):
                for filename in filenames:
                    if filename == resume:
                        print("找到了这个学生的照片(｡･ω･｡)：", filename)
                        img_pwd1 = img_pwd + '/' + resume
                        self.ui.newstuPhotoimg_label.setPixmap(QPixmap(img_pwd1))

    #单击监考模式table表单,在photo_label上显示照片
    def ident_showphoto(self):
        id = self.ui.tableView.getKeys()
        pwd = os.getcwd()
        img_pwd = os.path.abspath(os.path.dirname(pwd) + os.path.sep + ".")

        if id!=():
            print("被选中的学生ID：" ,id)
            img_pwd = img_pwd + '/files/examStudent'
            last = len(id)
            resume = str(id[last-1][1])
            name=''
            for parent, dirnames, filenames in os.walk(img_pwd):
                for filename in filenames:
                    if filename.find(resume) != -1:
                       name = filename

            img_pwd1=img_pwd+'/'+name
            print("找到了被选中的学生的皂片(*^◯^*)：", id[last-1][1])
            self.ui.info_photo.setPixmap(QPixmap(img_pwd1))

    #临时退出程序，清除未重命名的数据
    def clearData(self):
        pwd = os.getcwd()
        img_pwd = os.path.abspath(os.path.dirname(pwd) + os.path.sep + ".")
        match_pwd = img_pwd + '/match_file'
        for parent, dirnames, filenames in os.walk(match_pwd):
            for filename in filenames:
                if filename.find("ident") != -1:
                    os.remove(os.path.join(parent, filename))

        reg_pwd = img_pwd + '/files/registerStudent'
        for parent, dirnames, filenames in os.walk(reg_pwd):
            for filename in filenames:
                if filename.find("stu") != -1 or filename.find("FP")!=-1:
                    os.remove(os.path.join(parent, filename))

    #root清除本机数据时，清空各类文件夹
    def clearAllfiles(self):
        pwd = os.getcwd()
        up_pwd = os.path.abspath(os.path.dirname(pwd) + os.path.sep + ".")
        aim_pwd = up_pwd+'/files/examRecord'
        list = os.listdir(aim_pwd)  # 列出目录下的所有文件和目录
        for line in list:
            filepath = os.path.join(aim_pwd, line)
            if os.path.isdir(filepath):  # 如果filepath是目录
                shutil.rmtree(filepath)
        print("已清除examRecord中的所有数据")

        aim_pwd = up_pwd + '/files/examStudent'
        for parent, dirnames, filenames in os.walk(aim_pwd):
            for filename in filenames:
                files = aim_pwd + '/' + filename
                os.remove(os.path.join(parent, filename))
        print("已清除examStudent中的所有数据")

        aim_pwd = up_pwd + '/files/registerStudent'
        for parent, dirnames, filenames in os.walk(aim_pwd):
            for filename in filenames:
                files = aim_pwd + '/' + filename
                os.remove(os.path.join(parent, filename))
        print("已清除registerStudent中的所有数据")

        aim_pwd = up_pwd + '/match_file'
        for parent, dirnames, filenames in os.walk(aim_pwd):
            for filename in filenames:
                files = aim_pwd + '/' + filename
                os.remove(os.path.join(parent, filename))
        print("已清除match_file中的所有数据")

    #恢复出厂值设置
    def resertAll(self):
        if QMessageBox.Yes == QMessageBox.question(self, "question", "确定恢复出厂值设置？", QMessageBox.No, QMessageBox.Yes):
            configDB.resetLocalDB()
            self.ui.newstu_tableview.filter('', '', '', 'All', 'All')
            self.ui.tableView.filter('', '', '', '', 'All', 'All', 'All', 'All', 'All')
            self.ui.spk_tableView.filter('')
            self.ui.upexam_tableView.filter('', '', '', '')
            self.ui.updata_tableView.filter()
            self.ui.newtea_tableView.filter(24)
            self.ui.newoff_tableView.filter(35)
            QMessageBox.information(self, "成功", "恢复出厂值", QMessageBox.Ok)
