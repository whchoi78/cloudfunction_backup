import json

from api_sender import APISender
from base_auth_info import BaseAuthInfo
from common_func import CommonFunction


class LBControll:
	def insert_server_to_lb(self, lb_id, server_name):
		if not (self.valid_server_from_lb(lb_id, server_name)):
			print("Can't find");
	
	
	def delete_server_from_lb(self, lb_name, server_name):
		if (self.valid_server_from_lb(lb_id, server_name)):
			print("Find it");
	

	##### find instanc-id of LB #####
	def info_lb(self, lb_id):
		req_path = '/loadbalancer/v2/getLoadBalancerInstanceList?loadBalancerInstanceNoList.1=' + lb_id +  '&responseFormatType=json'. \
			format(lb_id)
		res = self.sender(req_path)
		count = res['getLoadBalancerInstanceListResponse']['totalRows']
		#print(">> LB Count = + ", count)
		
		if count == 1:
			return True
		
		print("Load Balancer ID = " + lb_id + " is none Exist.")
		return False


	##### find ServerName from LB #####
	def valid_server_from_lb(self, lb_id, server_name):
		req_path = '/loadbalancer/v2/getLoadBalancedServerInstanceList?loadBalancerInstanceNo=' + lb_id +  '&responseFormatType=json'. \
			format(lb_id)
		res = self.sender(req_path)
		
		ret = []
		for object in res['getLoadBalancedServerInstanceListResponse']['serverInstanceList']:
			_server_name = object['serverName']
			#print("server_name in lb = " + _server_name)

			if(server_name == _server_name):
				return True

		print("server_name = " + server_name + " is not exist in LoadBalancer.")
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