import json
import datetime

class CommonFunction:

	def get_today(self):
		create_time = datetime.datetime.now()
		create_fmt = create_time.strftime('%Y%m%d')
		return create_fmt