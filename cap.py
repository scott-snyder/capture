#!/usr/bin/env python

import cv2
import sys
import os
import numpy as np
import time

camera_number = 2
disp_geom = (640, 480)
raw_dir = 'raw'
tailored_dir = 'tailored'


def open_camera (geom):
    cap = cv2.VideoCapture(camera_number, cv2.CAP_V4L2)
    if not cap.isOpened():
        print ('Could not open video')
        sys.exit(1)
    #FIXME:
    #cam_w = cap.get (cv2.CAP_PROP_FRAME_WIDTH)
    #cam_h = cap.get (cv2.CAP_PROP_FRAME_HEIGHT)
    cam_w = 3264
    cam_h = 2448
    set_res (cap, geom)
    return cap, (cam_w, cam_h)


def set_res (cap, geom):
    cap.set (cv2.CAP_PROP_FRAME_WIDTH, int(geom[0]))
    cap.set (cv2.CAP_PROP_FRAME_HEIGHT, int(geom[1]))
    return


def disp_page (pageno):
    print ('PAGENO', pageno)
    cv2.setWindowTitle ('left', f'Page {pageno:04}')
    cv2.setWindowTitle ('right', f'Page {pageno+1:04}')
    if os.path.exists (f'{tailored_dir}/page{pageno:04}.png'):
        cv2.imshow ('left', cv2.imread (f'{tailored_dir}/page{pageno:04}.png'))
    else:
        cv2.imshow ('left', np.zeros((2,3,4)))
    if os.path.exists (f'{tailored_dir}/page{pageno+1:04}.png'):
        cv2.imshow ('right', cv2.imread (f'{tailored_dir}/page{pageno+1:04}.png'))
    else:
        cv2.imshow ('right', np.zeros((2,3,4)))
    return


def capture (cap, cam_geom, pageno):
    set_res (cap, cam_geom)
    print (f'capture {pageno}... ', flush=True, end='')
    t0 = time.time()
    for i in range(10):
        ret, frame = cap.read()
        if ret: break
    t_read = time.time() - t0
    gray = cv2.cvtColor (frame, cv2.COLOR_BGR2GRAY)
    t3 = time.time()
    if not os.path.exists (raw_dir):
        os.mkdir (raw_dir)
    if not os.path.exists (tailored_dir):
        os.mkdir (tailored_dir)
    fname = f'{raw_dir}/img{pageno:04}.png'
    cv2.imwrite (fname, gray)
    t0 = time.time()
    os.system (f'scantailor-cli --layout=2 --dewarping=auto -o={tailored_dir}/img{pageno:04}.ScanTailor {fname} {tailored_dir}')
    t1 = time.time()
    os.system (f'magick {tailored_dir}/img{pageno:04}_1L.tif -pointsize 40 -gravity northwest -annotate 0 {pageno:04} {tailored_dir}/page{pageno:04}.png')
    os.system (f'magick {tailored_dir}/img{pageno:04}_2R.tif -pointsize 40 -gravity northeast -annotate 0 {pageno+1:04} {tailored_dir}/page{pageno+1:04}.png')
    t2 = time.time()
    os.unlink (f'{tailored_dir}/img{pageno:04}_1L.tif')
    os.unlink (f'{tailored_dir}/img{pageno:04}_2R.tif')
    print (f'done; read {t_read:.2} tailor {t1-t0:.2} annotate {t2-t1:.2}')
    disp_page (pageno)
    return


def next_pageno (pageno):
    while os.path.exists (f'{raw_dir}/img{pageno:04}.png'):
        pageno += 2
    return pageno
    

#3264x2448
cv2.setLogLevel(3)
cap, cam_geom = open_camera (disp_geom)

print (f'Frame geometry {cam_geom[0]}x{cam_geom[1]}')

cv2.namedWindow ('left', 0)
cv2.resizeWindow ('left', 364, 600)
cv2.moveWindow ('left', 0, 100)
cv2.namedWindow ('right', 0)
cv2.resizeWindow ('right', 375, 600)
cv2.moveWindow ('right', 375, 100)
cv2.namedWindow ('preview', 0)
cv2.resizeWindow ('preview', 640, 480)
cv2.moveWindow ('preview', 750, 100)
pageno = 2
disp_page (pageno)
while True:
    ret, frame = cap.read()
    if not ret:
        print ('bad read')
        cap.release()
        cap, cam_geom = open_camera (disp_geom)
        continue
    cv2.imshow ('preview', frame)
    k = cv2.waitKey(25)
    if k == ord('q'):
        break
    elif k == ord('r'):
        capture (cap, cam_geom, pageno)
        set_res (cap, disp_geom)
    elif k == ord('s'):
        pageno = next_pageno (pageno)
        capture (cap, cam_geom, pageno)
        set_res (cap, disp_geom)
    elif k == 83: # right
        pageno += 2
        disp_page (pageno)
    elif k == 81: # left
        if pageno > 2:
            pageno -= 2
            disp_page (pageno)
    elif k == 84: # down
        pageno += 10
        disp_page (pageno)
    elif k == 82: # up
        if pageno > 10:
            pageno -= 10
            disp_page (pageno)
    elif k == 86: # page down
        pageno += 50
        disp_page (pageno)
    elif k == 85: # page up
        if pageno > 50:
            pageno -= 50
            disp_page (pageno)
        
