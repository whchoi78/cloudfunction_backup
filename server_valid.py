import json
import time

from api_sender import APISender
from base_auth_info import BaseAuthInfo

class ValidServer:
	def valid_server_status(self, server_name, status_code):
		req_path = '/server/v2/getServerInstanceList?searchFilterName=serverName&searchFilterValue=' + server_name + '&serverInstanceStatusCode=' + status_code + '&responseFormatType=json'. \
			format(server_name)
		res = self.sender(req_path)		

		#like 검색 결과이므로, for 문을 통한 정확한 이름 검색 필요
		#count = res['getServerInstanceListResponse']['totalRows']
		#if count == 1:
		ret = []
		for object in res['getServerInstanceListResponse']['serverInstanceList']:
			#print("servername = " +  object['serverName'] + ", server no = " + object['serverInstanceNo'])
			if server_name == object['serverName']:
				ret.append(object['serverInstanceNo'])		

		if len(ret) < 1:
			#print("server_name = " + server_name + ", status = " + status_code + " can't find Server")
			return False

		return ret


	def valid_server_normal_status(self, server_name):
		req_path = '/server/v2/getServerInstanceList?searchFilterName=serverName&searchFilterValue=' + server_name + '&responseFormatType=json'. \
			format(server_name)
		res = self.sender(req_path)		

		ret = []
		for object in res['getServerInstanceListResponse']['serverInstanceList']:
			if server_name == object['serverName']:
				status = object['serverInstanceStatus']['code']
				#print("status  = " + status )				
				if status == "RUN" or status == "NSTOP":
					ret.append(object['serverInstanceNo'])	
		
		if len(ret) < 1:
			#print("server_name = " + server_name + " is none Exist. or Server status is not RUN or STOP")
			return False
		return ret


	def valid_server(self, server_name):
		req_path = '/server/v2/getServerInstanceList?searchFilterName=serverName&searchFilterValue=' + server_name + '&responseFormatType=json'. \
			format(server_name)
		res = self.sender(req_path)		

		ret = []
		for object in res['getServerInstanceListResponse']['serverInstanceList']:
			if server_name == object['serverName']:
				ret.append(object)
		
		if len(ret) < 1:
			print("server_name = " + server_name + " is none Exist.")
			return False

		#print(">> server infomation <<")
		#print(ret)
		return True


	def wait_for_server_status(self, server_name, server_status, wait_time):
		sec = 10
		tot_time = 0
	
		while(True):
			if("normal" == server_status):
				ret = self.valid_server_normal_status(server_name)
			elif ("RUN" == server_status or "NSTOP" == server_status):
				ret = self.valid_server_status(server_name, server_status)
			else:
				print ("Wrong parameter server_status = " + server_status)
				return False
				
			#print("wait_for_server_status count = ", len(ret))

			if (False != ret):
				return True

			time.sleep(sec)
			tot_time = tot_time + sec
			
			if(tot_time > wait_time):
				print ("Wait time for server state change has been exceeded. wait second = ", wait_time)
				return False




	####################         sender            ####################	
	def sender(self, req_path):
		#print("req_path = " + req_path)
		base_auth_info = BaseAuthInfo()
		base_auth_info.set_req_path(req_path)
		sender = APISender(base_auth_info)
		
		response = sender.request()
		res_list = response.read()
		return json.loads(res_list.decode('utf-8'))