from tkinter import *
from tkinter import ttk, filedialog
import tkinter as tk
from tkinter import messagebox
from ttkthemes import ThemedTk
from PIL import ImageTk, Image
import numpy as np
import cv2 as cv
from matplotlib import pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import *
import os
from copy import deepcopy
import math
from time import sleep
from send2trash import send2trash


class Root(ThemedTk):
    def __init__(self,**kwargs):
        super(Root, self).__init__(theme="breeze")
        self.init_vars()

        self.title("ImageComparing")
        self.minsize(640, 400)
        self.labelFrame = ttk.LabelFrame(self, text = "Select Directory")
        self.label = ttk.Label(self.labelFrame, text = "No path specified yet")
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
        #self.entry_desc.grid(row=3, column=5,pady=1)
        
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
        self.nextbutton.grid(row=6, column=3, padx=10, pady=5)
        self.prevbutton=ttk.Button(self, text = "Show previous",command = self.showprevmatch)
        self.prevbutton.grid(row=6, column=0, padx=10, pady=5)

        w_c=100
        h_c=20
        self.canvas_c=Canvas(self,width=w_c,height=h_c)
        self.match_no_label=self.canvas_c.create_text(w_c/2,h_c/2, text=str(self.counter_matchlst)+"/"+str(len(self.matches)))
        self.canvas_c.grid(row=6,column=1,columnspan=2, pady=10)
        self.progress_bar = ttk.Progressbar(self, orient = 'horizontal', length = 400, mode = 'determinate')
        self.progress_bar.grid(column = 1, row = 10, padx=10,pady=5, columnspan=2)
        self.startbutton=ttk.Button(self, text = "Start Comparing",command = self.compare_handler)
        self.startbutton.grid(row=10, column=3, padx=10, pady=5)


        
    def init_vars(self,complete_reset=True):
        self.images={}
        self.img_info={}
        self.compare_dict={}
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
        self.label.configure(text = self.searchpath)
    def delete_left(self):
        if len(self.matches)>0:
            self.delete_img(self.key_l)
    def delete_right(self):
        if len(self.matches)>0:
            self.delete_img(self.key_r,False)
    def delete_img(self,name,left=True):
        if name in self.deleted:
            messagebox.showinfo("Info", "The file is already deleted.")
        else:
            #try:
                send2trash(str(os.path.join(self.root,name)).replace('/','\\'))#fix for send2trash v1.5.0
                print("deletetd",os.path.join(self.root,name))
                self.deleted[name]=True
                self.update_img(name,left)
            #except:
             #   messagebox.showerror("Error", "Error when deleting the Picture.")
        self.after(1000,self.shownextmatch)

    def update_img(self,key,left=True):
        res=str( self.img_info[key]).replace(","," x").replace("(","").replace(")","")
        if left:
            self.img_l=ImageTk.PhotoImage(self.images[key])
            self.canvas_l.itemconfig(self.default_img_l, image=self.img_l)
            self.canvas_l.itemconfig(self.def_txt_l, text=str(key))
            self.canvas_l.itemconfig(self.def_res_l, text=res)
            if key in self.deleted:
                self.canvas_l.itemconfig(self.def_del_l, text="DELETED")
                self.canvas_l.lift(self.def_del_l)
            else:
                self.canvas_l.itemconfig(self.def_del_l, text="")
            self.key_l=key
        else:
            self.img_r=ImageTk.PhotoImage(self.images[key])
            self.canvas_r.itemconfig(self.default_img_l, image=self.img_r)
            self.canvas_r.itemconfig(self.def_txt_r, text=str(key))
            self.canvas_r.itemconfig(self.def_res_r, text=res)
            if key in self.deleted:
                self.canvas_r.itemconfig(self.def_del_r, text="DELETED")
                self.canvas_r.lift(self.def_del_r)
            else:
                self.canvas_r.itemconfig(self.def_del_r, text="")
            self.key_r=key
    def show_match(self,id):
        if len(self.matches)>0:
            name1=list(self.matches.keys())[id]
            name2=self.matches[name1]
            self.update_img(name1)
            self.update_img(name2, False)
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
        
    def compute_vector(self,img):
        #cv.imshow('image',img)
        kp = self.orb.detect(img,None)
        kp, des = self.orb.compute(img, kp)
        koordinates=[k.pt for k in kp]
        dim=img.shape
        target_vec=np.full((int(self.fineness),int(self.fineness)),0, dtype=bool)
        for k in koordinates:
            if k[0].is_integer() and k[1].is_integer():
                rel_x=k[0]/dim[1]
                rel_y=k[1]/dim[0]
                target_vec[int(math.trunc(rel_x*self.fineness))][int(math.trunc(rel_y*self.fineness))]=1
        return target_vec
    def compare(self):
        self.matches={}
        compare_values=[val for val in self.compare_dict.values()]
        compare_names=[name for name in self.compare_dict.keys()]
        for index in range(0,len(compare_values)-1):
            for id in range(index+1,len(compare_values)):
                frac=compare2target_vec(compare_values[index],compare_values[id])
                if frac<self.allowed_deviation_percent:
                    self.matches[compare_names[index]]=compare_names[id]
        

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
        
    def compare_handler(self):
        if not self.searchpath:
            messagebox.showerror("Error", "Please specify a folder first.")
        else:
            self.init_vars(False)
            self.extract_from_gui()
            self.read_imgs()
            self.compare()
            print(self.matches)
            messagebox.showinfo("Search Completed", "Found "+str(len(self.matches.keys()))+" Matches")
            self.show_match(0)
    def read_imgs(self):       
        self.progressbar_counter=0
        for root, dirs, files in os.walk(self.searchpath):
            self.root=root
            self.progress_bar["maximum"] = len(files)
            self.progress_bar["value"] = 0
            for filename in files:
                fn_list=filename.split(".")
                ext=fn_list[-1].lower()
                self.progress_bar["value"]+=1
                self.progress_bar.update()
                if ext in self.allowed_data_types:
                    img=cv.imread(os.path.join(root,filename),0)#add ,0 to load image in grayscale
                    if type(img)!=type(None):
                        self.img_info[filename]=img.shape
                        self.compare_dict[filename]=self.compute_vector(img)
                        img=Image.open(os.path.join(root,filename))
                        self.images[filename]=img.resize( (int(round(img.width* self.preview_height/img.height)),int(self.preview_height)) )# reszizing after computation to save memory                
            if not self.include_subdirs:
                break
        

        

### FUNCTIONS ###



def compare2target_vec(tar1,tar2):
    dif=np.logical_xor(tar1,tar2)
    points=(np.count_nonzero(tar1)+np.count_nonzero(tar2))/2
    if points==0:
        points=10
    return dif.sum()/points*50 # 50 because 1 keypoint in different location makes 2 difference.

if __name__ == '__main__':
    print("Please Leave this window open while the programm is needed.")
    window=Root()
    window.mainloop()
    print("You can close this window now by pressing any key")
