# 🚀 Python CMS

A modern, lightweight, and highly customizable **Content Management System** built with **Django 6.0** and **Python 3.14.2**. Designed for performance, scalability, and ease of use.

---

## ✨ Key Features

- 🛠️ **Modular Architecture**: Clean separation of concerns with dedicated apps for Blog, Articles, Services, and more.
- 🎨 **Modern Admin Interface**: Powered by `django-jazzmin` with professional dark/light mode support.
- 📝 **Rich Content Editing**: Seamless content creation with integrated `django-ckeditor`.
- 🌐 **API-First Design**: Built-in REST API infrastructure using **Django REST Framework**.
- 🖌️ **Utility-First Styling**: Highly responsive UI built with **Tailwind CSS**.
- 📦 **Included Modules**:
  - `accounts` & `users`: Robust authentication and profile management.
  - `articles` & `blog`: Comprehensive content publishing tools.
  - `services` & `features`: Showcase your offerings effectively.
  - `testimonials` & `social`: Build trust and social proof.
  - `faq` & `menu`: Intuitive navigation and support management.
  - `gallery` & `slideshow`: Visual media presentation and hero banners.
  - `package` & `offers`: Booking packages, special deals, and promotions.
  - `location` & `nearby`: Maps, location details, and nearby attractions.
  - `popup` & `preferences`: Promotional popups and global site settings (SEO, contacts).

---

## 💻 Tech Stack

| Component | Technology |
| :--- | :--- |
| **Framework** | [Django 6.0](https://www.djangoproject.com/) |
| **Language** | [Python 3.14.2](https://www.python.org/) |
| **Database** | SQLite (Default) / PostgreSQL Ready |
| **Styling** | [Tailwind CSS](https://tailwindcss.com/) |
| **Admin Theme** | [Jazzmin](https://github.com/farridav/django-jazzmin) |
| **API** | [Django REST Framework](https://www.django-rest-framework.org/) |

---

## 🚀 Getting Started

Follow these steps to set up your local development environment.

### 1. Prerequisites
Ensure you have **Python 3.14.2** installed.
- **Download:** [Python 3.14.2 Official Release](https://www.python.org/downloads/release/python-3142/)

### 2. Setup and Installation

```bash
# 1. Clone the repository
git clone https://github.com/sachinsulu/python-cms.git
cd python-cms

# 2. Create and activate a virtual environment
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run database migrations
python manage.py migrate

# 5. Create an administrative user
python manage.py createsuperuser

# 6. Start the development server
python manage.py runserver
```

---

## 📂 Project Structure

```text
python-cms/
├── accounts/      # User authentication and accounts
├── api/           # REST API endpoints
├── cms/           # Core project settings and configuration
├── core/          # Shared components and utilities
├── frontend/      # Frontend templates and specific site themes
├── media_manager/ # Centralized file upload and image validations
├── package/       # Service packages and room offerings
├── preferences/   # Global site settings, SEO, content variables
├── requirements/  # Project dependencies
└── [other apps]/  # Feature apps like blog, gallery, offers, etc.
```

---

## 🛠️ Configuration

Key settings can be found in `cms/settings.py`. Ensure you configure your `SECRET_KEY` and `ALLOWED_HOSTS` for production environments.

### Environment Variables
Consider using a `.env` file for:
- `DEBUG`
- `SECRET_KEY`
- `DATABASE_URL`

---

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
