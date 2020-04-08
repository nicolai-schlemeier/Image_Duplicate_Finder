import numpy as np
import cv2 as cv
from matplotlib import pyplot as plt
import os
import pickle
import time
from datetime import datetime
import configparser
import logging
timer_prgm_start = time.perf_counter()


#Initialisation
images={}
img_info={}
compare_dict={}
orb = cv.ORB_create()

dt_string = datetime.now().strftime("%d_%m_%Y %H_%M_%S")



#Read the configuration
config=configparser.ConfigParser()
config.read("configuration.ini")
sectionname="custom_parameters"
if not config.has_section(sectionname):
    errtxt='section '+sectionname+' not found in configuration.ini!'
    raise Exception(errtxt)

if config.has_option(sectionname,"fineness"):
        fineness=config.getint(sectionname,"fineness")
else:
        fineness=config.getint("default","fineness")
if config.has_option(sectionname,"allowed_deviation_percent"):
        allowed_deviation_percent=config.getfloat(sectionname,"allowed_deviation_percent")
else:
        allowed_deviation_percent=config.getfloat("default","allowed_deviation_percent")
if config.has_option(sectionname,"searchpath"):
        searchpath=config.get(sectionname,"searchpath")
else:
        searchpath=config.get("default","searchpath")
if config.has_option(sectionname,"preview_height"):
        preview_height=config.getint(sectionname,"preview_height")
else:
        preview_height=config.getint("default","preview_height")
if config.has_option(sectionname,"allowed_data_types"):
        allowed_data_types=config.get(sectionname,"allowed_data_types").lower().split(",")
else:
        allowed_data_types=config.get("default","allowed_data_types").lower().split(",")
if config.has_option(sectionname,"include_subdirs"):
        include_subdirs= config.getboolean(sectionname,"include_subdirs")
else: 
        include_subdirs=config.getboolean("default","include_subdirs")
if config.has_option(sectionname,"include_logger"):
        include_logger= config.getboolean(sectionname,"include_logger")
else: 
        include_logger=config.getboolean("default","include_logger")
if config.has_option(sectionname,"print_to_console"):
        print_to_console= config.getboolean(sectionname,"print_to_console")
else: 
        print_to_console=config.getboolean("default","print_to_console")



#Configurate Logger

