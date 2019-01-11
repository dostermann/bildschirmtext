# -*- coding: utf-8 -*-
'''
    ████████████████████████████████████████████████
   █                                                █
  █                                                  █
 █                                                    █
 █                                                    █
 █                                                    █
 █                ████████████████████                █
 █             ██████████████████████████             █
 █           ██████████████████████████████           █
 █          ████████████████████████████████          █
 █         ███████████            ███████████         █
 █         ██████████              ██████████         █
 █         ██████████     ████     ██████████         █
 █         █████████    ████████    █████████         █
 █          ██████     ██████████     ██████          █
 █           ███   ███ ██████████ ███   ███           █
 █               █████ ██████████ █████               █
 █             ███████ ██████████ ███████             █
 █            ████████ ██████████ ████████            █
 █            ████████ ██████████ ████████            █
 █            ████████ ██████████ ████████            █
 █            █████████ ████████ █████████            █
 █            ██████████  ████  ██████████            █
 █            ████████████    ████████████            █
 █            ████████████████████████████            █
 █            ████████████████████████████            █
 █            ████████████████████████████            █
 █                                                    █
 █                                                    █
 █                                                    █
 █   ███ █ █   █        █   █                         █
 █   █ █   █   █        █              █          █   █
 █   █ █ █ █ ███ ███ ██ ███ █ ██ █████ ██ ███ █ █ ██  █
 █   ██  █ █ █ █ █   █  █ █ █ █  █ █ █ █  █ █ █ █ █   █
 █   █ █ █ █ █ █ ███ █  █ █ █ █  █ █ █ █  ███  █  █   █
 █   █ █ █ █ █ █   █ █  █ █ █ █  █ █ █ █  █   █ █ █   █
 █   ███ █ █ ███ ███ ██ █ █ █ █  █ █ █ ██ ███ █ █ ██  █
 █                                                    █
 █                                                    █
 █                                                    █
  █                                                  █
   █                                                █
    ████████████████████████████████████████████████
'''

import sys
import os
import re
import json
import time
import datetime
import pprint

from cept import Cept
from util import Util
from editor import Editor
from user import User
from user import User_UI
from messaging import Messaging
from messaging import Messaging_UI
from login import Login_UI

# paths
PATH_DATA = "data/"

user = None

# globals

last_filename_include = ""
last_filename_palette = ""
links = {}

def headerfooter(pageid, publisher_name, publisher_color):
	hide_header_footer = len(publisher_name) == 0
	hide_price = False
	# Early screenshots had a two-line publisher name with
	# the BTX logo in it for BTX-internal pages. Some .meta
	# files still reference this, but we should remove this.
	if publisher_name == "!BTX":
#		publisher_name = (
#			b'\x1b\x22\x41'                 # parallel mode
#			b'\x9b\x30\x40'                 # select palette #0
#			b'\x9e'                         # ???
#			b'\x87'                         # set fg color to #7
#			b'\x1b\x28\x20\x40'             # load DRCs into G0
#			b'\x0f'                         # G0 into left charset
#			b'\x21\x22\x23'                 # "!"#"
#			b'\n'
#			b'\r'
#			b'\x24\x25\x26'                 # "$%&"
#			b'\x0b'                         # cursor up
#			b'\x09'                         # cursor right
#			b'\x1b\x28\x40'                 # load G0 into G0
#			b'\x0f'                         # G0 into left charset
#			b'\n'
#			b'\x8d'                         # double height
#			# TODO: this does not draw!! :(
#			b'Bildschirmtext'
#		)
		publisher_name = "Bildschirmtext"
		hide_price = True
	else:
		publisher_name = publisher_name[:30]

	hf = bytearray(Cept.set_res_40_24())
	hf.extend(Cept.set_cursor(23, 1))
	hf.extend(Cept.unprotect_line())
	hf.extend(Cept.set_line_fg_color_simple(12))
	hf.extend(Cept.parallel_limited_mode())
	hf.extend(Cept.set_cursor(24, 1))
	hf.extend(Cept.unprotect_line())
	hf.extend(b' \b')
	hf.extend(Cept.clear_line())
	hf.extend(Cept.cursor_home())
	hf.extend(Cept.unprotect_line())
	hf.extend(b' \b')
	hf.extend(Cept.clear_line())
	hf.extend(Cept.serial_limited_mode())
	hf.extend(Cept.set_cursor(24, 1))
	hf.extend(Cept.set_fg_color(8))
	hf.extend(b'\b')
	hf.extend(Cept.code_9d())
	hf.extend(b'\b')

	if publisher_color < 8:
		color_string = Cept.set_fg_color(publisher_color)
	else:
		color_string = Cept.set_fg_color_simple(publisher_color - 8)

	hf.extend(color_string)

	hf.extend(Cept.set_cursor(24, 19))

	if not hide_header_footer:
		hf.extend(Cept.from_str(pageid).rjust(22))

	hf.extend(Cept.cursor_home())
	hf.extend(Cept.set_palette(1))
	hf.extend(Cept.set_fg_color(8))
	hf.extend(b'\b')
	hf.extend(Cept.code_9d())
	hf.extend(b'\b')
	
	hf.extend(color_string)

	hf.extend(b'\r')

	hf.extend(Cept.from_str(publisher_name))

	# TODO: price
	if not hide_header_footer and not hide_price:
		hf.extend(Cept.set_cursor(1, 31))
		hf.extend(b'  ')
		hf.extend(Cept.from_str(Util.format_currency(0)))

	hf.extend(Cept.cursor_home())
	hf.extend(Cept.set_palette(0))
	hf.extend(Cept.protect_line())
	hf.extend(b'\n')
	return hf

