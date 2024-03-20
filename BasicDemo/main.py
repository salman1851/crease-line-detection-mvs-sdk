# -- coding: utf-8 --
import sys
from tkinter import * 
from tkinter.messagebox import *
import _tkinter
import tkinter.messagebox
import tkinter as tk
import os
from tkinter import ttk
from CamOperation_class import *
from PIL import Image,ImageTk
import numpy
from tkinter import ttk
import pyscreenshot
from datetime import datetime
import datetime as dt
import csv
import math
import numpy
import cv2

sys.path.append(r"C:\Users\EE\Downloads\tetrapak_crease_line_marking_v2.zip-20240320T065015Z-001\MvImport")    # absolute path of the MvImport package
from MvCameraControl_class import *

if os.path.exists("image.jpg"):
  os.remove("image.jpg")

# Get the index of the selected device information and parse it through the characters between []
def TxtWrapBy(start_str, end, all):
    start = all.find(start_str)
    if start >= 0:
        start += len(start_str)
        end = all.find(end, start)
        if end >= 0:
            return all[start:end].strip()

# Convert the returned error code to hexadecimal display
def ToHexStr(num):
    chaDic = {10: 'a', 11: 'b', 12: 'c', 13: 'd', 14: 'e', 15: 'f'}
    hexStr = ""
    if num < 0:
        num = num + 2**32
    while num >= 16:
        digit = num % 16
        hexStr = chaDic.get(digit, str(digit)) + hexStr
        num //= 16
    hexStr = chaDic.get(num, str(num)) + hexStr   
    return hexStr

