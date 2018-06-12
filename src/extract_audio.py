from moviepy.editor import *
import sys
import os
import shutil 

def save_audio(path, dest) :

	video = VideoFileClip(path) ;
	audio = video.audio ;
	audio.write_audiofile(dest, fps=16000) ;

	return audio ;

def do(audio, voices, dest) :

	# video = VideoFileClip(path) ;
	# audio = video.audio ;
	duration = audio.duration ;
	fs = audio.fps ;	

	if os.path.exists(dest) :
		shutil.rmtree(dest) ;

	os.makedirs(dest) ;

	is_first = False ;
	st = 0 ;

	clip_times = [] ;
	_len = len(voices) ;

	for i in range(len(voices)) :

		if voices[i] == 1 and not is_first :
			st = i ;
			is_first = True ;
		elif voices[i] == 0 and is_first :

			st = 0 if st - 2 < 0 else st - 2 ;
			end = _len if i + 2 > _len else i + 2 ;

			clip_times.append([ round(st * 0.06, 2), round(end * 0.06, 2) ]) ;
			is_first = False ;			

	#print(clip_times);
	
	for i, time in enumerate(clip_times) :
		clip = audio.subclip(time[0], time[1]) ;
		clip.write_audiofile(dest + str(i) + '.wav', fps=16000) ;

	return clip_times ;

	'''		
	i = 0 ;
	frame_size = 10 ;
	# split audio at every frame size step
	while (i + frame_size < duration) :
		clip = audio.subclip(i, i + frame_size) ;
		clip.write_audiofile(dest + str(i) + '.wav', fps=16000) ;
		i += frame_size ;

	clip = audio.subclip(i) ;
	clip.write_audiofile(dest + str(i) + '.wav', fps=16000) ;
	'''		

# if __name__ == "__main__" :

# 	read_video(sys.argv[1]) ;