def create_preamble(basedir, meta):
	global last_filename_include
	global last_filename_palette

	preamble = b''

	# define palette
	if "palette" in meta:
		palette = meta["palette"]
		filename_palette = basedir + meta["palette"] + ".pal"
		sys.stderr.write("filename_palette = " + filename_palette + "\n")
		sys.stderr.write("last_filename_palette = " + last_filename_palette + "\n")
		if filename_palette != last_filename_palette:
			last_filename_palette = filename_palette
			with open(filename_palette) as f:
				palette = json.load(f)
			palette_data = Cept.define_palette(palette["palette"])
			preamble += palette_data
		else:
			sys.stderr.write("skipping palette\n")
	else:
		last_filename_palette = ""

	if "include" in meta:
		filename_include = basedir + meta["include"] + ".inc"
		if filename_include != last_filename_include:
			last_filename_include = filename_include
			with open(filename_include, mode='rb') as f:
				data_include = f.read()
			# palette definition has to end with 0x1f; add one if
			# the include data doesn't start with one
			if data_include[0] != 0x1f:
				preamble += Cept.set_cursor(1, 1)
			preamble += data_include
	else:
		last_filename_include = ""

	if len(preamble) > 600: # > 4 seconds @ 1200 baud
		preamble = Util.create_system_message(291) + preamble

	return preamble

def create_page(basepath, pageid):
	if pageid[-1:].isdigit():
		pageid += "a"

	basedir = None

	for i in reversed(range(0, len(pageid))):
		testdir = basepath + pageid[:i+1]
		if os.path.isdir(testdir):
			sys.stderr.write("testdir: '" + testdir + "'\n")
			filename = pageid[i+1:]
			sys.stderr.write("filename: '" + filename + "'\n")
			basedir = testdir + "/"
			break

	if basedir is None:
		return None

	ret = None
	# generated pages
	if pageid.startswith("00000") or pageid == "9a":
		# login
		ret = Login_UI.create_page(user, pageid)
	if not ret and pageid.startswith("7"):
		# user management
		ret = User_UI.create_page(user, pageid)
	if not ret and pageid.startswith("8"):
		# messaging
		ret = Messaging_UI.create_page(user, pageid)

	if ret:
		(meta, data_cept) = ret
	else:
		filename_meta = basedir + filename + ".meta"
		filename_cept = basedir + filename + ".cept"

		if not os.path.isfile(filename_meta):
			return None

		with open(filename_meta) as f:
			meta = json.load(f)
		
		with open(filename_cept, mode='rb') as f:
			data_cept = f.read()

	with open(basedir + "a.glob") as f:
		glob = json.load(f)
	meta.update(glob) # combine dicts, glob overrides meta

	all_data = bytearray(Cept.hide_cursor())

	if "clear_screen" in meta and meta["clear_screen"]:
		all_data.extend(Cept.serial_limited_mode())
		all_data.extend(Cept.clear_screen())

	all_data.extend(create_preamble(basedir, meta))

	if "cls2" in meta and meta["cls2"]:
		all_data.extend(Cept.serial_limited_mode())
		all_data.extend(Cept.clear_screen())

	# header
	hf = headerfooter(pageid, meta["publisher_name"], meta["publisher_color"])
	all_data.extend(hf)

	# payload
	all_data.extend(data_cept)

	all_data.extend(Cept.serial_limited_mode())

	# footer
	all_data.extend(hf)

	all_data.extend(Cept.sequence_end_of_page())

	inputs = meta.get("inputs")
	return (all_data, meta["links"], inputs)


def login(input_data):
	global user
	
	user = User.login(input_data["user_id"], input_data["ext"], input_data["password"])
	
	return not user is None

