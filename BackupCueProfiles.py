#
#      CORSAIR UTILITY ENGINE
#       Sam's Backup Engine
#   (please fix your software)
#
# Copyright Sam Cross (c) 2016 - Licensed under the MIT License. See LICENSE.md.

sbe_version_short = '1.1'

# Imports
import sys
if (sys.version_info[0] < 3):
	print('WARNING: SBE hasn\'t been tested on versions of Python under 3.x. If you discover a bug, please create an Issue on GitHub.')
	import Tkinter as tk
	from pathlib2 import Path
else:
	import tkinter as tk
	from pathlib import Path
import os, platform
import shutil, glob
from datetime import datetime

try:
	if(os.environ['PY_SBE_DEBUG'] == 'true'):
		print('WARNING: SBE is running in DEBUG mode. Your CUE files will NOT be changed, however backups can still be created. \
		To run in normal mode, change the environment variable "PY_SBE_DEBUG" to something OTHER than "true".')
		sbe_running_in_debug_mode = True
	else:
		sbe_running_in_debug_mode = False
except:
	sbe_running_in_debug_mode = False

def swap_debug_mode():
	global sbe_running_in_debug_mode
	if sbe_running_in_debug_mode:
		sbe_running_in_debug_mode = False
	else:
		sbe_running_in_debug_mode = True

# Check if we're running on a Windows machine
if (platform.system() != 'Windows'):
	print('SBE only supports systems running Windows Vista and above.')
	exit()

# Check and return what architecture we're running on
def check_platform_architecture():
	if (platform.machine() == 'AMD64'):
		print('running 64bit')
		return 64
	elif (platform.machine() == 'i386'):
		print('running 32bit')
		return 32
	else:
		print('Couldn\'t determine your system architecture. SBE only supports 32 and 64-bit systems.')
		exit()

# Set variables
if (check_platform_architecture() == 64):
	cue_install_dir = 'C:\\Program Files (x86)\\Corsair\\Corsair Utility Engine\\'
else:
	cue_install_dir = 'C:\\Program Files\\Corsair\\Corsair Utility Engine\\'
cue_install_exe = 'CUE.exe'
cue_data_dir    = os.environ['APPDATA'] + '\\Corsair\\CUE\\'
cue_backup_dir	= os.environ['USERPROFILE'] + '\\Documents\\Corsair\\CUE\\Backups\\'

class sbe_datetime():
	def date_string(separator):
		date_time_full = datetime.now()
		return str(date_time_full.year) + separator + str(date_time_full.month) + separator + str(date_time_full.day)

	def time_string(separator):
		date_time_full = datetime.now()
		return str(date_time_full.hour) + separator + str(date_time_full.minute)

class sbe_utility():
	def remove_special_characters(text):
		'''
		Remove any characters that aren't allowed in file names.
		'''
		return ''.join([char for char in text if char.isalpha() or char.isdigit() or char==' ' or char=='-' or char=='_']).rstrip()

	def limit_length(text):
		'''
		Check if text is longer than 40 characters, and shorten it if needed.
		'''
		if (len(text) > 40):
			return text[0:39]
		else:
			return text

	def del_dir(dir):
		'''
		Delete a directory, its sub-directories and files.

		@params
		dir:	Directory to be deleted.
		@returns
		-1:		Failed
		0:		Succeeded
		'''

		try:
			shutil.rmtree(dir)
			print('INFO: Deleted directory: ' + dir)
			return 0
		except OSError as e: # todo: check & fix if necessary
			print('ERROR: An error occurred in del_dir(' + dir + ').' + str(e))
			return -1

	def copy_dir(dir, out):
		'''
		Copy a directory, its sub-directories and files.

		@params
		dir:	Full path of the directory to be copied.
		out:	The directory to copy to (including the copied directory name).
		@returns
		-1:		Failed
		0:		Succeeded
		'''

		if (Path(out).exists()):
			print('The path "' + out + '" already exists.')
			return -1
		else:
			#os.mkdir(out) # create dir
			shutil.copytree(dir, out)
			return 0

	def end_process(name): # todo: make this work
		'''
		Check if a process is running, and if so, kill it.

		@returns
		-1:		Failed
		0:		Succeeded
		1:		Wasn't running anyway
		'''
		return -1

	#	tlcall = 'TASKLIST', '/FI', 'imagename eq %s' % processname
	#	# shell=True hides the shell window, stdout to PIPE enables
	#	# communicate() to get the tasklist command result
	#	tlproc = subprocess.Popen(tlcall, shell=True, stdout=subprocess.PIPE)
	#	# trimming it to the actual lines with information
	#	tlout = tlproc.communicate()[0].strip().split('\r\n')
	#	# if TASKLIST returns single line without processname: it's not running
	#	if len(tlout) > 1 and processname in tlout[-1]:
	#		print('process "%s" is running!' % processname)
	#		return True
	#	else:
	#		print(tlout[0])
	#		print('process "%s" is NOT running!' % processname)
	#		return False

	def is_directory(path):
		# todo: add
		return

	def list_dir(path):
		#return next(os.path.join(path, os.walk('.')))[1]
		# todo: add check to see if each is an actual folder, and if it is a valid backup
		return os.listdir(path)

	def check_if_valid_backup(file):
		'''
		Check if a folder is a valid SBE backup.

		@params
		file: File to check
		@returns
		-1: Invalid
		0:	Valid
		'''
		# todo: check & fix if necessary
		if (os.path.exists(os.path.join(file, 'Corsair\\')) and os.path.exists(os.path.join(file, 'config.cuecfg'))):
			return 0
		else:
			return -1

	def if_not_empty_then_restore(obj, arg):
		'''
		Check if obj is empty or non-existent, and run callback if it isn't.
		'''
		if (obj):
			sbe_function.restore_named(arg)

