# -*- coding: utf-8 -*-
#######################################
__file__ = "facerec_with_gui.py"
__author__ = "Sümeyye Türkmen"
__version__ = "1.0"
__email__ = "sumeyye3839@gmail.com"
#######################################



from tkinter import *
import PIL.Image
import PIL.ImageTk
import tkinter.filedialog
import face_recognition
import cv2
import os
import threading

frame = Tk()
frame.resizable(width=FALSE, height=FALSE)
frame.title("Yüz Tanıma GUI")
frame.geometry("1024x768")


global lblImage
video_capture = cv2.VideoCapture(0)
known_face_encodings = []
known_face_names = []
global camera_is_open
global btnOpenCamera


def trainFaces():
    print("---Eğitim Başladı---")
    for root, dirs, files in os.walk("./faces"):
        for filename in files:
            file_result = filename.split("_")
            known_face_names.append(file_result[0])
            image = face_recognition.load_image_file("faces/"+filename)
            image_face_encoding = face_recognition.face_encodings(image)[0]
            known_face_encodings.append(image_face_encoding)
            print("İsim: " + file_result[0])
    print("---Eğitim Tamamlandı---")


def faceRecognitionFromPicture(cvframe):
    print("---- Recognized Başladı ----")
    small_frame = cv2.resize(cvframe, (0, 0), fx=0.25, fy=0.25)

    # Görüntüyü BGR renginden RGB rengine dönüştürelim
    small_rgb_frame = small_frame[:, :, ::-1]

    # Yüzü bulun
    face_locations = face_recognition.face_locations(small_rgb_frame)
    print("Yüz taraması tamamlandı")

    face_encodings = face_recognition.face_encodings(
        small_rgb_frame, face_locations)

    face_names = []
    for face_encoding in face_encodings:
            # Eşleşip eşleşmediğini bulalım
        matches = face_recognition.compare_faces(
            known_face_encodings, face_encoding)
        name = "tanınmıyor"  # varsayılan ad tanınmıyor

        # known_face_encodings içinde bir eşleşme bulunursa, ilkini kullanın.
        if True in matches:
            first_match_index = matches.index(True)
            name = known_face_names[first_match_index]

        face_names.append(name)
    
        
    print("-Yüz lokasyonları")
    # yüz verilerini yazdır
    print(*face_locations, sep='\n')
    print(*face_names, sep='\n')
    print("Arama tamamlandı.")
    # geçerli çerçevede yüz dikdörtgenini ve adını çizin.
    drawFaceOnImage(cvframe, face_locations, face_names)

    faceNames = ''.join(face_names)
    count = str(len(face_locations))
    location = ','.join([str(i) for i in face_locations])
    return_string = "\nİsimler "+faceNames + \
        "\nYüz Sayısı: "+count+"\nLokasyonlar: "+location+"\n"
    lblTag["text"] = return_string
    print("---- Recognized Tamamlandı----")


def drawFaceOnImage(frame, face_locations, face_names):

    for (top, right, bottom, left), name in zip(face_locations, face_names):
        # Ölçeklendirme
        top *= 4
        right *= 4
        bottom *= 4
        left *= 4

        # Yüzün çevresine bir kutu çiz.
        cv2.rectangle(frame, (left, top), (right, bottom), (153, 0, 51), 4)

        # Yüzün altında adı olan bir etiket çizin.
        cv2.rectangle(frame, (left, top + 35),
                      (right, top), (153, 0, 51), cv2.FILLED)
        font = cv2.FONT_HERSHEY_DUPLEX
        cv2.putText(frame, name, (left + 10, top + 25),
                    font, 1.0, (255, 255, 255), 2)
    # temp görüntü dosyası yaz
    cv2.imwrite("temp.jpg", frame)


def openFile():
    camera_is_open = False
    filename = tkinter.filedialog.askopenfilename(
        initialdir="/", title="Choose Photo")
    # yüz tanıma
    cvframe = cv2.imread(filename)
    faceRecognitionFromPicture(cvframe)

    # tanınan resmi alın
    im = PIL.Image.open("temp.jpg")
    im = im.resize((700, 400))
    photo = PIL.ImageTk.PhotoImage(im)
    lblImage.configure(image=photo)
    lblImage.image = photo


def openCamera():
    global btnOpenCamera

    global camera_is_open
    if camera_is_open == False:
        camera_is_open = True
        btnOpenCamera["text"] = "Stop Camera"
        videoThread = threading.Thread(
            target=processCameraFrameForTkinter, args=())
        videoThread.start()
    else:
        camera_is_open = False
        btnOpenCamera["text"] = "Start Camera"


def processCameraFrameForTkinter():
    global camera_is_open
    while camera_is_open:
        ret, frame = video_capture.read()
        faceRecognitionFromPicture(frame)
        # tanınan resmi alın
        im = PIL.Image.open("temp.jpg")
        im = im.resize((960, 540))
        photo = PIL.ImageTk.PhotoImage(im)
        lblImage.configure(image=photo)
        lblImage.image = photo
        # veya cv2.imshow() kullanın


trainFaces()
# form bileşenleri
btnOpenFile = Button(text="Fotoğraflardan tanıma", command=openFile)
lblTag = Label(text="",
               bg="red", fg="white", font="Arial 18")
lblImage = Label()
btnOpenCamera = Button(text="Kameradan tanıma", command=openCamera)

btnOpenFile.pack()
btnOpenCamera.pack()
lblTag.pack()
lblImage.pack()
camera_is_open = False
mainloop()