def validate_input(input_data, type, validate):
	if validate and validate.startswith("call:"):
		(cls, method) = validate[5:].split(".")
		module = globals()[cls]()
		func = getattr(module, method)
		return func(input_data)

	if type == "user_id":
		if User.exists(input_data["user_id"]):
			return Util.VALIDATE_INPUT_OK
		else:
			msg = Util.create_custom_system_message("Teilnehmerkennung ungültig! -> #")
			ret = Util.VALIDATE_INPUT_BAD
	elif type == "ext":
		user_id = input_data.get("user_id")
		ext = input_data["ext"]
		if ext == "":
			ext = "1"
		if User.exists(user_id, ext):
			return Util.VALIDATE_INPUT_OK
		else:
			msg = Util.create_custom_system_message("Mitbenutzernummer ungültig! -> #")
			ret = Util.VALIDATE_INPUT_BAD
	elif type == "$login_password":
		if not login(input_data):
			sys.stderr.write("login incorrect\n")
			msg = Util.create_custom_system_message("Ungültiger Teilnehmer/Kennwort -> #")
			ret = Util.VALIDATE_INPUT_RESTART
		else:
			sys.stderr.write("login ok\n")
			return Util.VALIDATE_INPUT_OK
	else:
		return Util.VALIDATE_INPUT_OK

	sys.stdout.buffer.write(msg)
	sys.stdout.flush()
	Util.wait_for_ter()
	return ret

def confirm(inputs): # "send?" message
	price = inputs.get("price", 0)
	if price > 0:
		cept_data = bytearray(Util.create_system_message(47, price))
	else:
		cept_data = bytearray(Util.create_system_message(44))
	cept_data.extend(Cept.set_cursor(24, 1))
	cept_data.extend(Cept.sequence_end_of_page())
	sys.stdout.buffer.write(cept_data)
	sys.stdout.flush()

	# TODO: use an editor for this, too!
	seen_a_one = False
	while True:
		c = Util.readchar()
		if c == "2":
			return False
			sys.stdout.write(c)
			sys.stdout.flush()
			break
		elif c == "1" and not seen_a_one:
			seen_a_one = True
			sys.stdout.write(c)
			sys.stdout.flush()
		elif c == "9" and seen_a_one:
			return True
			sys.stdout.write(c)
			sys.stdout.flush()
			break
		elif ord(c) == 8 and seen_a_one:
			seen_a_one = False
			sys.stdout.buffer.write(b'\b \b')
			sys.stdout.flush()

def system_message_sent_message():
	# "sent" message
	sys.stdout.buffer.write(Util.create_system_message(73))
	sys.stdout.flush()
	Util.wait_for_ter()

def handle_inputs(inputs):
	global user

	# create editors and draw backgrounds
	editors = []
	for input in inputs["fields"]:
		editor = Editor()
		editor.line = input["line"]
		editor.column = input["column"]
		editor.height = input["height"]
		editor.width = input["width"]
		editor.fgcolor = input.get("fgcolor")
		editor.bgcolor = input.get("bgcolor")
		editor.hint = input.get("hint")
		editor.type = input.get("type")
		editor.cursor_home = input.get("cursor_home", False)
		editor.legal_values = input.get("legal_values")
		editor.clear_line = input.get("clear_line", True)
		editor.end_on_illegal_character = input.get("end_on_illegal_character", False)
		editor.end_on_legal_string = input.get("end_on_legal_string", False)
		editor.echo_ter = input.get("echo_ter", False)
		editor.no_navigation = inputs.get("no_navigation", False)
		editor.string = input.get("default")
		editors.append(editor)
		editor.draw()

	# get all inputs
	input_data = {}
	i = 0
	skip = False
	while i < len(inputs["fields"]):
		input = inputs["fields"][i]
		editor = editors[i]

		(val, dct) = editor.edit(skip)
		if dct:
			skip = True

		if val.startswith(chr(Cept.ini())):
			return { "$command": val[1:] }

		input_data[input["name"]] = val
		
		ret = validate_input(input_data, input.get("special"), input.get("validate"))

		if ret == Util.VALIDATE_INPUT_OK:
			i += 1
		if ret == Util.VALIDATE_INPUT_BAD:
			skip = False
			continue
		elif ret == Util.VALIDATE_INPUT_RESTART:
			i = 0
			skip = False
			continue

	# confirmation
	if inputs.get("confirm", True):
		if confirm(inputs):
			if inputs.get("action") == "send_message":
				user.messaging.send(input_data["user_id"], input_data["ext"], input_data["body"])
				system_message_sent_message()
			else:
				pass # TODO we stay on the page, in the navigator?
	elif not inputs.get("no_55", False):
		cept_data = Util.create_system_message(55)
		sys.stdout.buffer.write(cept_data)
		sys.stdout.flush()

	# send "input_data" to "inputs["target"]"
		
	if "target" in inputs:
		if inputs["target"].startswith("page:"):
			return { "$command": inputs["target"][5:] }
		elif inputs["target"].startswith("call:"):
			(cls, method) = inputs["target"][5:].split(".")
			module = globals()[cls]()
			func = getattr(module, method)
			return { "$command": func(input_data) }
		else:
			return None # error
	else:
		return input_data

