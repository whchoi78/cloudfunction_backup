import json
import time

from server_image import ServerImage
from server_snapshot import ServerSnapshot
from server_ctl import ServerControll
from server_valid import ValidServer

from loadbalancer_ctl import LBControll

# valid check
def valid_action(data):
	valid_action = ['CREATE_SERVER_IMAGE', 'FORCE_CREATE_SERVER_IMAGE', 'CREATE_SERVER_SNAPSHOT', 'CREATE_STORAGE_SNAPSHOT', 'START_SERVER', 'STOP_SERVER', 'INFO_SERVER']
	ret = False
	for object in valid_action:
		if object == data:
			ret = True
			break;
	return ret

def main(event):

#	event = { "server_names" : ["fc-test-server2", "web-fctest"]	, "action": "INFO_SERVER"	}
#	event = { "server_names" : ["fc-test-server2", "web-fctest"]	, "action": "START_SERVER"	}
#	event = { "server_names" : ["fc-test-server2", "web-fctest"]	, "action": "STOP_SERVER"	}
#	event = { "server_names" : ["fc-test-server2", "web-fctest"]	, "action": "CREATE_SERVER_IMAGE"		, "max_count": 3 }
#	event = { "server_names" : ["fc-test-server2", "web-fctest"]	, "action": "CREATE_SERVER_SNAPSHOT"	, "max_count": 3 }
#	event = { "storage_ids"  : ["1302400", "1302401"]				, "action": "CREATE_STORAGE_SNAPSHOT"	, "max_count": 3 }
#	event = { "server_names" : ["web-fctest-02", "web-fctest-01"]	, "action": "FORCE_CREATE_SERVER_IMAGE"	, "max_count": 1 }
#	event = { "server_names" : ["aurora-db"], "action":"CREATE_SERVER_SNAPSHOT","max_count":1}


	action = event.get('action').upper()

	if valid_action(action) == False:
		print("Invalid Action = ", action)
		return

	if action == "START_SERVER":
		module = ServerControll()
		server_names = event.get('server_names')		
		for server_name in server_names:
			module.start_server(server_name)

	elif action == "STOP_SERVER":
		module = ServerControll()
		server_names = event.get('server_names')		
		for server_name in server_names:
			module.stop_server(server_name)

	elif action == "INFO_SERVER":
		module = ValidServer()
		server_names = event.get('server_names')
		for server_name in server_names:
			module.valid_server(server_name)

	elif action == "CREATE_SERVER_IMAGE":
		module = ServerImage()
		server_names = event.get('server_names')
		max_count = event.get('max_count')
		for server_name in server_names:
			module.create_server_image(server_name, max_count)

	elif action == "CREATE_SERVER_SNAPSHOT":
		module = ServerSnapshot()
		server_names = event.get('server_names')		
		max_count = event.get('max_count')
		for server_name in server_names:
			module.create_server_snapshot(server_name, max_count)

	elif action == "CREATE_STORAGE_SNAPSHOT":
		module = ServerSnapshot()
		storage_ids = event.get('storage_ids')
		max_count = event.get('max_count')
		for storage_id in storage_ids:
			module.create_storage_snapshot(storage_id, max_count)		
	
	elif action == "FORCE_CREATE_SERVER_IMAGE":
		module = ServerImage()
		server_names = event.get('server_names')
		max_count = event.get('max_count')
		for server_name in server_names:
			module.force_create_server_image(server_name, max_count)

	else:
		return	

	return {"result": ""}


if __name__ == '__main__':
    main(None)



