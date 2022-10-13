import json
import settings
import logging
import traceback
import requests
from wfs_client import WFSClient
from os.path import join
"""This is modelled after https://docs.easydb.de/en/technical/plugins/
section "Example (Server Callback)
"""

DATABASE_CALLBACKS = ['db_pre_update_one',
                      'db_pre_update',
                      'db_pre_delete_one',
                      'db_pre_delete',
                      'db_post_update_one',
                      'db_post_update',
                      'db_post_delete_one',
                      'db_post_delete']

class ServicerClient:
    def __init__(self, url):
        if url.startswith('http'):
            self.url = url
        else:
            raise ValueError('Protocol information required in servicer url (e.g. "http:...")')
        populated_hooks = settings.ROUTING.keys()
        for hook in populated_hooks:
            def hook_method(self, easydb_context, easydb_info):
                return self.redirect(hook, easydb_context, easydb_info)
            setattr(self, hook, hook_method)     
    
    def redirect(self, hook, easydb_context, easydb_info):
        session = easydb_context.get_session()
        data = easydb_info.get('data')
        object_type = next(data.keys())
        served_types = settings.ROUTING[hook]
        
        if {object_type, '*'}.intersection(served_types):
            full_url = join(self.url, hook, object_type)
            try:
                logging.info("\n".join(["Redirecting:", full_url, str(session), str(data)]))

                response = requests.post(full_url,
                                        json={'session': session, "data": data},
                                        headers={'Content-type': 'application/json'})
                
                if response.ok:
                    data = response.json()['data']
                    logging.debug("Servicer returned data: " + json.dumps(data, indent=2))
                else:
                    logging.error("Servicer failed with: " + str(response.content))  
            except Exception as exception:
                logging.error(str(exception))
            
        return data


client = ServicerClient(settings.SERVICER_URL)

def easydb_server_start(easydb_context):
    routing = easydb_context.get_config('base')
    raise ValueError('base_config: ' + json.dumps(routing))
    for hook in settings.ROUTING.keys():
        easydb_context.register_callback('hook', {'callback': 'client.' + hook})
   
    logging.basicConfig(filename="/var/tmp/plugin.log", level=logging.DEBUG)
    logging.info("Loaded plugin")