def wait_for_dial_command():
	s = ""
	while True:
		c = Util.readchar()
		sys.stdout.write(c)
		sys.stdout.flush()
		if ord(c) == 10 or ord(c) == 13:
			sys.stderr.write("Modem command: '" + s + "'\n")
			if re.search("^AT *(X\d)? *D", s):
				break
			s = ""
		elif ord(c) >= 0x20:
			s += c
#		sys.stderr.write("'")
#		for cc in s:
#			if ord(cc) == 10:
#				sys.stderr.write("\\r")
#			if ord(cc) == 13:
#				sys.stderr.write("\\n")
#			else:
#				sys.stderr.write(cc)
#		sys.stderr.write("'\n")

# MAIN

sys.stderr.write("Neu-Ulm running.\n")

# TODO: command line option to log in a user
# TODO: command line option to navigate to a specific page

desired_pageid = "00000" # login page
compress = False

for arg in sys.argv[1:]:
	if arg == "--modem":
		wait_for_dial_command()
	elif arg.startswith("--user="):
		user = User.login(arg[7:], "1", None, True)
	elif arg.startswith("--page="):
		desired_pageid = arg[7:]
	elif arg == "--compress":
		compress = True

current_pageid = None
page_cept_data = b''
history = []
error = 0

showing_message = False

while True:
	if user is not None:
		user.stats.update()

	if error == 0:
		add_to_history = True
	
		if desired_pageid == "":
			if len(history) < 2:
				is_back = False
				sys.stderr.write("ERROR: No history.\n")
				error = 10
			else:
				desired_pageid = history[-2]
				history = history[:-2]
	
		if desired_pageid == "09": # hard reload
			sys.stderr.write("hard reload\n")
			desired_pageid = history[-1]
			add_to_history = False
	
		if desired_pageid == "00": # re-send CEPT data of current page
			sys.stderr.write("resend\n")
			error = 0
			add_to_history = False
		elif desired_pageid:
			sys.stderr.write("showing page: '" + desired_pageid + "'\n")
			ret = create_page(PATH_DATA, desired_pageid)
	
			success = ret is not None
			if success:
				(page_cept_data, links, inputs) = ret
			error = 0 if success else 100
		else:
			error = 100

	if error == 0:
		if (compress):
			page_cept_data = Cept.compress(page_cept_data)
		sys.stdout.buffer.write(page_cept_data)
		sys.stdout.flush()
		# showing page worked
		current_pageid = desired_pageid
		if add_to_history:
			history.append(current_pageid)
	else:
		if desired_pageid:
			sys.stderr.write("ERROR: Page not found: " + desired_pageid + "\n")
			if (desired_pageid[-1] >= "b" and desired_pageid[-1] <= "z"):
				code = 101
		cept_data = Util.create_system_message(error) + Cept.sequence_end_of_page()
		sys.stdout.buffer.write(cept_data)
		sys.stdout.flush()
		showing_message = True
	
	sys.stderr.write("history: " + pprint.pformat(history) + "\n")

	desired_pageid = None

	if inputs is None:
		legal_values = list(links.keys())
		if "#" in legal_values:
			legal_values.remove("#")
		inputs = {
			"fields": [
				{
					"name": "$navigation",
					"line": 24,
					"column": 1,
					"height": 1,
					"width": 20,
					"clear_line": False,
					"legal_values": legal_values,
					"end_on_illegal_character": True,
					"end_on_legal_string": True,
					"echo_ter": True
				}
			],
			"confirm": False,
			"no_55": True
		}

	input_data = handle_inputs(inputs)

	sys.stderr.write("input_data: " + pprint.pformat(input_data) + "\n")

	error = 0
	desired_pageid = input_data.get("$command")

	if desired_pageid is None:
		val = input_data["$navigation"]
		if val in links:
			# link
			desired_pageid = links[val]
		elif not val:
			if links.get("#"):
				# #-link
				sys.stderr.write("Cept.ter")
				desired_pageid = links["#"]
			else:
				# next sub-page
				if current_pageid[-1:].isdigit():
					desired_pageid = current_pageid + "b"
				elif current_pageid[-1:] >= "a" and current_pageid[-1:] <= "y":
					desired_pageid = current_pageid[:-1] + chr(ord(current_pageid[-1:]) + 1)
				else:
					error = 101
					desired_pageid = None
		else:
			error = 100
			desired_pageid = None
			
		
		
	
