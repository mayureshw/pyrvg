# pyrvg

This software is a work in progress to attempt to use a dental intraoral camera Carestream 5200 on Linux.

Disclaimer: This software is not based on any official driver. Please use at your own risk. The authors of this software won't be responsible if it causes any damage to your device or voids your warranty. Further, the authors take no responsibility for accuracy or lack of it of any of the outputs produced by this software and their suitability for any purpose whatsoever.

# Hardware and Software Requirements

- Carestream RVG 5200 USB camera (vendorid: 0x082b, productid: 0x000c)
- python3
- pypng

# Usage

Connect the Carestream RVG 5200 USB device to USB port
Run the program rvg5200.py and wait till it says 'Ready to shoot', then shoot the X ray. If it works (see open issues) it should produce an image file with name rvg.png

# Open issues:

- It is not known whether the device initialization sequences are generic or specific to a licensee. It requires at least one more individual owning another instance of the same device to try it out and provide feedback.

- The calibration settings (adjustments of brightness, contrast, gamma, exposure etc. applied inherently on the raw image before producing it as the output) need to be figured out and applied implicitly.

- Would like to add DICOM form image generation. Currently only png form image is produced.

# For advanced users only : if you have exactly the same device but it does not work

- These instructions assume you have a working carestream software installed on a windows virtual machine running on Linux. It is possible to produce the desired files (essentially files dev1init and dev2init produced at the end of these instructions) directly on a Windows computer, but the instructions would vary slightly. If you are able to produce these files on Windows, please consider contributing the instructions to this package.
- Familiarize yourself a bit with usbmon if you are already not. Get this usbmon pacakage (as the stock usbmon has a data truncation issue): https://github.com/swetland/usbmon. Build this package, which typically involves merely running make.
- Do 'modprobe usbmon' to enable usb monitoring
- Begin this exercise as a clean slate, that is when since last reboot the device has not yet been connected to the computer and carestream application has not been run.
- Run usbmon from above package without any CLI options for bus or device filter (we'll do the filtering by device later) and then insert the device cable.
- Note down the bus and device number of the device (lsusb should help) which we will need later
- Run the carestream application up to it being ready to acquire an RVG (but do not actually acquire).
- Use lsusb again. You should notice that the device 0x082b:0x000c has disappeared and a new device 0x082b:0x100a has appeared. Note down the latter's bus and device id which we will need later.
- Quit the application and kill the usbmon program, usually done by Ctrl-C in the terminal where you ran it
- Use the script supplied with this package usbmonfilt.sh (see its usage message). Filter out the first device's usbmon trace into a file 'dev1init' and the second device's trace into 'dev2init' overwriting the stock files with same names supplied with this package.
- Try the usage instructions now.
