# Image_Duplicate_Finder
Purpose:
When my girlfriend and I wanted to make a photo collection we each looked through all our devices for the photos and collected them in one folder. There where of cause a lot duplicates, but within 500+ photos they where difficult to find and some photos where resized because we sent them from one to the other, so the decision which one to keep was also important. Finally the deletion proces took some time.
To solve that problem I wrote this software.

Features:
- Easy to use graphical user Interface
- Recognizes Images with keypoints at the same spots (or slightly shifted), therefore recognizes rescaled Images
- Effective algorithm: Processes every image only once, comparison on minimal data, should handle 1000 Images (but needs some RAM then...)
- Fast comparison: Tahnks to parallel processing (1 Process per CPU core) of the images. This is new in V2.0.
- Delete Duplicates with just one click per Duplicate or even faster with
- Autodelete smaller Images: After computing the matching Images, you can browse them or refine search and search again. When you are happy with the result get rid of all the copys with just two more Clicks.

Infos for usage:
- download the exe file from the "releases" tab.
- the "blank.png" and "computer.ico" must be in the same directory as the exe.

- the parameters: 
	fineness:How many slices and rows the picture will be devided. A match is recognised, when Keypoints occur in the same spot. With a lower value a wider range of images will be matched. Higher value restricts matches to more or less exact copies. 20-50 ist recommended.
	min identity: how many percent of the keypoints have to match. High values will result in matches only for exact copies, low values will result in false matches, about 50-70 ist recommended.
	preview height: resolution of displayed images is reduced to save RAM, higher values will consume more RAM, 200px should be a good.	
- works on png and jpg files and all other files that can be read with opencv.(Not pdf etc)

- how can I ensure there is no virus when downloading the .exe? Very good question. You shouldn't trust guys from the internet. 

	A) Your antivirus software should tell you
	
	B) You can use a hash programm like quickhash to generate a hashcode(very individual key) of your file. The file I compiled myself without including viruses has the SHA256 Key: 1348D809BF3EFE72066390ACEF3805282F0DE39C0CF6CBF98FA7B98996F6B46C ("Release v2.0.zip")
Actually I don't even know how to write a virus...


How it works: All photos are analysed to find keypoints with opencv. Then an empty squarematrix with "fineness" length and width is populated in the fields where keypoints are found.
This is a kind of size indipendend fingerprint of the image, which is then compared to the other fingerprints. When the matrixes match to the specified percentage a match with the names and resolution is displayed. For better matching also the image ratio and some colorvalues are also considered.
You can then delete one of the duplicates with just one click.

What it wont find:
mirrored, rotated or shifted images and images that have the same motive, but at a slightly different place. This behavior can be supressed by using a lower fineness.
Also multiple duplicates might get matched right (because python-dictionarys). To be 100% sure that you eliminated all duplicates repeat the steps search and delete until no more matches are found. 

Speed:
Depends mainly on your disk speed, but about 0.5 sec for each high res photo is a good value (SSDs can be faster).
Expressed in the big o notation: O(n), because each photo is processed once (enhanced by parallel processing).
The matrix comparison is of cause O(n²), but due to the much smaller data volume it is usually completed within one sec for 250 Images.


Known Problems:
- PNG files are not displayed transparent in the preview due to internal conversion to RGB, but no worries: The original Files stay untouched!
- it takes up to 10 sec to startup... This is a known pythonic problem because the interpreter needs to be loaded ...there is no easy fix for that.(Except you program this in C++ :D )
- the design is lame, could be from year 2000! Feel free to add some flames.
-can't handle multiple Duplicates well.


