import os
import sys
import requests
import json
sys.path.append('src') ;

import vad
import extract_audio
import client
import paste_subs

if __name__ == '__main__' :

	model_path = 'models/output_graph.pb' ;
	alpha_path = 'models/alphabet.txt' ;
	bin_path = 'models/lm.binary' ;
	trie_path = 'models/trie' ;
	video_path = sys.argv[1] ;
	time_frame = int(sys.argv[2]) ;

	print video_path ;

	file_name = video_path.split('/') ;
	file_name = os.path.splitext(file_name[len(file_name) - 1])[0] ;

	if not os.path.exists('audio') :
		os.makedirs('audio') ;
	if not os.path.exists('clips') :
		os.makedirs('clips') ;
	if not os.path.exists('output') :
		os.makedirs('output') ;	

	orig_audio_path = 'audio/' + file_name + '.wav' ;
	dest = 'clips/' + file_name + '/' ;
	output_path = 'output/' + file_name + '.mp4' ;

	## use vad for segmenting audio segments
	audio = extract_audio.save_audio(video_path, orig_audio_path) ;
	voices = vad.main([3, orig_audio_path]) ;

	## extract audio from video and store audio segments using vad output
	clip_times = extract_audio.do(audio, voices, dest) ;
	print clip_times ;

	## speech to text using deepspeech
	subs = client.main(model_path, alpha_path, bin_path, trie_path, dest) ;

	## save subs to .txt file
	with open('output/' + file_name + '.txt', 'w') as f :
		for i in range(len(subs)) :
			f.write(str(clip_times[i][0]) + 's - ' + str(clip_times[i][1]) + 's : ' + subs[i] + '\n') ;

	## combining subtitles
	output_text = "" ;
	for i in subs :
		output_text += i + ". " ;
	output_text = output_text.strip() ;
	'''
	## get text summarizer output
	r = requests.post("http://zlabs-nlp:5000/generate_summary", data={'text': output_text, 'n': 3}).text ;
	print r
	summary = ''.join(json.loads(r)['3'])
	with open('output/' + file_name + '.txt', 'a') as f :
		f.write('\n' + summary) ;
	'''
	## paste subs on video
	paste_subs.do(video_path, subs, clip_times, time_frame, output_path) ;

