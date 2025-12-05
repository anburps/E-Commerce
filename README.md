
# 🛒 Multi-Tenant E-Commerce Backend (Django + DRF + JWT)

A complete multi-tenant e-commerce backend using **Django**, **Django REST Framework**, and **JWT authentication**.  
Each vendor acts as an isolated tenant with independent products, orders, and customers.

---

## 🚀 Features

### ✔ Multi-Tenancy
- Each vendor (tenant) manages their own data.
- Products, orders, and customers are scoped per vendor.
- Strict isolation—no cross-tenant access.

### ✔ Role-Based Access Control (RBAC)
| Role | Permissions |
|------|-------------|
| **Owner** | Full access: manage products, orders, staff & customers |
| **Staff** | Can manage products & orders only |
| **Customer** | Can view products & place orders |

### ✔ JWT Authentication
JWT token includes:
- `user_id`
- `vendor_id`
- `role`

Used for tenant-aware authorization.

---

# 🛠 Setup Steps

Follow these steps to install and run the project locally:

---

## 1️⃣ Clone the Repository
```sh
git clone <your-github-repository-url>
cd your-project-folder
```

---

## 2️⃣ Create Virtual Environment
```sh
python3.10 -m venv venv
source venv/bin/activate
```

---

## 3️⃣ Install Dependencies
```sh
pip install -r requirements.txt
```

---

## 4️⃣ Apply Migrations
```sh
python manage.py migrate
```

---

## 5️⃣ Create Superuser (Optional)
```sh
python manage.py createsuperuser
```

---

## 6️⃣ Run the Application
```sh
python manage.py runserver
```

Server accessible at:
```
http://127.0.0.1:8000/
```

---

# 📡 API Endpoints

## 🔐 Authentication
| Method | URL | Description |
|--------|-----|-------------|
| POST | `/accounts/register/` | Register new user |
| POST | `/accounts/login/` | JWT login |
| POST | `/accounts/token/refresh/` | Refresh token |

---

## 🏬 Vendor (Tenant) APIs
| Method | URL | Description |
|--------|-----|-------------|
| GET | `/app/vendors/` | List vendors owned by user |
| POST | `/app/vendors/` | Create new vendor |
| POST | `/app/vendors/{vendor_id}/assign-role/` | Assign staff/customer role |

---

## 🛍 Product APIs (Tenant Scoped)
| Method | URL | Description |
|--------|-----|-------------|
| GET | `/app/vendors/{vendor_id}/products/` | List products |
| POST | `/app/vendors/{vendor_id}/products/` | Create product (owner/staff only) |
| GET | `/app/vendors/{vendor_id}/products/{id}/` | Product details |
| PUT | `/app/vendors/{vendor_id}/products/{id}/` | Update product |
| DELETE | `/app/vendors/{vendor_id}/products/{id}/` | Delete product |

---

## 📦 Order APIs (Tenant Scoped)
| Method | URL | Description |
|--------|-----|-------------|
| GET | `/app/vendors/{vendor_id}/orders/` | List orders |
| POST | `/app/vendors/{vendor_id}/orders/` | Create order (customer only) |
| GET | `/app/vendors/{vendor_id}/orders/{id}/` | View single order |
| PUT | `/app/vendors/{vendor_id}/orders/{id}/` | Update order status (staff/owner only) |

---

# 🧠 Multi-Tenancy Implementation

### ✔ Vendor = Tenant
The `Vendor` model acts as a tenant.  
Every tenant-specific model contains:

```python
vendor = models.ForeignKey(Vendor, ...)
```

This ensures:
- Data separation
- Tenant-level filtering
- No cross-access between vendors

Views always fetch tenant data using:

```python
vendor_id = kwargs["vendor_id"]
```

---

# 🔐 Role-Based Access Implementation

### ✔ UserVendorRole Model
Each user gets a role **per vendor**:

```python
class UserVendorRole(models.Model):
    user = FK(User)
    vendor = FK(Vendor)
    role = owner | staff | customer
```

This allows:
- Same user to have different roles in different vendors
- Fine-grained permission control

### ✔ Permissions in Views

Example:

```python
if not (is_owner(user, vendor) or is_staff(user, vendor)):
    raise PermissionError("Not allowed")
```

Customers cannot modify data; they may only place orders.

---
