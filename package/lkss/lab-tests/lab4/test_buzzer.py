#!/bin/python3

import math
import struct
import argparse
import os
import subprocess
import sys

SEMITONE_CONST = 1.059463
DURATION_SCALE_FACTOR = 100
CDEV_MAJOR = 50
CDEV_MINOR = 0

# note frequency map (in hertz)
NOTE_FREQUENCIES = {
	"DO2": 65.41,
	"RE2": 73.42,
	"MI2": 82.41,
	"FA2": 87.31,
	"SOL2": 98.00,
	"LA2": 110.00,
	"SI2": 123.47,
	"DO3": 130.81,
	"RE3": 146.83,
	"MI3": 164.81,
	"FA3": 174.61,
	"SOL3": 196.00,
	"LA3": 220.00,
	"SI3": 246.94,
	"DO4": 261.63,
	"RE4": 293.66,
	"MI4": 329.63,
	"FA4": 349.23,
	"SOL4": 392,
	"LA4": 440,
	"SI4": 493.88,
	"REST": 0,
}

# note durations (in beats)
NOTE_DURATIONS = {
	"WHOLE": 4,
	"HALF": 2,
	"QUARTER": 1,
	"EIGHTH": 0.5
}

# possible alteration for a note
NOTE_ALTERATIONS = ["DOTTED", "SHARPENED", "FLATTENED"]

class BuzzerNote:
	def __init__(self, name, duration="QUARTER", alterations=[]):
		if name not in NOTE_FREQUENCIES:
			print(f"Invalid note name: {name}")
			return None

		if duration not in NOTE_DURATIONS:
			print(f"Invalid note duration: {duration}")
			return None

		self.freq = NOTE_FREQUENCIES[name]
		self.beats = NOTE_DURATIONS[duration]
		self.name = name

		self._apply_alterations(alterations)

	def _apply_alterations(self, alterations):
		for alt in alterations:
			match alt:
				case "DOTTED":
					self.beats += self.beats * 0.5
				case "SHARPENED":
					self.freq *= SEMITONE_CONST
				case "FLATTENED":
					self.freq /= SEMITONE_CONST
				case _:
					print(f"Invalid alteration: {alt}")
					return None

	def __str__(self):
		return f"Note {self.name} with {self.freq} Hz and {self.beats} beat(s)"

	def pack(self):
		# no point in scaling the frequencies ATM as their values
		# are big enough to not cause problems when casted to int
		scaled_freq = math.ceil(self.freq)

		# beats are potentiall really small so they need to be scaled
		# before being casted to int otherwise we'd end up with
		# quarter and eighth notes having the same number of beats
		scaled_beats = math.ceil(self.beats * DURATION_SCALE_FACTOR)

		return struct.pack("@II", scaled_freq, scaled_beats)

class BuzzerSong:
	CONFIG_VARIABLES=["BPM", "NAME", "COMPOSER", "ARRANGED_BY"]

	def __init__(self, filename):
		self.bpm = 0
		self.composer = "Unknown"
		self.arranged_by = "Unknown"
		self.name = "Unknown"

		print(f"Parsing sheet music at {filename}")

		self.notes = self._parse_sheet(filename)

		if self.notes is None:
			print(f"Failed to parse sheet at {filename}")
			return None

		if len(self.notes) == 0:
			print(f"No notes found in the sheet at {filename}")
			return None

		if self.bpm == 0:
			print(f"Sheet doesn't set the bpm variable")
			return None

		print(f"Song name: {self.name}")
		print(f"Composer: {self.composer}")
		print(f"Arranged by: {self.arranged_by}")
		print("Ready to play!")

	def _parse_config_line(self, line):
		if len(line) < 2:
			print(f"Invalid configuration line: {line}")
			return False

		variable = line[0]
		value = line[1]

		match variable:
			case "BPM":
				self.bpm = int(value)
			case "NAME":
				self.name = " ".join(line[1:])
			case "COMPOSER":
				self.composer = " ".join(line[1:])
			case "ARRANGED_BY":
				self.arranged_by = " ".join(line[1:])
			case _:
				print(f"Unknown variable name: {variable}")
				return False

		return True

	def _parse_sheet(self, filename):
		notes = []

		with open(filename) as fd:
			for line in fd:
				# lines starting with # are comments and thus ignored
				if line.startswith("#"):
					continue

				split_line = line.split()
			
				# empty lines are ignored	
				if len(split_line) == 0:
					continue

				if len(split_line) < 2:
					print(f"Line should contain at least the note and its duration")
					return None

				# line might define a configuration variable
				if split_line[0] in BuzzerSong.CONFIG_VARIABLES:
					if not self._parse_config_line(split_line):
						return None

					continue

				# ... it doesn't. We are dealing with a note
				note_name = split_line[0]
				duration = split_line[1]
				alterations = split_line[2:]

				# note, duration and alterations are validated during note creation
				note = BuzzerNote(note_name, duration, alterations)
				if note is None:
					return None

				notes.append(note)

		return notes

	def write_packed(self, filename):
		print("Flushing song to device")

		song = struct.pack("@II", self.bpm, len(self.notes))

		for note in self.notes:
			song += note.pack()

		with open(filename, "wb") as fd:
			fd.write(song)

	def __str__(self):
		song = ""

		# add name
		song += f"Song name: {self.name}\n"

		# add composer
		song += f"Composer: {self.composer}\n"

		# add person who arranged the sheet
		song += f"Arranged by: {self.arranged_by}\n"

		# add notes
		song += f"Sheet:\n"

		for note in self.notes:
			song += (str(note) + "\n")

		return song

parser = argparse.ArgumentParser(description="Buzzer test tool")
parser.add_argument("--sheet", "-s", type=str, help="Path to the sheet file", required=True)
parser.add_argument("--player", "-p", type=str, help="Path to the player chardev", required=True)
parser.add_argument("--major", "-m", type=int, help="Major number for the player chardev")

args = parser.parse_args()

song = BuzzerSong(args.sheet)

# create the character device for the player if it doesn't exist
if not os.path.exists(args.player):
	if args.major:
		major = args.major
	else:
		major = CDEV_MAJOR

	cmd = ["mknod", args.player, "c", str(major), str(CDEV_MINOR)]

	proc = subprocess.run(cmd)
	if proc.returncode != 0:
		print("Failed to create player character device")
		sys.exit(1)

# OK, flush to player
song.write_packed(args.player)
