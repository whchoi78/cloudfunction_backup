import json
import time

from api_sender import APISender
from base_auth_info import BaseAuthInfo
from server_valid import ValidServer
from server_ctl import ServerControll
from common_func import CommonFunction


class ServerImage:
	global WAIT_TIME
	WAIT_TIME = 600

	#서버백업처리
	def create_server_image(self, server_name, max_count):

		server_valid = ValidServer()
		server_ids = server_valid.valid_server_status(server_name, "NSTOP")
		if not (server_ids):
			return
		self.create_image(server_ids[0], server_name, max_count)
		print(">>> create_server_image() completed.")


	#서버 정지후, 서버백업처리
	def force_create_server_image(self, server_name, max_count):

		server_valid = ValidServer()
		if not (server_valid.valid_server(server_name)):			
			return

		server_ctl = ServerControll()

		if not (server_ctl.wait_server_status(server_name, "NSTOP", WAIT_TIME)):			
			return

		server_ids = server_valid.valid_server_status(server_name, "NSTOP")
		if not (server_ids):
			return

		self.create_image(server_ids[0], server_name, max_count)

		if not (server_ctl.wait_server_status(server_name, "RUN", WAIT_TIME)):
			return

		print(">>> force_create_server_image() completed.")



	# create server image
	def create_image(self, server_id, server_name, max_count):
		#checking server image status
		if self.get_server_image_status(server_name, "INIT"):
			print("Image of " + server_name + " is being created.")
			return False

		#counting server image
		ret = self.count_server_image(server_name)

		#delete server image
		if len(ret) >= max_count:
			del_count = len(ret) - max_count + 1
			for object in ret:
				#print("del no = " + object)
				self.req_delete_server_image(object)
				del_count = del_count - 1
				if del_count < 1:
					break

		#get server image name
		image_name = self.get_server_image_unique_name(server_name)
		#create server image
		self.req_create_server_image(server_id, server_name, image_name)

		return True



	##### get server image name #####
	# memberServerImageName >> Max Length 30 character
	# server_name(18) + datetime(9) + seq_number(3)

	def get_server_image_unique_name(self, server_name):
		common_func = CommonFunction()
		if len(server_name) > 18:
			server_name = server_name[0:18]

		org_image_name = server_name + '-' + common_func.get_today()
		image_name = org_image_name

		seq_number = 0
		while(True):
			if self.get_server_image_name(server_name, image_name):
				seq_number = seq_number + 1
				image_name = org_image_name + '-' + str(seq_number)
			else:
				break

		return image_name
	

	##### find server image name #####
	def get_server_image_name(self, server_name, image_name):		
		req_path = '/server/v2/getMemberServerImageList?responseFormatType=json'. \
			format(server_name)
		res = self.sender(req_path)

		for object in res['getMemberServerImageListResponse']['memberServerImageList']:
			if object['memberServerImageName'] == image_name:
				return True
		return False


	##### find server image status #####
	def get_server_image_status(self, server_name, status):		
		req_path = '/server/v2/getMemberServerImageList?responseFormatType=json'. \
			format(server_name)
		res = self.sender(req_path)

		for object in res['getMemberServerImageListResponse']['memberServerImageList']:
			if server_name == object['originalServerName'] and object['memberServerImageStatus']['code'] == status:
					return True
		return False


	
	##### counting server image #####
	def count_server_image(self, server_name):		
		#req_path = '/server/v2/getMemberServerImageList?sortedBy=memberServerImageNo&sortingOrder=ascending&responseFormatType=json'. \
		req_path = '/server/v2/getMemberServerImageList?responseFormatType=json'. \
			format(server_name)
		res = self.sender(req_path)

		orderArr = {}
		sortedArr = []
		for object in res['getMemberServerImageListResponse']['memberServerImageList']:
			if server_name == object['originalServerName']:
				str = object['createDate']
				key = str[0:4] + str[5:7] + str[8:10] + str[11:13] + str[14:16] + str[17:19]
				#print("create time = " + key)
				orderArr[key] = object['memberServerImageNo']
			
		if len(orderArr) > 0:
			sortedArr = sorted(orderArr.items())
        
		ret = []
		for object in sortedArr:
			#print("memberServerImageNo = " + object[1])
			ret.append(object[1])

		return ret



	######  create server image #####
	def req_create_server_image(self, server_ids, server_name, image_name):		
		req_path = '/server/v2/createMemberServerImage?serverInstanceNo=' + server_ids \
					+ '&memberServerImageName=' + image_name \
					+ '&memberServerImageDescription=' + server_name + '_AutoBackup_by_CloudFunction' \
					+ '&responseFormatType=json'. \
			format(server_name)
		self.sender(req_path)


	######  delete server image #####
	def req_delete_server_image(self, server_name):		
		req_path = '/server/v2/deleteMemberServerImages?memberServerImageNoList.1=' + server_name + '&responseFormatType=json'. \
			format(server_name)
		self.sender(req_path)



	####################         sender            ####################	
	def sender(self, req_path):
		#print("req_path = " + req_path)
		base_auth_info = BaseAuthInfo()
		base_auth_info.set_req_path(req_path)
		sender = APISender(base_auth_info)
		
		response = sender.request()
		res_list = response.read()
		return json.loads(res_list.decode('utf-8'))