class sbe_function():
	def backup_named(name):
		'''
		Create a new backup, and name it with the 'name' parameter.
		
		@returns
		-1:		Failed
		0:		Succeeded
		'''
		path = os.path.join(cue_backup_dir, sbe_utility.limit_length(sbe_utility.remove_special_characters(name)))

		if sbe_running_in_debug_mode:
			print('Backup would\'ve been created at: ' + path)
			return 0
		else:
			return sbe_utility.copy_dir(cue_data_dir, path)

	def restore_named(name):
		'''
		Restore settings from a backup.

		WARNING: THIS WILL NOT KILL CUE BEFORE RUNNING. MAKE SURE CUE IS KILLED BEFORE YOU RUN THIS METHOD.

		@returns
		-1: failure
		0: Success
		'''

		if sbe_running_in_debug_mode:
			print('Restore would\'ve started, however SBE is running in DEBUG mode. See console/log for more info.')
			return 0
		else:
			# End CUE.exe, if it's running /todo: doesn't work yet.
			#sbe_utility.end_process('CUE.exe')
			# Delete the old data
			sbe_utility.del_dir(cue_data_dir)
			# Write the backup
			return sbe_utility.copy_dir(os.path.join(cue_backup_dir, name), cue_data_dir)

##
##
##	GUI
##
##

# class colours():
# 	def __init__(self):
#		
# 	def is_active(el):
# 		if (el == self.active):
# 			return "#303030"
# 		else:
# 			return "#202020"

class Navbar(tk.Frame):
	def __init__(self, parent):
		tk.Frame.__init__(self, parent)
		self.parent = parent

		self.configure(background="#202020")

		self.gui_buttonlarge_backup = tk.Button(self, height=3, width=33, bd=0, bg="#202020", fg="white", \
			activebackground="#323232", activeforeground="white", text='Backup', command=lambda: parent.main.show_backup())
		self.gui_buttonlarge_backup.grid(row=1, column=0)

		self.gui_buttonlarge_restore = tk.Button(self, height=3, width=33, bd=0, bg="#202020", fg="white", \
			activebackground="#323232", activeforeground="white", text='Restore', command=lambda: parent.main.show_restore())
		self.gui_buttonlarge_restore.grid(row=1, column=1)

		self.gui_buttonlarge_options = tk.Button(self, height=3, width=33, bd=0, bg="#202020", fg="white", \
			activebackground="#323232", activeforeground="white", text='Options', command=lambda: parent.main.show_options())
		self.gui_buttonlarge_options.grid(row=1, column=2)
class Statusbar(tk.Frame):
	def __init__(self, parent):
		tk.Frame.__init__(self, parent)
		self.parent = parent

		self.status = tk.StringVar()
		self.gui_statusbar_label = tk.Label(self, width=102, bd=0, bg="#202020", fg="#cccccc", textvariable=self.status)
		self.gui_statusbar_label.pack(side="left", fill="x")
	def set_status(self, status):
		self.status.set(status)
		print('Status: ' + status)
	def clear_status(self):
		self.status.set('')
		print('Successfully doing nothing.')
