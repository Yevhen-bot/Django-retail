from django import forms
from main.models import Worker, Store

class WorkerForm(forms.ModelForm):
    class Meta:
        model = Worker
        fields = "__all__"

    id = forms.IntegerField(required=False)
    store = forms.IntegerField(label="Store ID")


    def clean_store(self):
        store_id = self.cleaned_data["store"]
        try:
            return Store.objects.get(id=store_id)
        except Store.DoesNotExist:
            raise forms.ValidationError(f"Store with id {store_id} does not exist")