This code is an SDK version of this application: https://github.com/salman1851/crease-line-detection.

It was designed to interface with Machine Vision SDK (MVS) hardware, such as the HikRobot area scan camera.

![crease_line_hikrobot_demo](https://github.com/salman1851/crease-line-detection-mvs-sdk/assets/131760691/8eb2d7cd-3086-4ee4-b85c-2df87ea4d743)

You need to include the absolute path of MvImport into the main script as well as the CamOperation class definition script.

When you click on Enum Devices, an MVS SDK camera would show up in the drop-down menu if it is connected to your computer.

You can start and stop the camera stream using the 'Start Grabbing' and 'Stop Grabbing' buttons. 

Before rotating the image, you must click on 'Show Image' button to display the frozen image. The auto-rotate function uses classical image processing techniques to align any detected segments with the vertical axis.

Once the image has been rotated, you can use the colored buttons to draw four lines on the image. The lines can be horizontally adjusted by clicking anywhere on the canvas.

When you click 'Process Image', the pixel distance between the first two lines and the last two lines is added to the error records.

The table is stored (along with the screen-shot of the GUI at that point) in a new folder when you click the 'Save All Points' button.
