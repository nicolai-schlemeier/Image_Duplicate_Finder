# Image_Duplicate_Finder
Purpose:
When my girlfriend and I wanted to make a photo collection we each looked through all our devices for the photos and collected them in one folder. There where of cause a lot duplicates, but within 500+ photos they where difficult to find and some photos where resized because we sent them from one to the other, so the decision which one to keep was also important. Finally the deletion proces took some time.
To solve that problem I wrote this software.

Goal: 
Find duplicate/similar images in the specified folder, even if they where resized. Provide an effective way to delete duplicate images.

infos for usage:

-the "blank.png" must be in the directory as the exe. You find the exe in the releases tab.

-the parameters: 
	fineness:how precise the programm works. Too much will result in matches not being found, to low will result in false matches, 20-50 ist recommended.
	min identity: how many percent of the images have to match. Too much will result in matches not being found, to low will result in false matches, 20-50 ist recommended.
	preview height: resolution of displayed images, using less saves memory.
	
-works on png and jpg files and all other files that can be read with opencv and PIL.(Not pdf etc)

-would not recommend to use it on much more than 1000 Highres images at once to prevent memory shortage. Compensate by reducing the preview height.

-how can I ensure there is no virus when downloading the .exe? Very good question. You shouldn't trust guys from the internet. 

	A) Your antivirus software should tell you
	
	B) You can use a hash programm like quickhash to generate a hashcode(very individual key) of your file. The file I compiled myself without including viruses has the SHA512 Key: BAA2AB33F46A647DEEB13C55D7A7367FC50F7428DAB933164C84EC29F7543169B389BC0FA126E05A0C98487E3861CF2DC224BA6C9875D9A86580539906F9519F
Actually I don't even know how to write a virus...


How it works: All photos are analysed to find keypoints with opencv. Then an empty squarematrix with "fineness" length and width is populated in the fields where keypoints are found.
This is a kind of size indipendend fingerprint of the image, which is then compared to the other fingerprints. When the matrixes match to the specified percentage a match with the names and resolution is displayed.
You can then delete one of the duplicates with just one click.

What it wont find:
mirrored, rotated or shifted images and images that have the same motive, but at a slightly different place. The behavior can be supressed by using a lower fineness.

speed:
depends mainly on your disk speed, but about 1 sec for high res photo is a good value.
Spoken in the big o notation: O(n), because each photo is processed once.
The matrix comparison is of cause O(n²), but due to the much smaller data volume it is usually completed within 0.5 sec for 500 Images.


Known Problems:
-it takes ca 10 sec to startup... yes, know pythonic problem...no easy fix for that.

-this program is based on dictionarys. therefore some images can only be matched once.

To be sure to find all similar images the programm should be run at least twice or until no more matches are found.

- the design is lame, could be from year 2000. Yes, live with it.

-there are some minor bugs.... Yes, live with it.


