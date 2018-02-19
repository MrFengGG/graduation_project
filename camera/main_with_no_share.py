import cv2
import time
import copy
import multiprocessing
from managers import CameraManager
from managers import CommandManager
from items import MessageItem
from transmitters import Dispatcher
from monitors import WatchDog,CamShiftTracker,DlibTracker
from threading import Thread
from settings import *
from utils import IOUtil,logger
from multiprocessing import Pool

def watch(watchDog,frame):
	if not watchDog.isWorking():
		watchDog.startWorking(frame)
	else:
		item = watchDog.update(frame)
	return item
def track(tracker,frame):
	if not tracker.isWorking():
		tracker.startWorking(frame)
	else:
		item = tracker.update(frame)
	return item
def dispense(item,dispatcher):
	dispatcher.dispenseImage(mydict['item'],(imageIp,imagePort))
def show(frame):
	if frame is None:
		return 3
	cv2.imshow("track",frame)
	k = cv2.waitKey(1) & 0xff
	if k == 27:
	    return 0
	return 1
def main():
	video = cv2.VideoCapture(0)
	cameraManager = CameraManager(video)
	cameraManager.start()
	pool = Pool(2)
	while True:
		a = pool.apply_async(show,args=(cameraManager.getFrame(),))
		print(a.get())
		if a.get() == 0:
			break

if __name__ == "__main__":
	main()