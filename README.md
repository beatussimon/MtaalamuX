# MtaalamuX 🚀

[![Django Version](https://img.shields.io/badge/Django-5.0.7-green.svg)](https://djangoproject.com/)
[![Python Version](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://img.shields.io/badge/Tests-8%20Passing-brightgreen.svg)]()

A **professional-grade Django platform** connecting experts with clients. Built with modern web technologies, featuring enterprise-level design, comprehensive testing, and production-ready architecture.

## ✨ Features

### 🔐 **Authentication & Security**
- Secure user authentication with Django's built-in auth system
- Password validation and security best practices
- CSRF protection and secure session management
- Environment-based configuration for production security

### 👥 **Professional Profiles**
- Comprehensive expert profiles with verification system
- Portfolio showcase with image uploads
- Skills categorization and location-based services
- Professional ratings and review system

### 📝 **Content Management**
- Rich article publishing with commenting system
- Category-based content organization
- Image upload and media management
- Professional content creation interface

### 💼 **Job Management**
- Advanced job posting and application system
- External job URL integration
- Professional document uploads
- Job status tracking and management

### 💬 **Communication**
- Real-time messaging system
- Notification center with unread counters
- Professional communication interface

### 🎨 **Modern UI/UX**
- **Enterprise-grade design** with professional styling
- **Flawless dark/light mode** with instant switching
- **Responsive design** optimized for all devices
- **Glassmorphism effects** and modern animations
- **Accessibility compliant** with proper contrast ratios

### 🛠 **Technical Excellence**
- **Comprehensive test suite** (8 tests passing)
- **Production-ready settings** with environment variables
- **Security hardened** for deployment
- **Optimized performance** with proper static file handling
- **Clean, maintainable code** following Django best practices

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip
- Virtual environment (recommended)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/beatussimon/MtaalamuX.git
   cd MtaalamuX
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment configuration**
   ```bash
   cp .env.example .env
   # Edit .env with your settings
   ```

5. **Database setup**
   ```bash
   python manage.py migrate
   python manage.py createsuperuser
   ```

6. **Collect static files**
   ```bash
   python manage.py collectstatic --noinput
   ```

7. **Run the development server**
   ```bash
   python manage.py runserver
   ```

Visit `http://127.0.0.1:8000` to see your professional platform!

## 🧪 Testing

Run the comprehensive test suite:

```bash
python manage.py test core.tests --verbosity=2
```

All 8 tests cover:
- ✅ Model creation and validation
- ✅ Form validation
- ✅ View functionality
- ✅ User profile management

## 📁 Project Structure

```
MtaalamuX/
├── core/                    # Main application
│   ├── models.py           # Database models
│   ├── views.py            # View logic
│   ├── forms.py            # Django forms
│   ├── templates/          # HTML templates
│   ├── static/            # CSS, JS, images
│   └── tests.py           # Test suite
├── mtaalamuX/             # Django project settings
│   ├── settings.py        # Configuration
│   ├── urls.py            # URL routing
│   └── wsgi.py            # WSGI application
├── media/                 # User uploaded files
├── staticfiles/           # Collected static files
├── requirements.txt       # Python dependencies
├── .env.example          # Environment template
└── .gitignore           # Git ignore rules
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file with:

```env
# Django Configuration
SECRET_KEY=your-secret-key-here-change-this-in-production
DEBUG=True
ALLOWED_HOSTS=127.0.0.1,localhost,yourdomain.com

# Database (Optional - defaults to SQLite)
DATABASE_URL=postgresql://user:password@localhost:5432/dbname

# Email Configuration
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Security (Production only)
SECURE_SSL_REDIRECT=True
SECURE_HSTS_SECONDS=31536000
CSRF_TRUSTED_ORIGINS=https://yourdomain.com
```

### Production Deployment

For production deployment:

1. Set `DEBUG=False`
2. Use a strong `SECRET_KEY`
3. Configure `ALLOWED_HOSTS`
4. Set up SSL/HTTPS
5. Use PostgreSQL database
6. Configure email settings
7. Set up proper static file serving

## 🎨 Design System

### Color Palette
- **Primary**: Professional blue gradients
- **Secondary**: Modern gray tones
- **Accent**: Success/error/warning colors
- **Dark Mode**: Carefully crafted dark theme

### Typography
- **Primary Font**: Inter (modern, professional)
- **Hierarchy**: Consistent heading scales
- **Readability**: Optimized line heights and spacing

### Components
- **Cards**: Professional shadows and hover effects
- **Buttons**: Modern styling with smooth animations
- **Forms**: Clean, accessible form design
- **Navigation**: Glassmorphism navbar with mobile optimization

## 🔒 Security Features

- **CSRF Protection**: Enabled on all forms
- **XSS Prevention**: Content security policies
- **Clickjacking Protection**: X-Frame-Options headers
- **Secure Headers**: HSTS, content type sniffing prevention
- **Password Security**: Strong validation requirements
- **Session Security**: Secure cookie settings

## 📱 Responsive Design

- **Mobile-first approach** with Bootstrap 5
- **Tablet optimization** for medium screens
- **Desktop enhancement** with advanced layouts
- **Touch-friendly** interface elements
- **Performance optimized** for all devices

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Django Framework** - The web framework that makes this possible
- **Bootstrap 5** - Responsive design foundation
- **Font Awesome** - Professional icon library
- **Inter Font** - Modern typography

## 📞 Support

For support, email support@mtaalamux.com or create an issue in this repository.

---

**Built with ❤️ and perfection in mind**