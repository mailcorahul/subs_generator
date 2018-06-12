from moviepy.editor import *
from PIL import Image, ImageFont, ImageDraw
import numpy as np
import math

## global variables used inside show_frame method
subtitles = [] ;
tf = 10 ;
ct = [] ;

def draw_text(im,str):

	img = Image.fromarray(im)
	img_h,img_w = im.shape[:2]

	font = ImageFont.truetype(font='utils/arial.ttf', size=15)
	draw = ImageDraw.Draw(img)
	text_w,text_h = draw.textsize(str,font = font)

	text_img_w = img_w*0.8
	cut_factor = text_w/text_img_w
	line_h = img_h * 0.8
	# print cut_factor
	if cut_factor > 1:
		# str_view = memoryview(str)
		str_ratio = int(math.floor(len(str) / cut_factor))
		lines = []
		for i in range(int(math.ceil(cut_factor))):
			# print str[i*str_ratio:(i+1)*str_ratio]+'hi'
			line = (str[i * str_ratio:(i+1)*str_ratio])
			# print line,i
			# print new_line__index
			# str = str[:new_line__index] + '\n' +str[new_line__index + 1:]
			draw.multiline_text((img_w * 0.1 ,line_h + (i * (text_h*1.2)) ), line, font=font, fill=(255,255,0))

	else:

		draw.multiline_text((((img_w -text_w) / 2) , img_h * 0.8), str, font=font, fill=(255,255,0))
	
	# print img_w ,text_w
	# exit()	
	return np.array(img)

def show_frame(gf,t):
	fr = gf(t)
	# print fr.shape
	#print t

	idx = -1 ;
	for j in range(len(ct)) :
		if t >= ct[j][0] and t <= ct[j][1] :
			idx = j ;
			break ;

	if idx != -1 :
		fr = draw_text(fr, subtitles[idx]) ;
	else :
		fr = draw_text(fr, "") ;

	return fr


def do(video_path, subs, clip_times, time_frame, output_path) :

	global subtitles , tf , ct ;
	subtitles = subs ;
	tf = time_frame ;
	ct = clip_times ;

	video = VideoFileClip(video_path) ;
	new_clip = video.fl(show_frame, apply_to='mask') ;
	new_clip.to_videofile(output_path) ;