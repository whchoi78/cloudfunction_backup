import json
import time

from api_sender import APISender
from base_auth_info import BaseAuthInfo
from server_valid import ValidServer

class ServerControll:

	def start_server(self, sever_name):
		server_valid = ValidServer()
		server_ids = server_valid.valid_server_status(sever_name, "NSTOP")
		if not (server_ids):
			return

		#print("server_id = " + ret[0])
		req_path = '/server/v2/startServerInstances?serverInstanceNoList.1=' + server_ids[0] + '&responseFormatType=json'. \
			format(server_ids[0])
		self.sender(req_path)
		print(">>> start_server() completed.")


	def stop_server(self, sever_name):
		server_valid = ValidServer()
		server_ids = server_valid.valid_server_status(sever_name, "RUN")
		if not (server_ids):
			return

		#print("server_id = " + ret[0])
		req_path = '/server/v2/stopServerInstances?serverInstanceNoList.1=' + server_ids[0] + '&responseFormatType=json'. \
			format(server_ids[0])
		self.sender(req_path)
		print(">>> stop_server() completed.")


	def wait_server_status(self, server_name, server_status, wait_time):

		sec = 10
		tot_time = 0

		server_valid = ValidServer()

		while(True):
			if("RUN" == server_status):
				if (False != server_valid.valid_server_status(server_name, "NSTOP")):
					self.start_server(server_name)			
				if (server_valid.valid_server_status(server_name, "RUN")):
					break;
			elif("NSTOP" == server_status):
				if (False != server_valid.valid_server_status(server_name, "RUN")):
					self.stop_server(server_name)			
				if (server_valid.valid_server_status(server_name, "NSTOP")):
					break;
			else:
				print ("Unkown server_status = " + server_status)
				return False

			time.sleep(sec)
			tot_time = tot_time + sec
			if(tot_time > wait_time):
				print ("Wait time for server state change has been exceeded. wait second = ", wait_time)
				return False

		print(">>> wait_status_server() completed.")
		return True



	def wait_status_server(self, server_name, server_status):
		server_valid = ValidServer()

		if not (server_valid.wait_for_server_status(server_name, "normal", 60 * 10)):
			return False

		if (False != server_valid.valid_server_status(server_name, "NSTOP")):
			self.start_server(server_name)
		if not (server_valid.wait_for_server_status(server_name, "RUN", 60 * 10)):
			return False
		
		print(">>> wait_start_server() completed.")
		return True




	####################         sender            ####################
	def sender(self, req_path):
		#print("req_path = " + req_path)
		base_auth_info = BaseAuthInfo()
		base_auth_info.set_req_path(req_path)
		sender = APISender(base_auth_info)
		
		response = sender.request()
		res_list = response.read()
		return json.loads(res_list.decode('utf-8'))
