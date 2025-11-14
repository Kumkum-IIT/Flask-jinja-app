# Flask Jinja App

This repository contains a **complete Flask + Jinja2 web application** built with a modular structure, template-based UI, and controller-driven backend logic. The application supports multiple user types (influencers, sponsors, admins) and includes dashboards, forms, and profile management.

---

## 🚀 Overview

This project is a multi-user web platform built with **Flask**, featuring:

* Jinja2-based HTML templates
* Role-based dashboards (Admin, Influencer, Sponsor)
* CRUD operations for campaigns, users, and requests
* Form submissions and profile update flows
* Modular Python backend (controllers, services, models)
* Static asset management

---

## 🧩 Key Features

### **User Management**

* Sponsor registration & login
* Influencer registration & login
* Admin dashboard for approvals and oversight

### **Campaign System**

* Create, edit, update, delete campaigns
* Assign influencers to campaigns
* Approve / reject campaign requests

### **Dashboards**

* **Admin dashboard** – Manage users, campaigns, approvals
* **Influencer dashboard** – View campaigns, requests, profile
* **Sponsor dashboard** – Create campaigns, manage influencers

### **Other Features**

* Search functionality
* Summary pages for all user types
* Email/request flow (request influencer, approve request, etc.)
* Profile update pages for all users

---

## 🗂️ Project Structure

* **applications/** – Main backend logic

  * `config.py`
  * `controllers.py`
  * `database.py`
  * `model.py`
* **templates/** – All HTML pages rendered using Jinja2
* **static/** – CSS, JS, and image files
* `main.py` – Application entry point
* `requirements.txt` – Python dependencies

---

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone <repo-url>
cd flask-jinja-app
```

### 2. Create and activate virtual environment

```bash
python -m venv env
source env/bin/activate  # Windows: env\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the application

```bash
python main.py
```

Visit the app at:
**[http://127.0.0.1:5000](http://127.0.0.1:5000)**

---

## 📝 Note on Templates

The `templates/` folder contains all user-facing HTML files, including:

* Registration/Login templates
* Influencer & Sponsor dashboards
* Campaign management pages
* Search & summary views
* Profile update pages

Each template uses Jinja2 features such as:

* Loops (`{% for ... %}`)
* Conditional rendering (`{% if ... %}`)
* Template inheritance (`{% extends 'base.html' %}`)

---

## 🤝 Contributing

Feel free to contribute by opening issues or submitting PRs.

---

## 📄 License

Open-source under MIT License.
