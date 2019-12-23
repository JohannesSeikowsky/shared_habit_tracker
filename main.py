# Hbt Sys
from __future__ import print_function
import pickle, io
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.http import MediaIoBaseDownload
from datetime import datetime
from utils import *
from configs import *


def authenticate_to_drive():
	scopes = ['https://www.googleapis.com/auth/drive']

	# get credentials
	creds = None
	if os.path.exists(path_to_project + 'token.pickle'):
		with open(path_to_project + 'token.pickle', 'rb') as token:
			creds = pickle.load(token)

	# if there are no credentials available, let the user log in.
	if not creds or not creds.valid:
		if creds and creds.expired and creds.refresh_token:
			creds.refresh(Request())
		else:
			flow = InstalledAppFlow.from_client_secrets_file('credentials.json', scopes)
			creds = flow.run_local_server(port=0)
        # save the credentials for the next run
        with open(path_to_project + 'token.pickle', 'wb') as token:
        	pickle.dump(creds, token)
   	
   	# authenticate
   	drive_service = build('drive', 'v3', credentials=creds)
   	return drive_service


def download_google_doc(file_id, download_destination):
	# authenticate
	drive_service = authenticate_to_drive()
	
	# download 
	request = drive_service.files().export_media(fileId=file_id, mimeType='text/plain')
	fh = io.BytesIO()
	downloader = MediaIoBaseDownload(fh, request)
	done = False
	while done is False:
		status, done = downloader.next_chunk()

	# write download to a destination file 
	with io.open(download_destination, 'wb') as f:
		fh.seek(0)
		f.write(fh.read())


def check_doc_for_changes(file_id, download_destination):
	# authenticate
	drive_service = authenticate_to_drive()

	def read_local_file():	
		indicators = ["_", "!"]
		lines = [line for line in open(download_destination).readlines() if line[0] not in indicators]
		lines = [line[:-2] for line in lines if line.endswith("\r\n")]
		return lines

	# read "old" file, then update from google drive and read "new" version
	old_habits = read_local_file()
	download_google_doc(file_id=file_id, download_destination=download_destination)
	new_habits = read_local_file()

	# compare old and new version to see whether there are changes
	if old_habits != new_habits:
		return True, new_habits
	else:
		return False, new_habits


def change_alert(file_id, download_destination):
	# sends out an alert email if a change in the habit tracking doc has occured
	doc_changed, new_habits = check_doc_for_changes(file_id, download_destination)
	if doc_changed:
		subject = "Shared Habit Tracker - Change"
		content = "Someone has made a change in the shared habit tracker. This is the new version:\n\n"
		content = content + "\n".join(new_habits)

		for recipient in recipients:
			send_email(subject, content, recipient)


def weekly_reminder():
	# simple weekly reminder to record habits for the week
	subject = "Shared Habit Tracker - Record"
	content = "To record your habits for the week put an underscore underneath each\nrespective habit if you adhered to it and an x if you slipped."
	content = content + "\nLink: bit.ly/shared_habit_tracker"

	for recipient in recipients:
		send_email(subject, content, recipient)

# execute
run_weekly(weekly_reminder)
run_daily(change_alert, file_id, path_to_project + "habits_content.txt")