log_fname='image_comparing'+dt_string+'.log'
logger = logging.getLogger(__name__)
logger.disabled = not include_logger
if include_logger:
    logger.setLevel(logging.INFO)
    fh = logging.FileHandler(log_fname)
    formatter = logging.Formatter('%(asctime)s -%(levelname)s: %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)

logger.info("Programm started at "+ str(dt_string))


def compute_vector(img):
    #cv.imshow('image',img)
    kp = orb.detect(img,None)
    kp, des = orb.compute(img, kp)
    koordinates=[k.pt for k in kp]
    dim=img.shape
    target_vec=np.full((fineness,fineness),0, dtype=bool)
    for k in koordinates:
        if k[0].is_integer() and k[1].is_integer():
            rel_x=k[0]/dim[1]
            rel_y=k[1]/dim[0]
            target_vec[int(round(rel_x*fineness))][int(round(rel_y*fineness))]=1
    return target_vec

def compare2target_vec(tar1,tar2):
    dif=np.logical_xor(tar1,tar2)
    points=(np.count_nonzero(tar1)+np.count_nonzero(tar2))/2
    if points==0:
        points=10
    return dif.sum()/points*50 # because 1 keypoint in different location makes 2 difference.

def compare_images(compare_dict):
    matches={}
    compare_values=[val for val in compare_dict.values()]
    compare_names=[name for name in compare_dict.keys()]
    for index in range(0,len(compare_values)-1):
        for id in range(index+1,len(compare_values)):
            frac=compare2target_vec(compare_values[index],compare_values[id])
            #print("Comparing ",compare_names[index]," and ",compare_names[id]," with Result:",frac)
            if frac<allowed_deviation_percent:
                print("Match found!", compare_names[index], compare_names[id],"with","{0:.1f}".format(100-frac),"% Identity")
                logger.info("Match found! "+ str(compare_names[index])+" & "+ str(compare_names[id])+" with "+"{0:.1f}".format(100-frac)+"% Identity")
                matches[compare_names[index]]=compare_names[id]
    return matches


def main():
    print("Searching through",searchpath, " and all Subdirs" if include_subdirs else "")
    print("it is working right now, might take a while. If worried check log file for progress.")
    counter=0
    for root, dirs, files in os.walk(searchpath):
            counter=0
            logger.debug("Searching in "+ str(root))
            for filename in files:
                #print("file analysed:",filename)
                timer_loopstart=time.perf_counter()
                fn_list=filename.split(".")
                ext=fn_list[-1].lower()
                if ext in allowed_data_types:
                    img=cv.imread(os.path.join(root,filename),0)#load image in grayscale
                    if type(img)!=type(None):
                        img_info[filename]=img.shape
                        compare_dict[filename]=compute_vector(img)
                        img=cv.imread(os.path.join(root,filename))
                        res=cv.resize(img,(int(preview_height),int(round(img.shape[0]* preview_height/img.shape[1]))))# reszizing after computation to save memory                
                        images[filename]=res
                        img_info[filename]=img.shape
                        timer_img= time.perf_counter()
                        counter+=1
                        if print_to_console: print("Computed "+str(filename)+" in "+ "{0:.2f}".format(timer_img-timer_loopstart)+"s, Progress(per folder):"+"{0:.0f}".format(counter/len(files)*100)+"%")
                        logger.info("Computed "+str(filename)+" in "+ "{0:.2f}".format(timer_img-timer_loopstart)+"s, Progress(per folder):"+"{0:.0f}".format(counter/len(files)*100)+"%")
                    else:
                        print("Error occured while reading",filename)
                        logger.warning("Error occured while reading"+str(filename)+" in "+str(root))
            if not include_subdirs:
                break
    timer_compu_fin=time.perf_counter()
    print("All ",counter," Images computed after ", "{0:.2f}".format(timer_compu_fin-timer_prgm_start), " s total")
    logger.info("All "+str(counter)+" Images computed after "+ "{0:.2f}".format(timer_compu_fin-timer_prgm_start)+ " s total")
    matches=compare_images(compare_dict)
    timer_compared=time.perf_counter()
    logger.info("Images compared in "+"{0:.2f}".format(timer_compared-timer_compu_fin)+" s")
    if matches:
        print(len(matches),"Matches found!")
        logger.info(str(len(matches))+"Matches found!")

        fig=plt.figure(figsize=(8, 6))
        for name1,name2 in matches.items():
            columns = 2
            rows = 1
            id=1
            for name in [name1,name2]:
                fig.add_subplot(rows, columns, id, title=name+" "+str(img_info[name]))
                plt.imshow(images[name][...,::-1].copy())
                id+=1
            plt.ion()
            plt.show()
            decision=input(str("Type l to delete "+str(name1)+ " r to delete "+str(name2)+ " or b to keep both:"))
            if decision in ["l", "L"]:
                os.remove(os.path.join(root,name1))
                print(name1," sucessfully removed.")
                logger.info(str(name1)+" sucessfully removed.")
            elif decision in ["r", "R"]:
                os.remove(os.path.join(root,name2))
                print(name2, " sucessfully removed.")
                logger.info(str(name2)+ " sucessfully removed.")
            else:
                logger.info("no file deleted.")
                print("ok!")
            fig.clf()
        plt.close('all')        
    else:
        print("No matches found.")
        logger.info("No matches found.")

if __name__ == '__main__':
    main()

    
#Fun stuff: Show all the targetvectors of the images
if input("What to see the target vectors? Type y:") in ["y","Y"]:
    fig=plt.figure(figsize=(8, 8))
    columns = 4
    rows = 4
    index=1
    for name,img in compare_dict.items():
        fig.add_subplot(rows, columns, index, title=name)
        plt.imshow(img, cmap='Greys', )# interpolation='nearest')
        index+=1
        if index>columns*rows:
            index=1
            plt.show()
            a=input("next? ")
            fig.clf()
    plt.show()
    a=input("All Vectors displayed. Confirm:")
    
timer_end=time.perf_counter()
logger.info("Total Runtime: "+"{0:.2f}".format(timer_end-timer_prgm_start)+" s")
cv.destroyAllWindows()


###Example for image, displayed with green keypoints.
#for img in images.values():
#    cv.imshow('image',img)
#    cv.waitKey(0)
#     #draw only keypoints location,not size and orientation
#    img2 = cv.drawKeypoints(img, kp, None, color=(0,255,0), flags=0)
#    plt.imshow(img2), plt.show()
#cv.destroyAllWindows()