if __name__ == "__main__":
    global deviceList 
    deviceList = MV_CC_DEVICE_INFO_LIST()
    global tlayerType
    tlayerType = MV_GIGE_DEVICE | MV_USB_DEVICE
    global cam
    cam = MvCamera()
    global nSelCamIndex
    nSelCamIndex = 0
    global obj_cam_operation
    obj_cam_operation = 0
    global b_is_run
    b_is_run = False

    global rotation_angle
    rotation_angle = 0

    global frozen_image
    frozen_image = None

    global active_line 
    active_line = 1

    global line1
    line1 = None

    global line2
    line2 = None

    global line3
    line3 = None

    global line4
    line4 = None

    global line_colors
    line_colors = ['yellow', 'red', 'green', 'blue']

    global line_coor
    line_coor = [0,0,0,0]

    global point_ser_num
    point_ser_num = 1

    global auto_rotate_toggle
    auto_rotate_toggle = 0

    # Interface design code
    window = tk.Tk()
    window.title('BasicDemo')
    window.geometry('1150x650')
    model_val = tk.StringVar()
    # global triggercheck_val
    triggercheck_val = tk.IntVar()
    page = Frame(window,height=400,width=60,relief=GROOVE,bd=5,borderwidth=4)
    page.pack(expand=True, fill=BOTH)
    panel = Canvas(window, width=800, height=600, bd=0, highlightthickness=0)
    panel.place(x=300, y=20, anchor=tk.NW)
    # panel = Label(page)
    # panel.place(x=190, y=10,height=600,width=1000)

    # Bind drop-down list to device information index
    def xFunc(event):
        global nSelCamIndex
        nSelCamIndex = TxtWrapBy("[","]",device_list.get())

    # enum devices
    def enum_devices():
        global deviceList
        global obj_cam_operation
        deviceList = MV_CC_DEVICE_INFO_LIST()
        tlayerType = MV_GIGE_DEVICE | MV_USB_DEVICE
        ret = MvCamera.MV_CC_EnumDevices(tlayerType, deviceList)
        if ret != 0:
            tkinter.messagebox.showerror('show error','enum devices fail! ret = '+ ToHexStr(ret))

        if deviceList.nDeviceNum == 0:
            tkinter.messagebox.showinfo('show info','find no device!')

        print ("Find %d devices!" % deviceList.nDeviceNum)

        devList = []
        for i in range(0, deviceList.nDeviceNum):
            mvcc_dev_info = cast(deviceList.pDeviceInfo[i], POINTER(MV_CC_DEVICE_INFO)).contents
            if mvcc_dev_info.nTLayerType == MV_GIGE_DEVICE:
                print ("\ngige device: [%d]" % i)
                chUserDefinedName = ""
                for per in mvcc_dev_info.SpecialInfo.stGigEInfo.chUserDefinedName:
                    if 0 == per:
                        break
                    chUserDefinedName = chUserDefinedName + chr(per)
                print ("device model name: %s" % chUserDefinedName)

                nip1 = ((mvcc_dev_info.SpecialInfo.stGigEInfo.nCurrentIp & 0xff000000) >> 24)
                nip2 = ((mvcc_dev_info.SpecialInfo.stGigEInfo.nCurrentIp & 0x00ff0000) >> 16)
                nip3 = ((mvcc_dev_info.SpecialInfo.stGigEInfo.nCurrentIp & 0x0000ff00) >> 8)
                nip4 = (mvcc_dev_info.SpecialInfo.stGigEInfo.nCurrentIp & 0x000000ff)
                print ("current ip: %d.%d.%d.%d\n" % (nip1, nip2, nip3, nip4))
                devList.append("["+str(i)+"]GigE: "+ chUserDefinedName +"("+ str(nip1)+"."+str(nip2)+"."+str(nip3)+"."+str(nip4) +")")
            elif mvcc_dev_info.nTLayerType == MV_USB_DEVICE:
                print ("\nu3v device: [%d]" % i)
                chUserDefinedName = ""
                for per in mvcc_dev_info.SpecialInfo.stUsb3VInfo.chUserDefinedName:
                    if per == 0:
                        break
                    chUserDefinedName = chUserDefinedName + chr(per)
                print ("device model name: %s" % chUserDefinedName)

                strSerialNumber = ""
                for per in mvcc_dev_info.SpecialInfo.stUsb3VInfo.chSerialNumber:
                    if per == 0:
                        break
                    strSerialNumber = strSerialNumber + chr(per)
                print ("user serial number: %s" % strSerialNumber)
                devList.append("["+str(i)+"]USB: "+ chUserDefinedName +"(" + str(strSerialNumber) + ")")
        device_list["value"] = devList
        device_list.current(0)

        open_device()
    
        # open device
    def open_device():
        global deviceList
        global nSelCamIndex
        global obj_cam_operation
        global b_is_run
        # if True == b_is_run:
        if b_is_run == True:
            tkinter.messagebox.showinfo('show info','Camera is Running!')
            return
        obj_cam_operation = CameraOperation(cam,deviceList,nSelCamIndex)
        ret = obj_cam_operation.Open_device()
        if  0!= ret:
            b_is_run = False
        else:
            model_val.set('continuous')
            b_is_run = True

    # Start grab image
    def start_grabbing():
        global obj_cam_operation
        obj_cam_operation.Start_grabbing(window,panel)
        # freeze_toggle == False

    # Stop grab image
    def stop_grabbing():
        global obj_cam_operation
        obj_cam_operation.Stop_grabbing()    

    # Close device   
    def close_device():
        global b_is_run
        global obj_cam_operation
        obj_cam_operation.Close_device()
        b_is_run = False 

    def jpg_save():
        global obj_cam_operation
        obj_cam_operation.b_save_jpg = True
        obj_cam_operation.Start_grabbing(window,panel)

    def show_frozen_image():
        obj_cam_operation.Stop_grabbing()
        frame = cv2.imread('image.jpg')
        global frozen_image
        frozen_image = frame
        frame = cv2.resize(frame, (800, 600))
        img = Image.fromarray(frame)
        imgtk = ImageTk.PhotoImage(image=img)

        panel.delete("all")
        panel.create_image(0, 0, anchor=tk.NW, image=imgtk)  # Set anchor to the top-left corner
        panel.img = imgtk

        print('active line ', active_line)

    def create_empty_table():

        fields = ['Point', 'X1', 'X2', 'Diff']

        global tree

        tree = ttk.Treeview(window, columns=(0, 1, 2, 3), show="headings", height=4)
        tree.place(x=20, y=440)

        for col in range(0, 4):
            tree.heading(col, text=fields[col])
            tree.column(col, width=64) 

    def update_rotation_angle(value):
        global rotation_angle
        rotation_angle = int(value)

    def rotate_image():
        img = cv2.imread('image.jpg')
        if img is not None:
            angle = rotation_angle
            frame = img
            rows, cols, _ = frame.shape
            rotation_matrix = cv2.getRotationMatrix2D((cols / 2, rows / 2), angle, 1)
            rotated_image = cv2.warpAffine(frame, rotation_matrix, (cols, rows))

            frame = cv2.resize(rotated_image, (800, 600))
            img = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=img)

            panel.delete("all")
            panel.create_image(0, 0, anchor=tk.NW, image=imgtk)  # Set anchor to the top-left corner
            panel.img = imgtk

    def set_active_line1():
        global active_line 
        active_line = 1

    def set_active_line2():
        global active_line
        active_line = 2

    def set_active_line3():
        global active_line
        active_line = 3

    def set_active_line4():
        global active_line
        active_line = 4

    def move_line(event):
        if active_line == 1:
            global line1
            line1 = draw_or_move_line(line1, event.x)
        elif active_line == 2:
            global line2
            line2 = draw_or_move_line(line2, event.x)
        elif active_line == 3:
            global line3
            line3 = draw_or_move_line(line3, event.x)
        elif active_line == 4:
            global line4
            line4 = draw_or_move_line(line4, event.x)

    def draw_or_move_line(line, x_coord):
        if line is not None:
            panel.delete(line)  # Delete the existing line
        line = panel.create_line(x_coord, 0, x_coord, 600, fill= line_colors[active_line-1], width=2)
        line_coor[active_line - 1] = x_coord
        return line

    def process_image():
        global tree
        global point_ser_num
        if len(tree.get_children()) < 4:
            x1 = line_coor[1] - line_coor[0]
            x2 = line_coor[3] - line_coor[2]
            diff = x1 - x2
            tree.insert("", "end", values=(str(point_ser_num), str(x1), str(x2), str(diff)))
            point_ser_num += 1

    def delete_last_row():
        global tree
        global point_ser_num
        if len(tree.get_children()) > 0:
            last_item = tree.get_children()[-1]
            tree.delete(last_item)
            point_ser_num = point_ser_num - 1
        else:
            print("No rows to delete")

    def next_point():
        global tree
        if len(tree.get_children()) < 4:
            if os.path.exists("image.jpg"):
                os.remove("image.jpg")
        start_grabbing()
        auto_rotate_toggle = 1

    def take_ss(path):
       ss=pyscreenshot.grab()
       ss.save(path + "/screenshot.png")

    def save_csv(path):
        global tree
        with open(path + "/point.csv", "w", newline='') as myfile:
            csvwriter = csv.writer(myfile, delimiter=',')
            for row_id in tree.get_children():
                row = tree.item(row_id)['values']
                csvwriter.writerow(row)

    def save_all_points():
        if os.path.exists("image.jpg"):
            os.remove("image.jpg")
        date_time = datetime.now()
        dt_format = '%Y-%m-%d-%H-%M-%S'
        date_string = date_time.strftime(dt_format)
        os.makedirs(date_string)
        take_ss(date_string)
        save_csv(date_string)

        reset_all()

        auto_rotate_toggle = 0

    def reset_all():
        create_empty_table()
        start_grabbing()

    def auto_rotate_image(image, angle):
        height, width = image.shape[:2]
        rotation_matrix = cv2.getRotationMatrix2D((width / 2, height / 2), angle, 1)
        rotated_image = cv2.warpAffine(image, rotation_matrix, (width, height))
        return rotated_image

    def line_angle(img):
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        edges = cv2.Canny(blurred, 50, 150)
        lines = cv2.HoughLines(edges, 1, np.pi/180, threshold=300)
        if isinstance(lines, np.ndarray):
            total_angle = 0
            for line in lines:
                rho, theta = line[0]
                total_angle += np.degrees(theta)
            average_angle = total_angle / len(lines)
            return average_angle
        else:
            return 0

    def auto_rotate():
        global auto_rotate_toggle
        if auto_rotate_toggle == 0:
            img = cv2.imread('image.jpg')
            rot_angle = line_angle(img)
            rotated_image = auto_rotate_image(img, rot_angle)
            cv2.imwrite('image.jpg', rotated_image)

            frame = cv2.resize(rotated_image, (800, 600))
            img = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=img)
            panel.delete("all")
            panel.create_image(0, 0, anchor=tk.NW, image=imgtk)  # Set anchor to the top-left corner
            panel.img = imgtk
            
            print('Image auto-rotated!')
            auto_rotate_toggle = 1
        
    date = dt.datetime.now()
    date_label = tk.Label(window, text=f"{date:%A, %B %d, %Y}", font="Helvetica 15 bold")
    date_label.place(relx = 0.02, rely = 0.04, anchor ='nw')

    xVariable = tkinter.StringVar()
    device_list = ttk.Combobox(window, textvariable=xVariable,width=39)
    device_list.place(relx=0.015, rely=0.1, anchor ='nw')
    device_list.bind("<<ComboboxSelected>>", xFunc)

    btn_enum_devices = tk.Button(window, text='Enum Devices', width=35, height=1, command = enum_devices)
    btn_enum_devices.place(relx=0.015, rely=0.15, anchor ='nw')
    # btn_open_device = tk.Button(window, text='Open Device', width=15, height=1, command = open_device)
    # btn_open_device.place(relx=0.015, rely=0.2, anchor ='nw')
    # btn_close_device = tk.Button(window, text='Close Device', width=15, height=1, command = close_device)
    # btn_close_device.place(relx=0.14, rely=0.2, anchor ='nw')

    model_val.set(1)

    btn_start_grabbing = tk.Button(window, text='Start Grabbing', width=15, height=1, command = start_grabbing)
    btn_start_grabbing.place(x=20, y=140)
    btn_start_grabbing = tk.Button(window, text='Stop Grabbing', width=15, height=1, command = stop_grabbing)
    btn_start_grabbing.place(x=160, y=140)    
    
    btn_save_jpg = tk.Button(window, text='Save Image', width=15, height=1, command = jpg_save)
    btn_save_jpg.place(x=20, y=180)
    btn_show_jpg = tk.Button(window, text='Show Image', width=15, height=1, command = show_frozen_image)
    btn_show_jpg.place(x=160, y=180)

    rotation_slider = tk.Scale(window, from_=0, to=360, orient=tk.HORIZONTAL, length=250,
                                                         label="Set Anti-clockwise Rotation Angle", command = update_rotation_angle)
    rotation_slider.set(0)
    rotation_slider.place(x=20, y=220)

    button_rot_img = tk.Button(window, text="Rotate Image", width=15, height=1, command = rotate_image)
    button_rot_img.place(x=20, y=310)

    L1 = tk.Button(window, text="L1", width=5, height=1, bg="yellow", fg="black", command = set_active_line1)
    L1.place(x=20, y=360)

    L2 = tk.Button(window, text="L2", width=5, height=1, bg="red", fg="white", command = set_active_line2)
    L2.place(x=90, y=360)

    L3 = tk.Button(window, text="L3", width=5, height=1, bg="green", fg="white", command = set_active_line3)
    L3.place(x=160, y=360)

    L4 = tk.Button(window, text="L4", width=5, height=1, bg="blue", fg="white", command = set_active_line4)
    L4.place(x=230, y=360)

    button_proc_img = tk.Button(window, text="Auto-rotate Image", width=15, height=1, command = auto_rotate)
    button_proc_img.place(x=160, y=310)

    button_proc_img = tk.Button(window, text="Process Image", width=35, height=1, command = process_image)
    button_proc_img.place(x=20, y=400)

    create_empty_table()

    btn_del_last = tk.Button(window, text='Delete Last Point', width=15, height=1, command = delete_last_row)
    btn_del_last.place(x=20, y=560)

    btn_next_pt = tk.Button(window, text='Next Point', width=15, height=1, command = next_point)
    btn_next_pt.place(x=160, y=560)

    btn_reset_pts = tk.Button(window, text='Reset All Points', width=15, height=1, command = reset_all)
    btn_reset_pts.place(x=20, y=600)

    btn_save_all_pts = tk.Button(window, text='Save All Points', width=15, height=1, command = save_all_points)
    btn_save_all_pts.place(x=160, y=600)

    panel.bind("<Button-1>", move_line)

    window.mainloop()