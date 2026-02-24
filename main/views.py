from django.shortcuts import render, redirect
from rest_framework.response import Response
from rest_framework.decorators import api_view
from .repositories import *
from .repositories.AggregationRepository import AggregationRepository
from .repositories.PandasRepository import PandasRepository
from .serializers import *
import pandas as pd
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from main.NetworkHelper import *
from django.views.decorators.csrf import csrf_exempt
from bokeh.plotting import figure
from bokeh.models import ColumnDataSource, Slider, CustomJS, HoverTool
from bokeh.layouts import column
from bokeh.embed import components
import numpy as np

# Create your views here.

# class StoreViewSet(viewsets.ModelViewSet):
#     """
#     A viewset for viewing and editing user instances.
#     """
#     serializer_class = getSerializer(Store)
#     queryset = Store.objects.all()

# ---------------------Store-----------------------
class StoreDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

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
    permission_classes = [IsAuthenticated]

    def get(self, request, id):
        sr = WorkerRepository()
        ser = getSerializer(Worker)

        obj = sr.get_by_id(id)
        if obj is None:
            return Response(status=status.HTTP_404_NOT_FOUND)
        return Response(ser(obj).data, status=status.HTTP_200_OK)

    def delete(self, request, id):
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
    permission_classes = [IsAuthenticated]

    def get(self, request):
        sr = WorkerRepository()
        ser = getSerializer(Worker)
        serializer = ser(sr.get_all(), many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        ser = getSerializer(Worker)
        serializer = ser(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
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


agg_repo = AggregationRepository()

def _return_dj(data):
    if data is not None:
        return Response({'data': data}, status=200)
    return Response([], status=404)

@api_view(['GET'])
def profitPerStore(request):
    data = agg_repo.get_profit_per_store()
    return _return_dj(data)

@api_view(['GET'])
def topItems(request):
    data = agg_repo.get_top_items()
    return _return_dj(data)

@api_view(['GET'])
def avgPriceForOperation(request):
    data = agg_repo.get_avg_price_for_operation()
    return _return_dj(data)

@api_view(['GET'])
def clientActivity(request):
    data = agg_repo.get_client_activity()
    return _return_dj(data)

@api_view(['GET'])
def estimatesByStore(request):
    data = agg_repo.get_estimates_by_store()
    return _return_dj(data)

@api_view(['GET'])
def maxOperationPriceByCity(request):
    data = agg_repo.get_max_operation_by_city()
    return _return_dj(data)

pandas_repo = PandasRepository()

def _return_pandas_response(data, stats):
    if data is not None and not data.empty:
        return Response({'data': data, 'stats': stats.to_dict()}, status=200)
    return Response({'error': 'No data available'}, status=404)

@api_view(['GET'])
def pandas_profit_per_store(request):
    result_df = pandas_repo.pandas_get_profit_per_store()
    result_df['total_income'] = pd.to_numeric(result_df['total_income'], errors='coerce')
    stats = result_df['total_income'].describe()
    return _return_pandas_response(result_df, stats)

@api_view(['GET'])
def pandas_top_items(request):
    result_df = pandas_repo.pandas_get_top_items()
    result_df['total_income'] = pd.to_numeric(result_df['total_income'], errors='coerce')
    stats = result_df['total_income'].describe()
    return _return_pandas_response(result_df, stats)

@api_view(['GET'])
def pandas_avg_price_for_operation(request):
    result_df = pandas_repo.pandas_get_avg_price_for_operation()
    result_df['avg_price'] = pd.to_numeric(result_df['total_income'], errors='coerce')
    stats = result_df['avg_price'].describe()
    return _return_pandas_response(result_df, stats)

@api_view(['GET'])
def pandas_client_activity(request):
    result_df = pandas_repo.pandas_get_client_activity()
    result_df['operations_count'] = pd.to_numeric(result_df['operations_count'], errors='coerce')
    result_df['total_spent'] = pd.to_numeric(result_df['total_spent'], errors='coerce')
    stats = result_df[['operations_count', 'total_spent']].describe()
    return _return_pandas_response(result_df, stats)

@api_view(['GET'])
def pandas_estimates_by_store(request):
    result_df = pandas_repo.pandas_get_estimates_by_store()
    result_df['estimates_count'] = pd.to_numeric(result_df['estimates_count'], errors='coerce')
    stats = result_df['estimates_count'].describe()
    return _return_pandas_response(result_df, stats)

@api_view(['GET'])
def pandas_max_operation_by_city(request):
    result_df = pandas_repo.pandas_get_max_operation_by_city()
    result_df['price'] = pd.to_numeric(result_df['price'], errors='coerce')
    stats = result_df['price'].describe()
    return _return_pandas_response(result_df, stats)

# plotly

@api_view(['GET'])
def plotly_profit_per_store(request):
    data = pandas_repo.pandas_get_profit_per_store()
    return render(request, 'plotly_profit_per_store.html', {'data': data.to_dict(orient='records')})

@api_view(['GET'])
def plotly_top_items(request):
    data = pandas_repo.pandas_get_top_items()
    return render(request, 'plotly_top_items.html', {'data': data.to_dict(orient='records')})

@api_view(['GET'])
def plotly_avg_price_for_operation(request):
    data = pandas_repo.pandas_get_avg_price_for_operation()
    return render(request, 'plotly_avg_price_for_operation.html', {'data': data.to_dict(orient='records')})

@api_view(['GET'])
def plotly_client_activity(request):
    data = pandas_repo.pandas_get_client_activity()
    return render(request, 'plotly_client_activity.html', {'data': data.to_dict(orient='records')})

@api_view(['GET'])
def plotly_estimates_by_store(request):
    data = pandas_repo.pandas_get_estimates_by_store()
    return render(request, 'plotly_estimates_by_store.html', {'data': data.to_dict(orient='records')})

@api_view(['GET'])
def plotly_max_operation_by_city(request):
    data = pandas_repo.pandas_get_max_operation_by_city()
    return render(request, 'plotly_max_operation_by_city.html', {'data': data.to_dict(orient='records')})

# bokeh

@api_view(['GET'])
def bokeh_profit_per_store(request):
    df = pandas_repo.pandas_get_profit_per_store()
    df['total_income'] = pd.to_numeric(df['total_income'], errors='coerce').fillna(0)
    agg = df.groupby(['id', 'name'], as_index=False)['total_income'].sum().sort_values('total_income', ascending=False)

    categories = list(pd.unique(agg['name'].astype(str)))
    source = ColumnDataSource(agg)
    original = ColumnDataSource(agg.copy())

    p = figure(x_range=categories, height=500, width=900, title="Дохід магазинів")
    p.vbar(x='name', top='total_income', width=0.8, source=source)
    p.add_tools(HoverTool(tooltips=[("Магазин", "@name"), ("Дохід", "@total_income")]))

    p.xaxis.major_label_orientation = 0.8
    p.xaxis.major_label_text_font_size = "10pt"
    p.title.text_font_size = "16pt"
    p.min_border = 50
    p.y_range.start = 0

    slider = Slider(start=0, end=float(agg['total_income'].max() or 0), value=0, step=100, title="Мінімальний дохід")
    slider.js_on_change("value", CustomJS(args=dict(source=source, original=original, slider=slider), code="""
        const s = source.data;
        const o = original.data;
        const thr = slider.value;
        for (let i = 0; i < o['total_income'].length; i++) {
            if (o['total_income'][i] >= thr) {
                s['total_income'][i] = o['total_income'][i];
            } else {
                s['total_income'][i] = 0;
            }
        }
        source.change.emit();
    """))

    layout = column(slider, p)
    script, div = components(layout)
    return render(request, "bokeh_profit_per_store.html", {"bokeh_script": script, "bokeh_div": div})


@api_view(['GET'])
def bokeh_top_items(request):
    df = pandas_repo.pandas_get_top_items()
    df['total_income'] = pd.to_numeric(df['total_income'], errors='coerce').fillna(0)
    agg = df.groupby(['id', 'name'], as_index=False)['total_income'].sum().sort_values('total_income', ascending=False)

    categories = list(pd.unique(agg['name'].astype(str)))
    source = ColumnDataSource(agg)
    original = ColumnDataSource(agg.copy())

    p = figure(x_range=categories, height=500, width=900, title="Топ товарів за доходом")
    p.vbar(x='name', top='total_income', width=0.8, source=source)
    p.add_tools(HoverTool(tooltips=[("Товар", "@name"), ("Дохід", "@total_income")]))

    p.xaxis.major_label_orientation = 0.8
    p.xaxis.major_label_text_font_size = "10pt"
    p.title.text_font_size = "16pt"
    p.min_border = 50
    p.y_range.start = 0

    slider = Slider(start=0, end=float(agg['total_income'].max() or 0), value=0, step=100, title="Мінімальний дохід")
    slider.js_on_change("value", CustomJS(args=dict(source=source, original=original, slider=slider), code="""
        const s = source.data;
        const o = original.data;
        const thr = slider.value;
        for (let i = 0; i < o['total_income'].length; i++) {
            s['total_income'][i] = (o['total_income'][i] >= thr) ? o['total_income'][i] : 0;
        }
        source.change.emit();
    """))

    layout = column(slider, p)
    script, div = components(layout)
    return render(request, "bokeh_top_items.html", {"bokeh_script": script, "bokeh_div": div})


@api_view(['GET'])
def bokeh_avg_price_for_operation(request):
    df = pandas_repo.pandas_get_avg_price_for_operation()
    df['avg_price'] = pd.to_numeric(df.get('avg_price', df.get('total_income')), errors='coerce').fillna(0)
    agg = df.groupby(['id', 'operation'], as_index=False)['avg_price'].mean().sort_values('avg_price', ascending=False)

    total = agg['avg_price'].sum()
    if total == 0:
        agg['angle'] = 0.0
    else:
        agg['angle'] = agg['avg_price'] / total * 2 * np.pi

    # compute start and end angles as columns (required when using a source)
    agg['start_angle'] = agg['angle'].cumsum().shift(fill_value=0).fillna(0)
    agg['end_angle'] = agg['start_angle'] + agg['angle']
    agg['color'] = ([
        "#718dbf","#e84d60","#c9d9d3","#e6a2c1","#c6d9f1","#ffd27f",
        "#b2df8a","#fb9a99","#fdbf6f","#cab2d6","#ffff99","#8dd3c7"
    ] * ((len(agg)//12)+1))[:len(agg)]
    agg['alpha'] = 1.0

    source = ColumnDataSource(agg)
    p = figure(height=500, width=700, title="Доля середньої ціни по операціях",
               toolbar_location=None, tools="hover", tooltips="@operation: @avg_price")
    # use start_angle and end_angle column names (required when source provided)
    p.wedge(x=0, y=1, radius=0.8, start_angle='start_angle', end_angle='end_angle',
            color='color', legend_field='operation', source=source, fill_alpha='alpha')

    # slider toggles alpha (no need to recalc angles client-side)
    slider = Slider(start=0, end=float(agg['avg_price'].max() or 0), value=0, step=1, title="Мінімальна середня ціна")
    slider.js_on_change("value", CustomJS(args=dict(source=source, slider=slider), code="""
        const s = source.data;
        const thr = slider.value;
        for (let i = 0; i < s['avg_price'].length; i++) {
            s['alpha'][i] = (s['avg_price'][i] >= thr) ? 1 : 0;
        }
        source.change.emit();
    """))

    layout = column(slider, p)
    script, div = components(layout)
    return render(request, "bokeh_avg_price_for_operation.html", {"bokeh_script": script, "bokeh_div": div})


@api_view(['GET'])
def bokeh_client_activity(request):
    df = pandas_repo.pandas_get_client_activity()
    df['operations_count'] = pd.to_numeric(df['operations_count'], errors='coerce').fillna(0)
    df['total_spent'] = pd.to_numeric(df['total_spent'], errors='coerce').fillna(0)
    df['full_name'] = (df['first_name'].fillna('') + ' ' + df['last_name'].fillna('')).str.strip()
    agg = df.groupby(['id', 'full_name'], as_index=False).agg({'operations_count': 'sum', 'total_spent': 'sum'}).sort_values('total_spent', ascending=False)

    categories = list(pd.unique(agg['full_name'].astype(str)))
    source = ColumnDataSource(agg)
    original = ColumnDataSource(agg.copy())

    p = figure(x_range=categories, height=500, width=1000, title="Активність клієнтів")
    p.vbar(x='full_name', top='total_spent', width=0.8, source=source)
    p.add_tools(HoverTool(tooltips=[("Клієнт", "@full_name"), ("Витратив", "@total_spent"), ("Операцій", "@operations_count")]))

    p.xaxis.major_label_orientation = 0.8
    p.xaxis.major_label_text_font_size = "9pt"
    p.title.text_font_size = "16pt"
    p.min_border = 50
    p.y_range.start = 0

    slider = Slider(start=0, end=float(agg['total_spent'].max() or 0), value=0, step=100, title="Мінімальні витрати клієнта")
    slider.js_on_change("value", CustomJS(args=dict(source=source, original=original, slider=slider), code="""
        const s = source.data;
        const o = original.data;
        const thr = slider.value;
        for (let i = 0; i < o['total_spent'].length; i++) {
            s['total_spent'][i] = (o['total_spent'][i] >= thr) ? o['total_spent'][i] : 0;
            s['operations_count'][i] = (o['total_spent'][i] >= thr) ? o['operations_count'][i] : 0;
        }
        source.change.emit();
    """))

    layout = column(slider, p)
    script, div = components(layout)
    return render(request, "bokeh_client_activity.html", {"bokeh_script": script, "bokeh_div": div})


@api_view(['GET'])
def bokeh_estimates_by_store(request):
    df = pandas_repo.pandas_get_estimates_by_store()
    df['estimates_count'] = pd.to_numeric(df['estimates_count'], errors='coerce').fillna(0)
    agg = df.groupby(['id', 'name'], as_index=False)['estimates_count'].sum().sort_values('estimates_count', ascending=False)

    categories = list(pd.unique(agg['name'].astype(str)))
    source = ColumnDataSource(agg)
    original = ColumnDataSource(agg.copy())

    p = figure(x_range=categories, height=500, width=900, title="Кількість оцінок по магазинах")
    p.vbar(x='name', top='estimates_count', width=0.8, source=source)
    p.add_tools(HoverTool(tooltips=[("Магазин", "@name"), ("Оцінок", "@estimates_count")]))

    p.xaxis.major_label_orientation = 0.8
    p.xaxis.major_label_text_font_size = "10pt"
    p.title.text_font_size = "16pt"
    p.min_border = 50
    p.y_range.start = 0

    slider = Slider(start=0, end=float(agg['estimates_count'].max() or 0), value=0, step=1, title="Мінімальна кількість оцінок")
    slider.js_on_change("value", CustomJS(args=dict(source=source, original=original, slider=slider), code="""
        const s = source.data;
        const o = original.data;
        const thr = slider.value;
        for (let i = 0; i < o['estimates_count'].length; i++) {
            s['estimates_count'][i] = (o['estimates_count'][i] >= thr) ? o['estimates_count'][i] : 0;
        }
        source.change.emit();
    """))

    layout = column(slider, p)
    script, div = components(layout)
    return render(request, "bokeh_estimates_by_store.html", {"bokeh_script": script, "bokeh_div": div})


@api_view(['GET'])
def bokeh_max_operation_by_city(request):
    df = pandas_repo.pandas_get_max_operation_by_city()
    df['price'] = pd.to_numeric(df['price'], errors='coerce').fillna(0)
    agg = df.groupby('city', as_index=False).agg({'price': 'max'}).sort_values('price', ascending=False)

    categories = list(pd.unique(agg['city'].astype(str)))
    source = ColumnDataSource(agg)
    original = ColumnDataSource(agg.copy())

    p = figure(x_range=categories, height=500, width=900, title="Максимальна операція по містам")
    p.vbar(x='city', top='price', width=0.8, source=source)
    p.add_tools(HoverTool(tooltips=[("Місто", "@city"), ("Ціна", "@price")]))

    p.xaxis.major_label_orientation = 0.8
    p.xaxis.major_label_text_font_size = "10pt"
    p.title.text_font_size = "16pt"
    p.min_border = 50
    p.y_range.start = 0

    slider = Slider(start=0, end=float(agg['price'].max() or 0), value=0, step=1, title="Мінімальна ціна")
    slider.js_on_change("value", CustomJS(args=dict(source=source, original=original, slider=slider), code="""
        const s = source.data;
        const o = original.data;
        const thr = slider.value;
        for (let i = 0; i < o['price'].length; i++) {
            s['price'][i] = (o['price'][i] >= thr) ? o['price'][i] : 0;
        }
        source.change.emit();
    """))

    layout = column(slider, p)
    script, div = components(layout)
    return render(request, "bokeh_max_operation_by_city.html", {"bokeh_script": script, "bokeh_div": div})

# ---------------------Role-----------------------
class RoleDetailAPIView(APIView):
    permission_classes = [IsAuthenticated]

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
    permission_classes = [IsAuthenticated]

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
    permission_classes = [IsAuthenticated]

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
    permission_classes = [IsAuthenticated]

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
    permission_classes = [IsAuthenticated]

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
    permission_classes = [IsAuthenticated]

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