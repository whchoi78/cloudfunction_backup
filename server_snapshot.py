import json
import time

from api_sender import APISender
from base_auth_info import BaseAuthInfo
from server_valid import ValidServer
from common_func import CommonFunction

class ServerSnapshot:
	##### create server snapshot #####
	def create_server_snapshot(self, server_name, max_count):

		server_valid = ValidServer()
		server_ids = server_valid.valid_server_normal_status(server_name)
		if len(server_ids) < 1:
			return

		#find server storage list
		storage_list = self.get_server_storage_list(server_name, server_ids[0])
		if len(storage_list) < 1:
			return

		#counting storage snapshot
		for object in storage_list:
			if(server_valid.wait_for_server_status(server_name, "normal", 60 * 10)):
				self.create_storage_snapshot(object, max_count)
			else:
				print("wait_for_server_normal_status() is fail. A long time has elapsed.")
				return

		print(">>> create_server_snapshot() completed.")


	##### create storage snapshot by storage_id #####
	def create_storage_snapshot(self, storage_id, max_count):
		storage_name = self.get_storage(storage_id)
		if storage_name == "NULL":
			print("storage_id = " + storage_id + " can't find it.")
			return
		self.create_snapshot(storage_name, storage_id, max_count)

	
	def create_snapshot(self, storage_name, storage_id, max_count):

		ret = self.req_count_storage_snapshot(storage_id)

		#delete storage snapshot
		if len(ret) >= max_count:
			del_count = len(ret) - max_count + 1
			for snapshot_id in ret:
				#print("del list = " + snapshot_id)
				self.req_delete_storage_snapshot(snapshot_id)
				del_count = del_count - 1
				if del_count < 1:
					break


		#create storage snapshot
		#blockStorageSnapshotName >> Max Length 30 character
		#storage_name(18) + datetime(9) + seq_number(3)
		common_func = CommonFunction()
		if len(storage_name) > 18:
			storage_name = storage_name[0:18]

		org_snapshot_name = storage_name + '-' + common_func.get_today()
		snapshot_name = org_snapshot_name

		seq_number = 0
		while(True):
			if self.get_storage_snapshot_name(storage_id, snapshot_name):
				seq_number = seq_number + 1
				snapshot_name = org_snapshot_name + '-' + str(seq_number)
			else:
				break

		#print("storage snapshot, storage_id = " + storage_id)
		req_path = '/server/v2/createBlockStorageSnapshotInstance?blockStorageInstanceNo=' + storage_id \
					+ '&blockStorageSnapshotName=' + snapshot_name \
					+ '&blockStorageSnapshotDescription=' + storage_name + '_AutoBackup_by_CloudFunction' \
					+ '&responseFormatType=json'. \
			format(storage_id)
		self.sender(req_path)

		print(">>> create_snapshot() completed.")

	
	##### find storage snapshot name #####
	def get_storage_snapshot_name(self, storage_id, snapshot_name):
		req_path = '/server/v2/getBlockStorageSnapshotInstanceList?originalBlockStorageInstanceNoList.1=' + storage_id + '&responseFormatType=json'. \
			format(storage_id)
		res = self.sender(req_path)		

		for object in res['getBlockStorageSnapshotInstanceListResponse']['blockStorageSnapshotInstanceList']:
			if object['blockStorageSnapshotName'] == snapshot_name:
				return True
		return False



	##### counting storage snapshot #####
	def req_count_storage_snapshot(self, storage_id):
		req_path = '/server/v2/getBlockStorageSnapshotInstanceList?originalBlockStorageInstanceNoList.1=' + storage_id + '&responseFormatType=json'. \
			format(storage_id)
		res = self.sender(req_path)		

		orderArr = {}
		sortedArr = []
		for object in res['getBlockStorageSnapshotInstanceListResponse']['blockStorageSnapshotInstanceList']:
			str = object['createDate']
			key = str[0:4] + str[5:7] + str[8:10] + str[11:13] + str[14:16] + str[17:19]
			#print("create time = " + key + ", no = " + object['blockStorageSnapshotInstanceNo'])
			orderArr[key] = object['blockStorageSnapshotInstanceNo']

		if len(orderArr) > 0:
			sortedArr = sorted(orderArr.items())
        
		ret = []
		for object in sortedArr:
			#print("memberServerImageNo = " + object[1])
			ret.append(object[1])  

		return ret





	#####  delete storage snapshot #####
	def req_delete_storage_snapshot(self, snapshot_id):		
		req_path = '/server/v2/deleteBlockStorageSnapshotInstances?blockStorageSnapshotInstanceNoList.1=' + snapshot_id + '&responseFormatType=json'. \
			format(snapshot_id)
		self.sender(req_path)




	##### find server storage list #####
	def get_server_storage_list(self, server_name, sever_id):
		req_path = '/server/v2/getBlockStorageInstanceList?serverInstanceNo=' + sever_id + '&responseFormatType=json'. \
			format(sever_id)
		res = self.sender(req_path)

		ret = []
		count = res['getBlockStorageInstanceListResponse']['totalRows']
		if count > 1:
			for object in res['getBlockStorageInstanceListResponse']['blockStorageInstanceList']:
				#print("devicename = " + object['deviceName'])
				#print("deviceID   = " + object['blockStorageInstanceNo'])
				device_name = object['deviceName']
				if device_name == '/dev/xvda' or device_name == 'Disk 0':
					continue
				else:
					#print("device_name = " + device_name + ", ID = " + object['blockStorageInstanceNo'])
					ret.append(object['blockStorageInstanceNo'])			
		else:
			print("server_name = " + server_name + ", server_id = " + sever_id + ", can't find storage.")

		return ret



	##### find storage name #####
	def get_storage(self, storage_id):
		req_path = '/server/v2/getBlockStorageInstanceList?blockStorageInstanceNoList.1=' + storage_id + '&responseFormatType=json'. \
			format(storage_id)
		res = self.sender(req_path)

		ret = "NULL"
		count = res['getBlockStorageInstanceListResponse']['totalRows']
		if count == 1:
			for object in res['getBlockStorageInstanceListResponse']['blockStorageInstanceList']:
				ret = object['blockStorageName']
				print("storage_name = " + ret)
		
		return ret




	####################         sender            ####################	
	def sender(self, req_path):
		#print("req_path = " + req_path)
		base_auth_info = BaseAuthInfo()
		base_auth_info.set_req_path(req_path)
		sender = APISender(base_auth_info)
		
		response = sender.request()
		res_list = response.read()
		return json.loads(res_list.decode('utf-8'))