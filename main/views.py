from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .repositories import *
from .serializers import *
from rest_framework import status
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from .forms import WorkerForm
from django.shortcuts import redirect
from main.NetworkHelper import *
from django.views.decorators.csrf import csrf_exempt

# Create your views here.

# class StoreViewSet(viewsets.ModelViewSet):
#     """
#     A viewset for viewing and editing user instances.
#     """
#     serializer_class = getSerializer(Store)
#     queryset = Store.objects.all()

# ---------------------Store-----------------------
class StoreDetailAPIView(APIView):
    def get(self, request, id):
        sr = StoreRepository()
        ser = getSerializer(Store)

        obj = sr.get_by_id(id)
        if obj is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(ser(obj).data, status=status.HTTP_200_OK)

    def delete(self, request, id):
        if not request.user.is_authenticated:
            return Response(
                {"detail": "Authentication credentials were not provided."},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        sr = StoreRepository()
        try:
            res = sr.delete_by_id(id)
        except Exception as e:
            return Response({"Error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        if res == 0:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    def put(self, request, id):
        sr = StoreRepository()
        res = sr.update_by_id(
            id,
            request.data.get('name'),
            request.data.get('country'),
            request.data.get('street'),
            request.data.get('city'),
            request.data.get('house_number')
        )

        if res > 0:
            ser = getSerializer(Store)
            serializer = ser(sr.get_by_id(id))
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)


class StoreListCreateUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        sr = StoreRepository()
        ser = getSerializer(Store)
        serializer = ser(sr.get_all(), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        ser = getSerializer(Store)
        serializer = ser(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
# ---------------------Worker-----------------------
class WorkerDetailAPIView(APIView):
    def get(self, request, id):
        sr = WorkerRepository()
        ser = getSerializer(Worker)

        obj = sr.get_by_id(id)
        if obj is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return render(request, "worker_detail.html", {"worker": ser(obj).data})
    
    # delete
    def post(self, request, id):
        # if not request.user.is_authenticated:
        #     return Response(
        #         {"detail": "Authentication credentials were not provided."},
        #         status=status.HTTP_401_UNAUTHORIZED
        #     )
        
        sr = WorkerRepository()
        try:
            res = sr.delete_by_id(id)
        except Exception as e:
            return Response({"Error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        if res == 0:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return render(request, "worker_deleted.html", {"id": id})

    def delete(self, request, id):
        if not request.user.is_authenticated:
            return Response(
                {"detail": "Authentication credentials were not provided."},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        sr = WorkerRepository()
        try:
            res = sr.delete_by_id(id)
        except Exception as e:
            return Response({"Error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        if res == 0:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    def put(self, request, id):
        sr = WorkerRepository()
        res = sr.update_by_id(
            id,
            request.data.get('last_name'),
            request.data.get('first_name'),
            request.data.get('email'),
            request.data.get('birth_date'),
            request.data.get('phone_number'),
            request.data.get('store'),
            request.data.get('role')
        )

        if res > 0:
            ser = getSerializer(Worker)
            serializer = ser(sr.get_by_id(id))
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)


class WorkerListCreateUpdateAPIView(APIView):
    # permission_classes = [IsAuthenticated]
    
    def get(self, request):
        sr = WorkerRepository()
        ser = getSerializer(Worker)
        serializer = ser(sr.get_all(), many=True)
        form = WorkerForm()
        return render(request, "worker_list.html", {"workers": serializer.data,"form" : form})
        # return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        sr = WorkerRepository()
        form = WorkerForm(request.POST)
        if(form.is_valid()):
            if(sr.get_by_id(form.cleaned_data["id"])):
                sr.update_by_id(form.cleaned_data["id"],
                                form.cleaned_data["first_name"],
                                form.cleaned_data["last_name"],
                                form.cleaned_data["email"],
                                form.cleaned_data["birth_date"],
                                form.cleaned_data["phone_number"],
                                form.cleaned_data["store"],
                                form.cleaned_data["role"])
                return redirect("worker-detail", id=form.cleaned_data["id"])
            else:
                new = sr.add_one(form.cleaned_data["first_name"],
                                form.cleaned_data["last_name"],
                                form.cleaned_data["email"],
                                form.cleaned_data["birth_date"],
                                form.cleaned_data["phone_number"],
                                form.cleaned_data["store"],
                                form.cleaned_data["role"])
                return redirect("worker-detail", id=new.id)
        else:
            return Response({"error": "incorrect form"}, status=status.HTTP_400_BAD_REQUEST)
        
@api_view(['GET'])
def getList(request, name):
    nh = NetworkHelper()
    log = nh.login()
    res = nh.send('get', f'api/{name}/', sessionid=log['sessionid'])
    if res['status_code'] != 200:
        return Response(status=status.HTTP_400_BAD_REQUEST)
    return render(request, 'custom_list.html', {"data": res['json'], "name": name})

@api_view(['POST'])
@csrf_exempt
def deleteElement(request, name, id):
    nh = NetworkHelper()
    log = nh.login()
    sessionid = log['sessionid']
    res = nh.send("GET", f"api/{name}/", sessionid=sessionid)

    if res['status_code'] != 200:
        return Response({"error": "cannot fetch list"}, status=400)

    data = res['json']
    target = None
    for item in data:
        for key, value in item.items():
            if key.lower().endswith("id") and str(value) == str(id):
                target = value
                break

    if target is None:
        return Response({"error": "object not found"}, status=404)
    
    nh.send("delete", f"api/{name}/{id}/", sessionid=sessionid)

    return redirect(f"/custom/{name}/")


# ---------------------Role-----------------------
class RoleDetailAPIView(APIView):
    def get(self, request, id):
        sr = RoleRepository()
        ser = getSerializer(Role)

        obj = sr.get_by_id(id)
        if obj is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(ser(obj).data, status=status.HTTP_200_OK)

    def delete(self, request, id):
        if not request.user.is_authenticated:
            return Response(
                {"detail": "Authentication credentials were not provided."},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        sr = RoleRepository()
        try:
            res = sr.delete_by_id(id)
        except Exception as e:
            return Response({"Error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        if res == 0:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    def put(self, request, id):
        sr = RoleRepository()
        res = sr.update_by_id(
            id,
            request.data.get('role')
        )

        if res > 0:
            ser = getSerializer(Role)
            serializer = ser(sr.get_by_id(id))
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)


class RoleListCreateUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        sr = RoleRepository()
        ser = getSerializer(Role)
        serializer = ser(sr.get_all(), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        ser = getSerializer(Role)
        serializer = ser(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ---------------------Operation-----------------------
class OperationDetailAPIView(APIView):
    def get(self, request, id):
        sr = OperationRepository()
        ser = getSerializer(Operation)

        obj = sr.get_by_id(id)
        if obj is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(ser(obj).data, status=status.HTTP_200_OK)

    def delete(self, request, id):
        if not request.user.is_authenticated:
            return Response(
                {"detail": "Authentication credentials were not provided."},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        sr = OperationRepository()
        try:
            res = sr.delete_by_id(id)
        except Exception as e:
            return Response({"Error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        if res == 0:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    def put(self, request, id):
        sr = OperationRepository()
        res = sr.update_by_id(
            id,
            request.data.get('operation')
        )

        if res > 0:
            ser = getSerializer(Operation)
            serializer = ser(sr.get_by_id(id))
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)


class OperationListCreateUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        sr = OperationRepository()
        ser = getSerializer(Operation)
        serializer = ser(sr.get_all(), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        ser = getSerializer(Operation)
        serializer = ser(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ---------------------Client-----------------------
class ClientDetailAPIView(APIView):
    def get(self, request, id):
        sr = WorkerRepository()
        ser = getSerializer(Client)

        obj = sr.get_by_id(id)
        if obj is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(ser(obj).data, status=status.HTTP_200_OK)

    def delete(self, request, id):
        if not request.user.is_authenticated:
            return Response(
                {"detail": "Authentication credentials were not provided."},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        sr = ClientRepository()
        try:
            res = sr.delete_by_id(id)
        except Exception as e:
            return Response({"Error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        if res == 0:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    def put(self, request, id):
        sr = ClientRepository()
        res = sr.update_by_id(
            id,
            request.data.get('last_name'),
            request.data.get('first_name'),
            request.data.get('email'),
            request.data.get('birth_date'),
            request.data.get('phone_number')
        )

        if res > 0:
            ser = getSerializer(Client)
            serializer = ser(sr.get_by_id(id))
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)


class ClientListCreateUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        sr = ClientRepository()
        ser = getSerializer(Client)
        serializer = ser(sr.get_all(), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        ser = getSerializer(Client)
        serializer = ser(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ---------------------Item-----------------------
class ItemDetailAPIView(APIView):
    def get(self, request, id):
        sr = ItemRepository()
        ser = getSerializer(Item)

        obj = sr.get_by_id(id)
        if obj is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(ser(obj).data, status=status.HTTP_200_OK)

    def delete(self, request, id):
        if not request.user.is_authenticated:
            return Response(
                {"detail": "Authentication credentials were not provided."},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        sr = ItemRepository()
        try:
            res = sr.delete_by_id(id)
        except Exception as e:
            return Response({"Error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        if res == 0:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    def put(self, request, id):
        sr = ItemRepository()
        res = sr.update_by_id(
            id,
            request.data.get('description'),
            request.data.get('name')
        )

        if res > 0:
            ser = getSerializer(Item)
            serializer = ser(sr.get_by_id(id))
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)


class ItemListCreateUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        sr = ItemRepository()
        ser = getSerializer(Item)
        serializer = ser(sr.get_all(), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        ser = getSerializer(Item)
        serializer = ser(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ---------------------Estimate-----------------------
class EstimateDetailAPIView(APIView):
    def get(self, request, id):
        sr = EstimateRepository()
        ser = getSerializer(Estimate)

        obj = sr.get_by_id(id)
        if obj is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(ser(obj).data, status=status.HTTP_200_OK)

    def delete(self, request, id):
        if not request.user.is_authenticated:
            return Response(
                {"detail": "Authentication credentials were not provided."},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        sr = EstimateRepository()
        try:
            res = sr.delete_by_id(id)
        except Exception as e:
            return Response({"Error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        if res == 0:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    def put(self, request, id):
        sr = EstimateRepository()
        res = sr.update_by_id(
            id,
            request.data.get('item'),
            request.data.get('worker'),
            request.data.get('reasoning'),
            request.data.get('date'),
        )

        if res > 0:
            ser = getSerializer(Estimate)
            serializer = ser(sr.get_by_id(id))
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)


class EstimateListCreateUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        sr = EstimateRepository()
        ser = getSerializer(Estimate)
        serializer = ser(sr.get_all(), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        ser = getSerializer(Estimate)
        serializer = ser(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
# ---------------------OperationHistory-----------------------
class OperationHistoryDetailAPIView(APIView):
    def get(self, request, id):
        sr = OperationHistoryRepository()
        ser = getSerializer(OperationHistory)

        obj = sr.get_by_id(id)
        if obj is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(ser(obj).data, status=status.HTTP_200_OK)

    def delete(self, request, id):
        if not request.user.is_authenticated:
            return Response(
                {"detail": "Authentication credentials were not provided."},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        sr = OperationHistoryRepository()
        try:
            res = sr.delete_by_id(id)
        except Exception as e:
            return Response({"Error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
        if res == 0:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(status=status.HTTP_204_NO_CONTENT)
    
    def put(self, request, id):
        sr = OperationHistoryRepository()
        res = sr.update_by_id(
            id,
            request.data.get('client'),
            request.data.get('item'),
            request.data.get('operation'),
            request.data.get('store'),
            request.data.get('date'),
            request.data.get('price'),
            request.data.get('info')
        )

        if res > 0:
            ser = getSerializer(OperationHistory)
            serializer = ser(sr.get_by_id(id))
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            return Response(status=status.HTTP_404_NOT_FOUND)


class OperationHistoryListCreateUpdateAPIView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        sr = OperationHistoryRepository()
        ser = getSerializer(OperationHistory)
        serializer = ser(sr.get_all(), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        ser = getSerializer(OperationHistory)
        serializer = ser(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)