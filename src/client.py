#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function
from timeit import default_timer as timer

import time
import argparse
import subprocess

import sys
import os
import shutil
import numpy as np

import scipy.io.wavfile as wav
from deepspeech.model import Model
from sox import Transformer
from pydub import AudioSegment
from moviepy.editor import *
import pygame

sys.path.append('src') ;
import paste_subs

# These constants control the beam search decoder

# Beam width used in the CTC decoder when building candidate transcriptions
BEAM_WIDTH = 500

# The alpha hyperparameter of the CTC decoder. Language Model weight
LM_WEIGHT = 1.75

# The beta hyperparameter of the CTC decoder. Word insertion weight (penalty)
WORD_COUNT_WEIGHT = 1.00

# Valid word insertion weight. This is used to lessen the word insertion penalty
# when the inserted word is part of the vocabulary
VALID_WORD_COUNT_WEIGHT = 1.00


# These constants are tied to the shape of the graph used (changing them changes
# the geometry of the first layer), so make sure you use the same constants that
# were used during training

# Number of MFCC features to use
N_FEATURES = 26

# Size of the context window used for producing timesteps in the input vector
N_CONTEXT = 9

def convert_samplerate(audio_path):

	sox_cmd = 'sox {} --type raw --bits 16 --channels 1 --rate 16000 - '.format(audio_path)
	try:
		p = subprocess.Popen(sox_cmd.split(),
							 stderr=subprocess.PIPE, stdout=subprocess.PIPE)
		output, err = p.communicate()

		if p.returncode:
			raise RuntimeError('SoX returned non-zero status: {}'.format(err))

	except OSError as e:
		raise OSError('SoX not found, use 16kHz files or install it: ', e)

	audio = np.fromstring(output, dtype=np.int16)

	return 16000, audio

def convert_sr_channel(audio) :

	transformer = Transformer()
	transformer.convert(samplerate=16000, n_channels=1)
	transformer.build(original_audio_file, wav_file)


def read_video(path) :

	video = VideoFileClip(path) ;
	audio = video.audio ;
	duration = video.duration ;
	fs = audio.fps ;

	audio.write_audiofile('audio/pm.wav',fps=16000) ;

	if os.path.exists('clips') :
		shutil.rmtree('clips') ;

	os.makedirs('clips') ;
	print(duration) ;


	# audio = audio.to_soundarray(fps=16000) #* 32767 ;

	# if audio.shape[1] > 1 :
	# 	audio = np.int16(np.mean(audio, axis=1)) ;
	# 	print(audio , np.count_nonzero(audio)) ;
	# 	# wav.write('test/2.wav', 16000, (audio)) ;
	# 	# audio = audio[:,0]
	# 	# wav.write('test/3.wav', 16000, np.int16(audio)) ;

	return fs, audio ;


def main(model, alphabet, lm, trie, dest):

	# parser = argparse.ArgumentParser(description='Benchmarking tooling for DeepSpeech native_client.')
	# parser.add_argument('model', type=str,
	# 					help='Path to the model (protocol buffer binary file)')
	# parser.add_argument('alphabet', type=str,
	# 					help='Path to the configuration file specifying the alphabet used by the network')
	# parser.add_argument('lm', type=str, nargs='?',
	# 					help='Path to the language model binary file')
	# parser.add_argument('trie', type=str, nargs='?',
	# 					help='Path to the language model trie file created with native_client/generate_trie')
	# parser.add_argument('audio', type=str,
	# 					help='Path to the audio file to run (WAV format)')
	# args = parser.parse_args()

	# print(args);

	print('Loading model from file %s' % (model), file=sys.stderr)
	model_load_start = timer()
	ds = Model(model, N_FEATURES, N_CONTEXT, alphabet, BEAM_WIDTH)
	model_load_end = timer() - model_load_start
	print('Loaded model in %0.3fs.' % (model_load_end), file=sys.stderr)

	if lm and trie:
		print('Loading language model from files %s %s' % (lm, trie), file=sys.stderr)
		lm_load_start = timer()
		ds.enableDecoderWithLM(alphabet, lm, trie, LM_WEIGHT,
							   WORD_COUNT_WEIGHT, VALID_WORD_COUNT_WEIGHT)
		lm_load_end = timer() - lm_load_start
		print('Loaded language model in %0.3fs.' % (lm_load_end), file=sys.stderr)

	# fs, audio = read_video(args.audio) #wav.read(args.audio)
	# return ;
	print('Running inference.', file=sys.stderr)
	clips = os.listdir(dest) ; # clips dir path

	subs = [] ;

	for i, clip in enumerate(clips) :
		fs, audio = wav.read(dest + str(i) + '.wav') ;

		if fs != 16000:
			if fs < 16000:
				print('Warning: original sample rate (%d) is lower than 16kHz. Up-sampling might produce erratic speech recognition.' % (fs), file=sys.stderr)
		
		fs, audio = convert_samplerate(dest + str(i) + '.wav')	
		audio_length = len(audio) * ( 1 / 16000)

		inference_start = timer()
		subs.append(ds.stt(audio, fs)) ;
		print(subs[len(subs) - 1]);

		inference_end = timer() - inference_start
		print('Inference took %0.3fs for %0.3fs audio file.' % (inference_end, audio_length), file=sys.stderr)

		# break ;

	return subs ;	

# if __name__ == '__main__':
# 	main()
