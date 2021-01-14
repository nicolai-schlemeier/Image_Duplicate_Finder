from tkinter import *
from tkinter import ttk, filedialog
import tkinter as tk
from tkinter import messagebox
from ttkthemes import ThemedTk
from PIL import ImageTk, Image
import numpy as np
import cv2 as cv
#from matplotlib import pyplot as plt 
#from matplotlib.figure import Figure 
#from matplotlib.backends.backend_tkagg import * 
import os
#from copy import deepcopy
import math
from time import sleep
from send2trash import send2trash
import multiprocessing as mp


#Known Bugs:
#Due to internal conversion to RGB png files are not transparent displayed in the preview, but no worries: the original files remain unchanged.


class Bild:
    def __init__(self,path,fname, size,prevheight=200,fineness=30,*args, **kwargs):
        self.status=0
        self.path=path
        self.filename=fname
        self.resolution=0
        self.size=size
        self.colorval=0
        self.keymat=0
        self.preview=0
        self.previewheight=prevheight
        self.fineness=fineness
    def __repr__(self):
        return "Bild:"+self.filename
    def processImg(self):
        img=cv.imread(self.path) #add ,0 to load image in grayscale
        if type(img)!=type(None):
            self.resolution=img.shape
            self.compute_vector(img,self.fineness)
            self.getcolorval(img)
            img2=Image.fromarray(cv.cvtColor(img,cv.COLOR_BGR2RGB))
            self.preview=img2.resize( (int(round(img2.width* self.previewheight/img2.height)),int(self.previewheight)) )# resizing after computation to save memory
            self.status="processed"
        else:
            self.status="Error in cv.imread()"
    def compute_vector(self,img,fineness):
        #cv.imshow('image',img)
        self.orb = cv.ORB_create()
        kp = self.orb.detect(img,None)
        kp, des = self.orb.compute(img, kp)
        koordinates=[k.pt for k in kp]
        dim=img.shape
        self.keymat=np.full((int(fineness),int(fineness)),0, dtype=bool)
        for k in koordinates:
            if k[0].is_integer() and k[1].is_integer():
                rel_x=k[0]/dim[1]
                rel_y=k[1]/dim[0]
                self.keymat[int(math.trunc(rel_x*fineness))][int(math.trunc(rel_y*fineness))]=1
        self.orb=0 #delete orb, reicht ORB_create() für alle Bilder?
        
    def getcolorval(self,img):
        shape=img.shape
        imgpart=img[:math.trunc(shape[0]*0.1),:math.trunc(shape[1]*0.1)]
        r=np.mean(imgpart[:,:,0])
        g=np.mean(imgpart[:,:,1])
        b=np.mean(imgpart[:,:,2])
        self.colorval=[r,g,b]





