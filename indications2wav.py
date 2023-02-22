#!/usr/bin/python

######################################################################
# About:
# indications2wav is a script designed to generate WAV files for tone
# data found in Astrisk tone configuration file, indications.conf.
# This script generates tones based on the tone definitions in the 
# configuration file, and creates a WAV file for each tone.
# The script allows for customized duration and audio sample rate for 
# the output WAV files.
######################################################################
# Author: Dimitri Pappas (https://github.com/fragtion)
# Release Date: 2023/02/22
# License: MIT
######################################################################

import os
import math
import struct
import wave
import configparser

# Path to asterisk 'indications.conf' file
config_file = "indications.conf"

# Playtime duration (in seconds) for each output wav file
duration = 10

# Audio sample rate for the output wav files (usually below 44100). Values below 4000 may not work.
# 4000 to 8000 is a good analog phone quality approximation.
sample_rate = 4000

def generate_tone(frequency, modulation_frequency, modulation_depth, sample_rate, duration):
  samples = []
  max_samples = int(sample_rate * duration)
  for i in range(max_samples):
    # calculate the instantaneous amplitude for the carrier wave
    amplitude = math.sin(2 * math.pi * frequency * i / sample_rate)
    # calculate the instantaneous amplitude for the modulating wave
    modulation_amplitude = (1 + modulation_depth * math.sin(2 * math.pi * modulation_frequency * i / sample_rate)) / 2
    # combine the amplitudes
    final_amplitude = amplitude * modulation_amplitude
    # normalize the amplitude to be within the range of a signed 16-bit integer
    final_amplitude = max(min(final_amplitude, 0.9), -0.9)  # limit to +/- 0.9
    final_amplitude *= 32767  # scale to the range of a signed 16-bit integer
    samples.append(int(final_amplitude))
  return samples

def generate_tones(filename, duration, sample_rate, output_dir):
  max_samples = duration * sample_rate
  # Parse the indications.conf file and return a dictionary of tone definitions.
  config = configparser.ConfigParser()
  config.read(filename)
  tones = {}
  for section in config.sections():
    for key, value in config.items(section):
      if key != 'description' and key != 'ringcadence':
        output_file = os.path.join(output_dir, section + "_" + key + ".wav")
        print("Creating " + output_file + "...")
        tonelist = value.split(",")
        samples = []
        s=0
        for tones in tonelist:
          samples.append([])
          # Set "tone should be played once only" to no by default
          samples[s].append(0)
          tones = tones.split("/")
          duration = (int(tones[1]) / 1000) if len(tones) > 1 else 1
          samples[s].append(duration)
          if tones[0].startswith("!"):
            #print("tones to play once: " + tones[0])
            tones[0] = tones[0][1:]
            samples[s][0] = 1
          # Check if tone should be polyphonic
          tones = tones[0].split("+")
          t=2
          for tone in tones:
            samples[s].append([])
            frequency = int(tone.split("*")[0])
            modulation_frequency = int(tone.split("*")[1] if len(tone.split("*")) > 1 else 0)
            samples[s][t] = generate_tone(frequency, modulation_frequency, 0.9, sample_rate, duration)
            t=t+1
          s=s+1
          # merge multiple tones into polyphonic tone
          if (len(samples[s-1]) > 3):
            poly = zip(*samples[0][2:])
            sample_merged = []
            for sub_samples in poly:
              sample_sum = sum(sub_samples)
              sample_avg = sample_sum / len(sub_samples)
              sample_int = int(sample_avg)
              sample_merged.append(sample_int)
            samples[s-1] = samples[s-1][:2]
            samples[s-1].append([])
            samples[s-1][2] = sample_merged;
        # merge all tones into section sequence
        samples_mux = []
        while len(samples_mux) < max_samples:
          # append tone for remainder of duration
          for sample in samples:
            if sample[0] < 2:
              samples_mux.extend(sample[2:][0])
              # Mark play-once tone as played
              if sample[0] == 1:
                sample[0] = 2
        samples_mux = samples_mux[:max_samples]
        # write the samples to a WAV file
        with wave.open(output_file, 'w') as wav_file:
          wav_file.setparams((1, 2, sample_rate, max_samples, 'NONE', 'not compressed'))
          wav_file.writeframes(struct.pack('h' * max_samples, *samples_mux))
def main():
    output_dir = "output"
    script_dir = os.path.abspath(__file__)
    output_dir = os.path.join(os.path.dirname(script_dir), output_dir)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    generate_tones(config_file, duration, sample_rate, output_dir)
    
main()
