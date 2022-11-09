import json
import settings
import traceback
import requests
from wfs_client import WFSClient
from os.path import join
import logging
import logging.handlers

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


client_logger = logging.getLogger('servicer_client')
client_logger.setLevel(logging.DEBUG)

handler = logging.handlers.RotatingFileHandler('/var/log/servicer_client.log', maxBytes=4194304, backupCount=1)
handler.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

client_logger.addHandler(handler)


def redirect(hook, easydb_context, easydb_info):
    logger = client_logger
    settings = easydb_context.get_config('base.system.servicer_client')
    session = easydb_context.get_session()
    data = easydb_info.get('data')

    servicer_url = settings.get('servicer_url', "")
    
    routing_json = settings.get('routing',  '{}')
    routing = json.loads(routing_json)

    logger.debug('For ' + hook + ': ' + str(data))
    with open('/var/tmp/data.json', 'w') as out_file:
        json.dump(data, out_file)
    
    if isinstance(data, list):
        object_type = list(data[0].keys())[0]
    else:
        object_type = list(data.keys())[0]
    
    served_types = routing[hook]
    logger.debug(f'Looking for redirect for {object_type}/{hook} in {served_types}.')
    if object_type in served_types or '*' in served_types:
        full_url = join(servicer_url, hook, object_type)
        logger.info("\n".join(["Redirecting:", full_url, str(session), str(data)]))
        try:
            response = requests.post(full_url,
                                     json={'session': session, "data": data},
                                     headers={'Content-type': 'application/json'})
            
            if response.ok:
                data = response.json()['data']
                logger.debug("Servicer returned data: " + json.dumps(data, indent=2))
            else:
                logger.error("Servicer failed with: " + str(response.content))  
        except Exception as exception:
            logger.exception(exception)
    return data


def latch_db_pre_update_one(easydb_context, easydb_info):
    return redirect('db_pre_update_one', easydb_context, easydb_info)
        
def latch_db_pre_update(easydb_context, easydb_info):
    return redirect('db_pre_update', easydb_context, easydb_info)
        
def latch_db_pre_delete_one(easydb_context, easydb_info):
    return redirect('db_pre_delete_one', easydb_context, easydb_info)
        
def latch_db_pre_delete(easydb_context, easydb_info):
    return redirect('db_pre_delete', easydb_context, easydb_info)
        
def latch_db_post_update_one(easydb_context, easydb_info):
    return redirect('db_post_update_one', easydb_context, easydb_info)
        
def latch_db_post_update(easydb_context, easydb_info):
    return redirect('db_post_update', easydb_context, easydb_info)
        
def latch_db_post_delete_one(easydb_context, easydb_info):
    return redirect('db_post_delete_one', easydb_context, easydb_info)
        
def latch_db_post_delete(easydb_context, easydb_info):
    return redirect('db_post_delete', easydb_context, easydb_info)
        
def easydb_server_start(easydb_context):
    settings = easydb_context.get_config('base.system.servicer_client')
    servicer_url = settings.get('servicer_url', "")
    logger = easydb_context.get_logger('pf.server.plugin.servicer')
    if not servicer_url:
        logger.warning('No servicer url provided in base config')

    rules = settings.get('routing', '{}')
    routing = json.loads(rules)

    for hook in routing.keys():
        latch = 'latch_' + hook
        easydb_context.register_callback(hook, {'callback': latch})
        logger.info('Connected ' + hook + ' to ' + latch)

   

