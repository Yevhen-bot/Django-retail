from main.repositories.IPersonRepository import IPersonRepository
from main.models import *

class WorkerRepository(IPersonRepository):
    def get_all(self):
        return Worker.objects.all()
    
    def get_by_id(self, id):
        return Worker.objects.filter(id=id).first()
    
    def get_by_email(self, email):
        return Worker.objects.filter(email=email).first()
    
    def get_by_phone_number(self, phone_number):
        return Worker.objects.filter(phone_number=phone_number).first()

    # returns (count of ALL deleted rows, dictionary of 'name' - times deleted) 
    def delete_all(self):
        return Worker.objects.all().delete()

    def delete_by_id(self, id):
        return Worker.objects.filter(id=id).delete()[0]

    # returns created entity
    def add_one(self, first_name, last_name, email, birth_date, phone_number, store, role):
        return Worker.objects.create(
            first_name=first_name,
            last_name=last_name,
            email=email,
            birth_date=birth_date,
            phone_number=phone_number,
            store=store,
            role=role
        )
    
    # returns count of updated rows
    def update_by_id(self, id, first_name, last_name, email, birth_date, phone_number, store, role):
        w = Worker.objects.filter(id=id).first()

        if not w: return 0

        if store == 0: store = w.store
        if role == 0: role = w.role
        
        w.first_name = first_name
        w.last_name = last_name
        w.email = email
        w.birth_date = birth_date
        w.phone_number = phone_number
        if store is int:
            w.store = Store.objects.filter(id=store).first()
        else:
            w.store = store
        if role is int:
            w.role = Role.objects.filter(id=role).first()
        else:
            w.role = role

        w.save()
        return 1