class Main(tk.Frame):
	def __init__(self, parent):
		tk.Frame.__init__(self, parent)
		self.parent = parent

		#self.configure(background="#303030")

		self.title_label_text = tk.StringVar()
		self.gui_main_title_label = tk.Label(self, textvariable=self.title_label_text, font=("Helvetica", 14), pady=6)
		self.gui_main_title_label.pack(side="top")

		self.show_backup() # Show backup page on startup
	def hide_everything(self):
		for el in self.winfo_children():
			if el != self.gui_main_title_label:
				el.destroy()

	def show_backup(self):
		self.hide_everything()
		self.parent.navbar.gui_buttonlarge_backup['state']  = 'disabled'
		self.parent.navbar.gui_buttonlarge_restore['state'] = 'normal'
		self.parent.navbar.gui_buttonlarge_options['state'] = 'normal'

		self.parent.statusbar.clear_status()
		self.title_label_text.set('Backup')

		self.gui_backup_label = tk.Label(self, text='Create a new backup.')
		self.gui_backup_label.pack(side="top")
		self.gui_textbox_backup_name_label = tk.Label(self, text='Name your backup:')
		self.gui_textbox_backup_name_label.pack(side="top")
		self.gui_textbox_backup_name = tk.Entry(self, width=60)
		self.gui_textbox_backup_name.insert(0, 'CUEBackup-' + sbe_datetime.date_string('-') + '-' + sbe_datetime.time_string('-'))
		self.gui_textbox_backup_name.pack(side="top")
		self.gui_button_backup = tk.Button(self, text='Backup', command=lambda: self.backup_start(self.parent.statusbar, self.gui_textbox_backup_name.get()))
		self.gui_button_backup.pack(side="top")

	# todo: find a more elegant way of implementing this and changing the statusbar's text
	def backup_start(self, sb, name):
		sb.set_status('Copying files...')
		if (sbe_function.backup_named(name) == 0):
			sb.set_status('Completed successfully! Located at "' + \
				str(os.path.join(cue_backup_dir, sbe_utility.limit_length(sbe_utility.remove_special_characters(name)))) + '".')
		else:
			sb.set_status('Backup failed, for some reason. Check console/logs for more info.')

	def show_restore(self):
		self.hide_everything()
		self.parent.navbar.gui_buttonlarge_backup['state']  = 'normal'
		self.parent.navbar.gui_buttonlarge_restore['state'] = 'disabled'
		self.parent.navbar.gui_buttonlarge_options['state'] = 'normal'

		self.parent.statusbar.set_status('Loading backups...')
		self.title_label_text.set('Restore')

		self.gui_backups_list = tk.Listbox(self, exportselection=0, width=80)
		self.gui_backups_list.pack()

		for d in sbe_utility.list_dir(cue_backup_dir):
			self.gui_backups_list.insert(tk.END, d)

		self.parent.statusbar.clear_status()

		# If we're running in debug mode, tell the user that SBE won't touch their settings.
		if sbe_running_in_debug_mode:
			self.parent.statusbar.set_status('SBE is running in DEBUG mode. Your settings won\'t be touched, see console/log for more info.')

		# todo: tidy
		self.gui_button_restore = tk.Button(self, text='Restore', \
			command=lambda: self.restore_selection_callback(self.gui_backups_list.curselection()))
		self.gui_button_restore.pack(side="top")
	def restore_selection_callback(self, list_sel):
		items = list(map(int, list_sel))
		if(len(items) > 0):
			# something was selected /todo: tidy
			print('Info: "' + sbe_utility.list_dir(cue_backup_dir)[items[0]] + '" was selected.')
			self.parent.statusbar.set_status('Restoring from "' + sbe_utility.list_dir(cue_backup_dir)[items[0]] + '"...')
			if sbe_function.restore_named(sbe_utility.list_dir(cue_backup_dir)[items[0]]) == 0:
				self.parent.statusbar.set_status('Restoration successful.')
		else:
			self.parent.statusbar.set_status('You should probably select a backup first.')
			print('Warning: Nothing was selected, so doing nothing.')

	def show_options(self):
		self.hide_everything()
		self.parent.navbar.gui_buttonlarge_backup['state']  = 'normal'
		self.parent.navbar.gui_buttonlarge_restore['state'] = 'normal'
		self.parent.navbar.gui_buttonlarge_options['state'] = 'disabled'

		self.parent.statusbar.clear_status()
		self.title_label_text.set('Options')

		self.gui_option_none_label = tk.Label(self, text='SBE doesn\'t have any options yet, but we\'re working on it.')
		self.gui_option_none_label.pack(side="top")

		# todo: add switch for debug mode
		#self.gui_option_change_debug_mode_label_var = tk.StringVar()
		#self.gui_option_change_debug_mode_label = tk.Button(self, textvariable=gui_option_change_debug_mode_label_var, command=lambda: swap_debug_mode())
		#self.gui_option_change_debug_mode_label.pack(side="top")
		#if (sbe_running_in_debug_mode):
		#	self.gui_option_change_debug_mode_label_var.set('Turn DEBUG mode off.')

class App(tk.Frame):
	def __init__(self, parent, *args, **kwargs):
		tk.Frame.__init__(self, parent, *args, **kwargs)
		self.statusbar  = Statusbar(self)
		self.navbar     = Navbar(self)
		self.main       = Main(self)

		self.navbar.pack(side="top", fill="x")
		self.statusbar.pack(side="bottom", fill="x")
		self.main.pack(side="left", fill="both", expand=True)

if __name__ == "__main__":
	root = tk.Tk()
	root.minsize(width=640, height=480)
	root.resizable(width=False, height=False)
	root.title('SBE for CUE ' + sbe_version_short)

	App(root).pack(side="top", fill="both", expand=True)
	root.mainloop()
