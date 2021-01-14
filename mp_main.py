import multiprocessing as mp
from ImageComp_GUI import Bild,Root
from time import sleep
import os
from ttkthemes import ThemedTk #bugfix pyinstaller?
from send2trash import send2trash

def guifunc(q1,q2):
    gui=Root(q1,q2)
    print("this is GUI Process, GUI started")
    gui.mainloop()
    return 0

def imgworkerfunc(q1,q2):
    while(1):
        img=None
        if not q1.empty():
            try:
                img=q1.get(1)
            except:
                pass
        else:
            sleep(0.1)
        if type(img)!=type(None):
            #print("Imageworker: processing",img)
            img.processImg()
            q2.put(img)

if __name__ == "__main__":
    mp.freeze_support()
    print("Startmethod:",mp.get_start_method())
    q1=mp.Queue()
    q2=mp.Queue()
    p = mp.Process(target=guifunc, args=(q1,q2))
    p.start()
    print("This ist the MAIN Process, gui started")
    imgworkerprocesses=[]
    for id in range(os.cpu_count()):
        wp=mp.Process(target=imgworkerfunc, args=(q1,q2))
        wp.start()
        imgworkerprocesses.append(wp)
    print("This is the MAIN Process, imgworkers started")
    p.join()
    for wp in imgworkerprocesses:
        wp.terminate()
        wp.join()
    print("Programm End")