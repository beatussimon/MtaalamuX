# Contributing to MtaalamuX

Thank you for your interest in contributing to MtaalamuX! We welcome contributions from the community.

## Code of Conduct

This project follows a code of conduct to ensure a welcoming environment for all contributors.

## How to Contribute

### 1. Fork the Repository

Click the "Fork" button at the top right of this page to create your own copy of the repository.

### 2. Clone Your Fork

```bash
git clone https://github.com/your-username/MtaalamuX.git
cd MtaalamuX
```

### 3. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
```

### 4. Set Up Development Environment

```bash
# Using Makefile (recommended)
make setup

# Or manually
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
```

### 5. Make Your Changes

- Follow the existing code style
- Write tests for new features
- Update documentation as needed
- Ensure all tests pass

### 6. Code Quality

Before submitting, ensure your code meets our standards:

```bash
# Run tests
make test

# Check code quality
make lint

# Format code
make format
```

### 7. Commit Your Changes

```bash
git add .
git commit -m "Add your descriptive commit message"
```

### 8. Push to Your Fork

```bash
git push origin feature/your-feature-name
```

### 9. Create a Pull Request

1. Go to the original repository
2. Click "New Pull Request"
3. Select your feature branch
4. Provide a clear description of your changes
5. Submit the pull request

## Development Guidelines

### Code Style

- Follow PEP 8 guidelines
- Use Black for code formatting
- Use isort for import sorting
- Maximum line length: 88 characters

### Testing

- Write tests for all new features
- Maintain test coverage above 80%
- Run the full test suite before submitting

### Documentation

- Update README.md for significant changes
- Add docstrings to new functions and classes
- Update comments for complex logic

### Git Commit Messages

Use clear, descriptive commit messages:

```
feat: add user authentication system
fix: resolve issue with profile image upload
docs: update installation instructions
style: format code with black
test: add tests for user registration
```

### Branch Naming

Use descriptive branch names:

```
feature/user-authentication
bugfix/profile-image-upload
hotfix/security-vulnerability
docs/update-readme
```

## Project Structure

```
MtaalamuX/
├── core/                    # Main Django app
│   ├── models.py           # Database models
│   ├── views.py            # View logic
│   ├── forms.py            # Django forms
│   ├── templates/          # HTML templates
│   ├── static/            # CSS, JS, images
│   └── tests.py           # Test suite
├── mtaalamuX/             # Django project settings
├── media/                 # User uploaded files
├── staticfiles/           # Collected static files
├── requirements.txt       # Python dependencies
└── .env.example          # Environment template
```

## Testing

Run the test suite:

```bash
python manage.py test core.tests --verbosity=2
```

## Reporting Issues

When reporting issues, please include:

1. **Description**: Clear description of the issue
2. **Steps to reproduce**: Step-by-step instructions
3. **Expected behavior**: What should happen
4. **Actual behavior**: What actually happens
5. **Environment**: OS, Python version, Django version
6. **Screenshots**: If applicable

## Feature Requests

For feature requests, please:

1. Check if the feature already exists
2. Search existing issues for similar requests
3. Provide a clear description of the feature
4. Explain why it would be valuable
5. Consider implementation complexity

## License

By contributing to MtaalamuX, you agree that your contributions will be licensed under the MIT License.

## Getting Help

If you need help:

1. Check the [README.md](README.md) for documentation
2. Search existing issues and pull requests
3. Create a new issue with detailed information
4. Join our community discussions

Thank you for contributing to MtaalamuX! 🎉