class Root(ThemedTk):
    def __init__(self,q1=mp.Queue(),q2=mp.Queue(),**kwargs):
        super(Root, self).__init__(theme="breeze")
        self.init_vars()
        self.q1=q1 
        self.q2=q2
        self.title("ImageComparing")
        self.minsize(640, 400)
        self.iconbitmap("computer.ico")
        self.labelFrame = ttk.LabelFrame(self, text = "Select Directory")
        self.label = ttk.Label(self.labelFrame, text = "No path selected, click Browse")
        self.label.grid(column = 1, row = 1, padx=20 , pady=5)
        self.labelFrame.grid(column = 0, row = 1, padx = 20, pady = 10, sticky="N")

        self.button = ttk.Button(self.labelFrame, text = "Browse Directories",command = self.fileDialog)
        self.button.grid(column = 1, row = 0, padx=20, pady=5)
        
        self.options = ttk.LabelFrame(self, text = "Options")
        self.options.grid(column = 1, row = 0, padx = 20, pady = 10, sticky="N",columnspan=2,rowspan=2)
        self.checkButtons()
        w_s=8
        self.fineness_label=ttk.Label(self.options, text="Fineness")
        self.fineness_label.grid(row=0, column=2, padx=10,pady=5)
        self.fineness_var=tk.IntVar()
        self.fineness_var.set(30)
        self.fineness_var_min=10
        self.fineness_var_max=100
        self.fineness_scale = ttk.Spinbox(self.options,from_=self.fineness_var_min, to=self.fineness_var_max, textvariable=self.fineness_var, width=w_s)#, length=160)
        self.fineness_scale.grid(row=1,column=2,columnspan=1, padx = 10, pady = 5)

        self.min_id_label=ttk.Label(self.options, text="Min. Identical")
        self.min_id_label.grid(row=0, column=3, padx=10,pady=5)
        self.min_id_var=tk.IntVar()
        self.min_id_var.set(50)
        self.min_id_var_min=10
        self.min_id_var_max=100
        self.min_id_scale = ttk.Spinbox(self.options,from_=self.min_id_var_min, to=self.min_id_var_max,textvariable=self.min_id_var,width=w_s)#, length=160)
        self.min_id_scale.grid(row=1,column=3,columnspan=1, padx = 10, pady = 5)


        self.prev_h_label=ttk.Label(self.options, text="Preview Height")
        self.prev_h_label.grid(row=0, column=4, padx=10,pady=5)
        self.prev_h_var=tk.IntVar()
        self.prev_h_var.set(200)
        self.prev_h_var_min=50
        self.prev_h_var_max=300
        self.prev_h_scale = ttk.Spinbox(self.options,from_=self.prev_h_var_min, to=self.prev_h_var_max, textvariable=self.prev_h_var,width=w_s)#, length=100)
        self.prev_h_scale.grid(row=1,column=4,columnspan=1, padx = 10, pady = 5)

        self.entry_label=ttk.Label(self.options, text="Allowed Datatypes")
        self.entry_label.grid(row=0, column=5, padx=20,pady=5)
        self.entry_var=tk.StringVar()
        self.entry_var.set("png,jpg,jpeg")
        self.entry=ttk.Entry(self.options, textvariable=self.entry_var,width=15)
        self.entry.grid(row=1, column=5, padx=20, pady=2)
        self.entry_desc=ttk.Label(self.options,text="no dots seperate by ',' ")
        self.entry_desc.grid(row=3, column=5,pady=1)
        
        #IMAGES#
        w=300
        h=300
        self.canvas_l= Canvas(self, width = w, height = h)
        self.pos_l=(3,1)
        self.def_txt_l=self.canvas_l.create_text(w/2,20,text="Default Image")
        self.def_res_l=self.canvas_l.create_text(w/2,40,text="Resolution")
        self.def_del_l=self.canvas_l.create_text(w/2,h/2,text="",font=("Arial",20),fill="red",angle=45)
        self.img_l = ImageTk.PhotoImage(Image.open("blank.png"))      
        self.default_img_l=self.canvas_l.create_image(w/2,60, anchor=N, image=self.img_l)    
        self.canvas_l.image = self.img_l  
        self.canvas_l.grid(row=self.pos_l[0], column=self.pos_l[1])

        self.canvas_r = Canvas(self, width = w, height = h) 
        self.pos_r=(3,2)
        self.def_txt_r=self.canvas_r.create_text(w/2,20,text="Default Image")
        self.def_res_r=self.canvas_r.create_text(w/2,40,text="Resolution")
        self.def_del_r=self.canvas_r.create_text(w/2,h/2,text="",font=("Arial",20),fill="red",angle=45)
        self.img_r = ImageTk.PhotoImage(Image.open("blank.png"))    
        self.default_img_r=self.canvas_r.create_image(w/2,60, anchor=N, image=self.img_r)    
        self.canvas_r.image = self.img_r  
        self.canvas_r.grid(row=self.pos_r[0], column=self.pos_r[1])

        #LOWER BUTTONS##
        self.left_del_button=ttk.Button(self, text = "Delete Left",command = self.delete_left)
        self.left_del_button.grid(row=3, column=0, padx=10, pady=5)
        self.right_del_button=ttk.Button(self, text = "Delete Right",command = self.delete_right)
        self.right_del_button.grid(row=3, column=3, padx=10, pady=5)

        self.nextbutton=ttk.Button(self, text = "Show Next",command = self.shownextmatch)
        self.nextbutton.grid(row=3, column=3, padx=10, pady=5,sticky="S")
        self.prevbutton=ttk.Button(self, text = "Show previous",command = self.showprevmatch)
        self.prevbutton.grid(row=3, column=0, padx=10, pady=5,sticky="S")

        w_c=100
        h_c=40
        self.canvas_c=Canvas(self,width=w_c,height=h_c)
        self.match_no_label=self.canvas_c.create_text(w_c/2,h_c/2, text=f'{self.counter_matchlst}/{len(self.matches)}')
        self.canvas_c.grid(row=4,column=1,columnspan=2, pady=10, sticky="N")
        self.progress_var = DoubleVar()
        self.progress_var.set(0)
        self.progressbar_counter=0
        self.progress_bar = ttk.Progressbar(self, orient = 'horizontal', variable=self.progress_var, length = 450)#mode = 'determinate'
        self.progress_bar.grid(column = 1, row = 10, padx=10,pady=5, columnspan=2, sticky="W")
        self.startbutton=ttk.Button(self, text = "Start Comparing",command = self.compare_handler)
        self.startbutton.grid(row=10, column=3, padx=10, pady=5)
        
        self.canvas_autodel= Canvas(self, width = 140, height = 120)#, bg='#D5E88F')
        self.autodeltext = self.canvas_autodel.create_text(70,25,text="After comparing \nthis deletes all \nsmaller matched Images.")
        self.canvas_autodel.grid(column=3,row=1,padx=10, pady=50,  rowspan=3,sticky="N")
        self.autodeletebutton=ttk.Button(self, text = "Auto Delete Matches",command = self.autodeletematches)
        self.autodeletebutton.grid(row=1, column=3, padx=10, pady=20,sticky="N")

        self.canvas_u= Canvas(self, width = 120, height = 30) #, bg='#D5E88F')
        self.imgfoundtext = self.canvas_u.create_text(50,15,text="Waiting to start")
        self.canvas_u.grid(column=2,row=10,padx=10, pady=10, sticky="E")
       
    def init_vars(self,complete_reset=True):
        self.imglst=[]
        self.returnimglst=[]
        self.orb = cv.ORB_create()
        self.progressbar_counter=0
        self.matches={}
        self.deleted={}
        if complete_reset:
            self.counter_matchlst=0
            self.searchpath=""
            self.root="./"
            self.key_l=""
            self.key_r=""
        
    def checkButtons(self):
        self.include_subdirs_tk=tk.BooleanVar()
        self.include_subdirs_tk.set(False)
        self.include_subdirs_check = ttk.Checkbutton(self.options, variable=self.include_subdirs_tk, text = "Include Subdirs" )
        self.include_subdirs_check.grid(row = 0, column = 1, rowspan=2)
    def fileDialog(self):
        self.searchpath = filedialog.askdirectory(initialdir =  "/", title = "Select A Directory")
        if len(self.searchpath)>31:
            self.label.configure(text = "..."+self.searchpath[-28:])
        else:
            self.label.configure(text = self.searchpath)
    def delete_left(self):
        if len(self.matches)>0:
            self.delete_img(self.key_l)
    def delete_right(self):
        if len(self.matches)>0:
            self.delete_img(self.key_r,False)
    def delete_img(self,id,left=True):
        if id in self.deleted:
            messagebox.showinfo("Info", "The file is already deleted.")
        else:
            #try:
                send2trash(str(self.imglst[id].path).replace('/','\\'))#fix for send2trash v1.5.0
                print("deletetd",self.imglst[id].path)
                self.deleted[id]=True
                self.update_img(id,left)
            #except:
             #   messagebox.showerror("Error", "Error when deleting the Picture.")
        self.after(1000,self.shownextmatch)

    def update_img(self,id,left=True):
        res=f'{self.imglst[id].resolution[0]}x{self.imglst[id].resolution[1]}  {self.imglst[id].size:.2f} MB'
        if left:
            self.img_l=ImageTk.PhotoImage(self.imglst[id].preview)
            self.canvas_l.itemconfig(self.default_img_l, image=self.img_l)
            fname= self.imglst[id].filename if len(self.imglst[id].filename)<=32 else "..."+self.imglst[id].filename[-30:]
            self.canvas_l.itemconfig(self.def_txt_l, text=fname)
            self.canvas_l.itemconfig(self.def_res_l, text=res)
            if id in self.deleted:
                self.canvas_l.itemconfig(self.def_del_l, text="DELETED")
                self.canvas_l.lift(self.def_del_l)
            else:
                self.canvas_l.itemconfig(self.def_del_l, text="")
            self.key_l=id
        else:
            self.img_r=ImageTk.PhotoImage(self.imglst[id].preview)
            self.canvas_r.itemconfig(self.default_img_l, image=self.img_r)
            self.canvas_r.itemconfig(self.def_txt_r, text=self.imglst[id].filename)
            self.canvas_r.itemconfig(self.def_res_r, text=res)
            if id in self.deleted:
                self.canvas_r.itemconfig(self.def_del_r, text="DELETED")
                self.canvas_r.lift(self.def_del_r)
            else:
                self.canvas_r.itemconfig(self.def_del_r, text="")
            self.key_r=id
    def show_match(self,mid):
        if len(self.matches)>0:
            id1=list(self.matches.keys())[mid]
            id2=self.matches.get(id1)
            #print("Displaying images No",id1, "and", id2)
            self.update_img(id1)
            self.update_img(id2, False)
            self.canvas_c.itemconfig(self.match_no_label,text=str(self.counter_matchlst+1)+"/"+str(len(self.matches)))
    def shownextmatch(self):
        if len(self.matches)>0:
            if self.counter_matchlst<=len(self.matches.keys())-2:
                self.counter_matchlst+=1
            self.show_match(self.counter_matchlst)
    def showprevmatch(self):
        if len(self.matches)>0:
            if self.counter_matchlst>0:
                self.counter_matchlst-=1
            self.show_match(self.counter_matchlst)
    def comparecolorvals(self,cval1,cval2):
        dev_percent=[0,0,0]
        for id in range(3):
            cval1[id]=(cval1[id]<1)*1+cval1[id]
            cval2[id]=(cval2[id]<1)*1+cval2[id]
            dev_percent[id]=abs(cval1[id]-cval2[id])/(cval1[id]+cval2[id])*100<=self.allowed_deviation_percent
            #print("colordeviation:",abs(cval1[id]-cval2[id])/(cval1[id]+cval2[id])*100,"returnval:",dev_percent)
        return all(dev_percent)
    def compare(self):
        self.matches={}
        for index in range(0,len(self.imglst)-1):
            for id in range(index+1,len(self.imglst)):
                if self.imglst[index].status=="processed" and self.imglst[id].status=="processed":
                    dev_perc=compare2keymat(self.imglst[index].keymat,self.imglst[id].keymat)
                    #print("Img",index,"vs",id,"dev_percent:",dev_perc)
                    if dev_perc<self.allowed_deviation_percent:
                        shape1=self.imglst[index].resolution
                        shape2=self.imglst[id].resolution
                        rr=(shape1[0]/shape2[1])/(shape2[0]/shape2[1])
                        if rr>=(100-self.allowed_deviation_percent/2)/100 and rr<=(100+self.allowed_deviation_percent/2)/100: # /2 weil abweichung vom Mittelwert bestimmt
                            if self.comparecolorvals(self.imglst[index].colorval,self.imglst[id].colorval):
                                self.matches[index]=id
            self.progressbar_counter+=1
            self.progress_var.set(self.progressbar_counter)
            self.update()
    def extract_from_gui(self):
        temp=self.entry.get().lower().replace(".","").replace(" ","").replace(";",",").replace(":",",").split(",")#Intensive Cleaning because of dummies.
        self.allowed_data_types=temp

        temp=self.fineness_var.get()
        if temp<self.fineness_var_min:
            self.fineness_var.set(self.fineness_var_min)
        if temp>self.fineness_var_max:
            self.fineness_var.set(self.fineness_var_max)
        self.fineness=int(self.fineness_scale.get())

        temp=self.prev_h_var.get()
        if temp<self.prev_h_var_min:
            self.prev_h_var.set(self.prev_h_var_min)        
        if temp>self.prev_h_var_max:
            self.prev_h_var.set(self.prev_h_var_max)
        self.preview_height=int(self.prev_h_var.get())

        temp=self.min_id_var.get()
        if temp<self.prev_h_var_min:
            self.prev_h_var.set(self.prev_h_var_min)
        if temp>self.prev_h_var_max:
            self.prev_h_var.set(self.prev_h_var_max)
        self.min_id=int(self.min_id_var.get())

        self.allowed_deviation_percent=100-self.min_id
        self.include_subdirs=self.include_subdirs_tk.get()
    def putImgstoQueue(self):
        for img in self.imglst:
            self.q1.put(img)
            self.progressbar_counter+=1
            self.progress_var.set(self.progressbar_counter)
            self.update()
    def getImgsfromQueue(self):
        while len(self.returnimglst)<len(self.imglst):
            retimg=None
            if not self.q2.empty():
                try:
                    retimg=self.q2.get(1)
                except:
                    pass
            else:
                sleep(0.1)
            #print("GUI is waiting",retimg)
            if type(retimg)!=type(None):
                self.returnimglst.append(retimg)
                self.progressbar_counter+=10
                self.progress_var.set(self.progressbar_counter)
            self.update()
        while not self.q1.empty(): #signal for imgworker termination
            temp=self.q1.get()
    def compare_handler(self):
        if not self.searchpath:
            messagebox.showerror("Error", "Please specify a folder first.")
        else:
            #messagebox.showinfo("Handling Info", "The Window will freeze now and hopefully finish soon. You can see the progress in the other window until a better solution is found.")
            self.init_vars(False)
            self.extract_from_gui()
            self.find_imgs()
            self.putImgstoQueue()
            self.getImgsfromQueue()
            #print("GUI RESULTS:",self.returnimglst)
            self.imglst=self.returnimglst
            self.compare()
            #print(self.matches)
            messagebox.showinfo("Search Completed", "Found "+str(len(self.matches.keys()))+" Matches")
            self.show_match(0)
    def find_imgs(self):
        startprogress=10
        self.progressbar_counter=startprogress
        self.progress_var.set(self.progressbar_counter)
        self.progress_bar["maximum"]=80
        self.update()
        self.canvas_u.itemconfig(self.imgfoundtext, text="Preprocessing")
        for root, dirs, files in os.walk(self.searchpath):
            self.root=root            
            for filename in files:
                fn_list=filename.split(".")
                ext=fn_list[-1].lower()
                if ext in self.allowed_data_types:
                    #print("ext regognized:", ext)
                    path=os.path.join(root,filename)
                    try:
                        size=int(os.path.getsize(path))/1000000
                    except:
                        size=0.01
                    self.imglst.append(Bild(path,filename,size,self.preview_height,self.fineness))
            if not self.include_subdirs:
                break
        maximgs=len(self.imglst)
        self.progressbar_counter=startprogress+maximgs
        self.progress_bar["maximum"] = maximgs*12+startprogress
        self.canvas_u.itemconfig(self.imgfoundtext, text=f"{maximgs} Images found")
        self.update()
    def autodeletematches(self,delsmaller=True):
        if len(self.matches)>0:
            if all([True if self.imglst[id].status=="processed" else False for id in self.matches.keys()]):
                if messagebox.askyesnocancel("Autodelete smaller Images","Are you sure to delete all smaller matched images? They will be moved to trash!"):
                    for id1 in self.matches.keys():
                        id2=self.matches.get(id1)
                        if not (id1 in self.deleted or id2 in self.deleted):
                            img_to_del=id1
                            if self.imglst[id1].size>self.imglst[id2].size:
                                img_to_del=id2
                            elif self.imglst[id1].resolution[0]*self.imglst[id1].resolution[1]>self.imglst[id2].resolution[0]*self.imglst[id2].resolution[1]:
                                img_to_del=id2
                            elif len(self.imglst[id1].filename)<len(self.imglst[id1].filename):
                                img_to_del=id2
                            self.delete_img(img_to_del)
                            self.show_match(0)
        else:
            messagebox.showinfo("Info","First click on 'Start Comparing' !")


### FUNCTIONS ###

def compare2keymat(tar1,tar2):
    dif=np.logical_xor(tar1,tar2)
    points=(np.count_nonzero(tar1)+np.count_nonzero(tar2))/2
    if points==0:
        points=10
    return dif.sum()/points*50 # 50 because 1 keypoint in different location makes 2 difference.

if __name__ == '__main__':
    print("Please Leave this window open while the programm is needed. Is good for debugging etc")
    #mp.set_start_method('fork')
    window=Root()    
    window.mainloop()
    input("You can close this window now by pressing Enter")
