# utils
from datetime import datetime, date
import smtplib
import configs


def send_email(subject, content, target):
	my_address = "joseikowsky@gmail.com"
	mail = smtplib.SMTP("smtp.gmail.com", 587)
	mail.ehlo()
	mail.starttls()
	mail.login(my_address, configs.pw)

	from_address = my_address
	to_address = target

	email_content = "Subject:{}\n\n{}".format(subject, content)
	mail.sendmail(from_address, to_address, email_content)
	mail.close()


## replace path_to_project
def get_done_dates():
	done_dates = open(path_to_project + "done_dates.txt").read().splitlines()
	return done_dates


def add_done_date(date):
	done_dates = open(path_to_project + "done_dates.txt", "a").write(date + "\n")


def run_weekly(func):
	# run function after a certain time on a certain weekday (Sundays in this case)
	# only if it hasn't been run yet today
	today = datetime.today().strftime('%d.%m')
	current_weekday = date.today().weekday()
	current_hour = datetime.now().hour
	done_dates = get_done_dates()

	if today not in done_dates and current_weekday == 6 and current_hour >= 11:
		func()
	else:
		pass


def run_daily(func, arg1, arg2):
	""" Ensures that the pass in function only gets run once a day after a specified time. 
	Necessary in our case because can't set Cronjob to a specified time as machine maybe off 
	at that time. Hence have to run the job in intervals and want to avoid repeat-executions."""
	today = datetime.today().strftime('%d.%m')
	current_hour = datetime.now().hour

	done_dates = get_done_dates()
	if today not in done_dates and current_hour >= 11:
		func(arg1, arg2)
		add_done_date(today)
	else:
		pass