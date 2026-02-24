# Lab3 - Django Pawnshop Management System

## Project Description

A Django REST API application for managing a pawnshop business, featuring data models for clients, workers, stores, operations, and items. Includes analytics, data visualization, and a dynamic repository pattern implementation.

## Technology Stack

- **Framework**: Django 5.2
- **Database**: MySQL (127.0.0.1:3306, database: pawnshop)
- **REST API**: Django REST Framework
- **Authentication**: dj-rest-auth + django-allauth (Token-based)
- **API Documentation**: drf-spectacular (OpenAPI schema at `/api/schema/`)
- **Data Analysis**: Pandas, NumPy
- **Visualization**: Plotly, Bokeh
- **Template Engine**: Django Templates

## Data Models

| Model | Description |
|-------|-------------|
| **Client** | Person with first_name, last_name, email, birth_date, phone_number |
| **Worker** | Person linked to Store and Role |
| **Store** | Shop location (name, country, city, street, house_number) |
| **Role** | Worker role (e.g., Manager, Cashier) |
| **Operation** | Type of operation (e.g., Buy, Sell, Pawn) |
| **Item** | Item being traded/sold |
| **Estimate** | Worker estimates for items (composite primary key) |
| **OperationHistory** | Transaction records linking client, item, operation, store |

### Inheritance
- `Person` (abstract): Base model for Client and Worker

## API Endpoints

### CRUD Endpoints
| Endpoint | Methods | Description |
|----------|---------|-------------|
| `/stores/` | GET, POST | List/Create stores |
| `/stores/<id>/` | GET, PUT, DELETE | Single store |
| `/workers/` | GET, POST | List/Create workers |
| `/workers/<id>/` | GET, PUT, DELETE | Single worker |
| `/roles/` | GET, POST | List/Create roles |
| `/roles/<id>/` | GET, PUT, DELETE | Single role |
| `/operations/` | GET, POST | List/Create operations |
| `/operations/<id>/` | GET, PUT, DELETE | Single operation |
| `/clients/` | GET, POST | List/Create clients |
| `/clients/<id>/` | GET, PUT, DELETE | Single client |
| `/items/` | GET, POST | List/Create items |
| `/items/<id>/` | GET, PUT, DELETE | Single item |
| `/estimates/` | GET, POST | List/Create estimates |
| `/estimates/<id>/` | GET, PUT, DELETE | Single estimate |
| `/op-his/` | GET, POST | List/Create operation history |
| `/op-his/<id>/` | GET, PUT, DELETE | Single operation record |

### Custom Endpoints
- `/custom/<name>/` - Dynamic list via NetworkHelper
- `/custom/<name>/<id>/` - Dynamic delete

### Aggregation Endpoints (Django ORM)
- `/aggregation/profitPerStore/`
- `/aggregation/topItems/`
- `/aggregation/avgPriceForOperation/`
- `/aggregation/clientActivity/`
- `/aggregation/estimatesByStore/`
- `/aggregation/maxOperationPriceByCity/`

### Pandas Analysis Endpoints
- `/pandas/profitPerStore/`
- `/pandas/topItems/`
- `/pandas/avgPriceForOperation/`
- `/pandas/clientActivity/`
- `/pandas/estimatesByStore/`
- `/pandas/maxOperationPriceByCity/`

Returns: `{ "data": [...], "stats": {...} }`

### Visualization Endpoints

#### Plotly
- `/plotly/profitPerStore/`
- `/plotly/topItems/`
- `/plotly/avgPriceForOperation/`
- `/plotly/clientActivity/`
- `/plotly/estimatesByStore/`
- `/plotly/maxOperationPriceByCity/`

#### Bokeh
- `/bokeh/profitPerStore/`
- `/bokeh/topItems/`
- `/bokeh/avgPriceForOperation/`
- `/bokeh/clientActivity/`
- `/bokeh/estimatesByStore/`
- `/bokeh/maxOperationPriceByCity/`

### Authentication
- `/api/auth/` - Authentication endpoints (login, registration, token)

## Architecture Patterns

### Repository Pattern
- Custom repository interfaces: `IRepository`, `IPersonRepository`
- Implementations: `StoreRepository`, `WorkerRepository`, `ClientRepository`, `RoleRepository`, `OperationRepository`, `ItemRepository`, `EstimateRepository`, `OperationHistoryRepository`
- Provides abstraction over Django ORM

### Dynamic Serializer
- `getSerializer(model)` in `main/serializers.py` dynamically generates ModelSerializer classes

### NetworkHelper
- `main/NetworkHelper.py` - Handles login and session-based API requests

## Problems & Improvements

### Issues Found

1. **Hardcoded Database Credentials**
   - `lab3/settings.py:103-104` contains plaintext MySQL password
   - Should use environment variables

2. **Inconsistent Authentication**
   - Some endpoints check authentication, others don't
   - `WorkerDetailAPIView.post()` has auth check commented out (line 109)
   - `WorkerListCreateUpdateAPIView` has auth entirely commented (line 164)

3. **Mixed Response Types**
   - Same endpoint returns JSON (APIView) or HTML (render) depending on method
   - Example: `WorkerDetailAPIView.get()` returns Response, but `WorkerListCreateUpdateAPIView.get()` returns render

4. **Duplicate Code**
   - Aggregation logic duplicated in `AggregationRepository` and `PandasRepository`
   - Could consolidate into single analytics service

5. **No Input Validation**
   - Forms in `main/forms.py` exist but minimal validation
   - API relies heavily on serializer validation only

6. **Missing Error Handling**
   - Repository methods lack consistent error handling
   - Generic Exception catching without specific handling

7. **Incomplete Composite Primary Key Support**
   - `Estimate` model uses `CompositePrimaryKey` (line 27) but standard Django patterns may not handle it well

8. **Template-Code Coupling**
   - Business logic mixed with view rendering
   - Templates contain embedded JavaScript for Bokeh interactivity

### Suggested Improvements

1. **Environment Variables**: Move secrets to `.env` file using `python-dotenv`

2. **Consistent Auth**: Apply `IsAuthenticated` permission class uniformly to all CRUD endpoints

3. **Separate API/UI Layers**: Create dedicated API-only views and UI views

4. **Type Hints**: Add type annotations throughout codebase

5. **Tests**: Add unit tests for repositories and views

6. **Caching**: Implement caching for aggregation endpoints

7. **Pagination**: Add pagination to list endpoints

8. **Rate Limiting**: Add throttling for API endpoints

9. **Database Indexes**: Add indexes on frequently queried fields (foreign keys, dates)

10. **Docker**: Add Dockerfile for containerization

## Running the Project

```bash
# Install dependencies
pip install django djangorestframework mysqlclient pandas numpy plotly bokeh drf-spectacular dj-rest-auth django-allauth

# Run migrations
python manage.py migrate

# Start server
python manage.py runserver
```

## Project Structure

```
lab3/
├── lab3/              # Django project settings
├── main/              # Main app
│   ├── models.py      # Database models
│   ├── views.py       # API views
│   ├── serializers.py # DRF serializers
│   ├── forms.py       # Django forms
│   ├── repositories/  # Repository pattern implementations
│   └── NetworkHelper.py
├── authentication/     # Auth app
├── templates/         # Templates app + HTML templates
└── manage.py
```
