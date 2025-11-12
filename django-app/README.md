# Django Development Guide 

This guide provides a step-by-step workflow for creating and testing any new endpoint in our Django project.  
It ensures everyone follows the same process and avoids confusion during development.

---
##### Documentation - https://docs.djangoproject.com/en/5.2/ref/urls/

### 1 - Create URL
- Each endpoint must be registered in your app’s `library/urls.py`.
- Example:
```py
from django.urls import path
from .views import views

urlpatterns = [
    path('example/', views.ExampleView.as_view(), name='example-endpoint'),
]
```

---

##### Documentation - https://docs.djangoproject.com/en/5.2/topics/http/views/

### 2 - Create View
- Decide whether your endpoint will be class-based or function-based..
- Example:

```py
from django.views import View
from django.http import JsonResponse
from django.shortcuts import render

class ExampleView(View):
    def get(self, request):
        # Option 1: JSON API
        return JsonResponse({"message": "GET request successful"})

    def post(self, request):
        # Option 2: Render HTML template
        return render(request, 'templates/example-template.html')

```

---

##### Documentation - https://docs.djangoproject.com/en/5.2/topics/templates/

### 3 - Create Template (if view renders HTML)

- If your view uses render(), create the corresponding HTML template.

- Template path example:

```py
<form method="POST">
  {% csrf_token %}
  <label>Name:</label>
  <input type="text" name="name" required>
  <label>Password:</label>
  <input type="password" name="password" required>
  <button type="submit">Submit</button>
</form>
```

---

##### Documentation - https://docs.djangoproject.com/en/5.2/topics/migrations/
### 4 - Apply Migrations (if models are involved)

- Whenever a new model is created or modified:


##### Create new database migrations
```bash
make migrations
```

##### Apply database migrations

```bash
make migrate 
```

