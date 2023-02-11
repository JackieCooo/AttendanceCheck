# AttendanceCheck —— 人脸考勤系统

![](Others/img/home.png)

## 简介 Brief
这是一个大三的数字图像处理课程设计。  
功能如其名，它是一个用来考勤打卡的桌面小软件。有人脸注册和人脸打卡两个功能，简单易用。  

This is my junior digital image processing course design at university.  
It functions as the name suggests, it is a small desktop software used to clock in and out. It has two functions, face registration and face clocking, and is easy to use.  

## 编译环境 Compiler Environment
这个项目用到了比较新的环境。  
IDE使用JetBrains公司的**PyCharm**  
编程语言使用**Python 3.10.x**，GUI使用了Qt公司的**PySide6**，人脸识别使用了第三方库**dlib**和**OpenCV**  
> dlib的安装比较复杂，需要电脑中安装了Visual Studio才能够安装成功，网上也有对应的教程  

This project uses a relatively new environment.  
The IDE is **PyCharm** from JetBrains.  
The programming language is **Python 3.10.x**, the GUI is **PySide6** from Qt, and the face recognition uses third-party libraries **dlib** and **OpenCV**.  
> The installation of dlib is complicated and requires Visual Studio to be installed on the computer.  

## 软件打包 Software Packaging
Python环境下对软件打包需要安装**pyinstall**库。  
在项目根目录下打开命令行，输入以下命令即可：  
``` shell
pyinstaller -D -w main.py
```

To package software in Python, you need to install the **pyinstall** library.  
Open a command line in the project root directory and enter the following command.  
``` shell
pyinstaller -D -w main.py
```

## 如何使用 How to Use
软件启动后点击最下面“Open Camera”按钮打开摄像头（请确保自己的电脑有接入摄像头或自带摄像头）。  
摄像头打开后选择模式，“Register”按钮为人脸注册模式，“Check”按钮为人脸考勤模式。  

Once the software has started, click on the "Open Camera" button at the bottom to open the camera (make sure your computer has access to a camera or comes with one).  
Once the camera is open, select the mode, the "Register" button is for face registration mode and the "Check" button is for face attendance mode.  

### 人脸注册模式 Face registration mode
![](Others/img/facial_register.png)  
这个模式下摄像头图像周围会有一个框，注册人脸时，必须要使人脸完全在这个框内才会识别成功。  
识别成功后会要求用户输入姓名，点击“OK”按钮后人脸即注册成功。  

In this mode, there will be a box around the camera image. When registering a face, the face must be completely inside this box before the recognition will be successful.  
After a successful recognition, the user will be asked to enter his/her name, and the face will be successfully registered when the "OK" button is clicked.  

### 人脸考勤模式 Face attendance mode
![](Others/img/facial_check.png)  
在这个模式下，用户将脸对准摄像头，系统成功识别人脸后会在软件上方显示用户的ID和姓名，表示考勤成功。  

In this mode, the user will point his/her face at the camera and the system will display the user's ID and name at the top of the software after the face is successfully recognised, indicating successful attendance.  
