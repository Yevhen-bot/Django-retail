import os
import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "lab3.settings")
django.setup()

# from main.repositories.ClientRepository import ClientRepository
# from main.repositories.WorkerRepository import WorkerRepository
# from main.repositories.StoreRepository import StoreRepository
# from main.repositories.ItemRepository import ItemRepository
# from main.repositories.RoleRepository import RoleRepository
# from main.repositories.OperationRepository import OperationRepository
# from main.repositories.OperationHistoryRepository import OperationHistoryRepository
# from main.repositories.EstimateRepository import EstimateRepository

# srepo = StoreRepository()
# wrepo = WorkerRepository()
# ohreop = OperationHistoryRepository()
# irepo = ItemRepository()
# crepo = ClientRepository()

# print('Creating new item:')
# watches = irepo.add_one('Brand new watches', 'Rolex 5')
# print(watches)

# print('Getting a client by id:')
# client4 = crepo.get_by_id('4')
# print(client4)

# w = wrepo.get_by_id(2)
# if w is not None:
#     print(f"{w.first_name} works in {w.store.name}")

# allstores = srepo.get_all()
# from random import randint

# print(f'{client4.first_name} {client4.last_name} is buying {watches.description}')
# res = ohreop.add_one(client4, watches, OperationRepository().get_by_id(2), allstores[randint(0, len(allstores)-1)], '2020-12-12', 1000, None)
# print(res)

# if(irepo.update_by_id(watches.id, 'New desc', 'Crocodile')==1): print('Updated successfuly')
# else: print('(:')

# try:
#     irepo.delete_by_id(watches.id-1)
# except Exception as e:
#     print('Smth went wrong:', e)

from main.NetworkHelper import *
nh = NetworkHelper()
log = nh.login()
print(log)
print(nh.send(method="GET", endpoint="api/courses", sessionid=log['sessionid']))