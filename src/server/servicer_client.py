import json
import settings
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
    def __init__(self, url, routing={}, logger=None):
        self.url = url
        self.routing = routing
        self.logger = logger
        self.logger.info('Instanciated client')
    
    def add_latch(self, hook):
        def hook_method(self, easydb_context, easydb_info):
            return self.redirect(hook, easydb_context, easydb_info)
        setattr(self, hook, hook_method)
        self.logger.info(f'Latched onto {hook}.')

    def redirect(self, hook, easydb_context, easydb_info):
        session = easydb_context.get_session()
        data = easydb_info.get('data')
        object_type = next(data.keys())
        served_types = self.routing[hook]
        self.logger.debug(f'Looking for redirect for {object_type} in {hook}.')
        if object_type in served_types or '*' in served_types:
            full_url = join(self.url, hook, object_type)
            try:
                self.logger.info("\n".join(["Redirecting:", full_url, str(session), str(data)]))

                response = requests.post(full_url,
                                        json={'session': session, "data": data},
                                        headers={'Content-type': 'application/json'})
                
                if response.ok:
                    data = response.json()['data']
                    self.logger.debug("Servicer returned data: " + json.dumps(data, indent=2))
                else:
                    self.logger.error("Servicer failed with: " + str(response.content))  
            except Exception as exception:
                self.logger.error(str(exception))
            
        return data

def easydb_server_start(easydb_context):
    settings = easydb_context.get_config('base.system.servicer_client')
    servicer_url = settings.get('servicer_url', "")
    logger = easydb_context.get_logger('pf.server.plugin.servicer')
    if not servicer_url:
        logger.warning('No servicer url provided in base config')
    

    routing = settings.get('routing', False)
    if not routing:
        routing = '{}'
    routing = json.loads(routing)

    client = ServicerClient(servicer_url, routing, logger)

    for hook in routing.keys():
        client.add_latch(hook)
        easydb_context.register_callback('hook', {'callback': 'client.' + hook})

   

