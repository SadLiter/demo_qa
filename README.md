# API Testing Suite

This project is a demo for API testing using **pytest**, **requests**, and **python-dotenv**. It demonstrates 6 small tests covering basic operations such as authentication and movie data management.  
Additionally, it implements a **custom testing framework** for managing API clients and HTTP requests.

## Project Structure

```
├── api
│   ├── api_manager.py        # API Manager for grouping API clients
│   ├── auth_api.py           # Authentication API client
│   └── movies_api.py         # Movies API client
├── conftest.py               # Pytest fixtures
├── constants.py              # Configuration constants (loaded from .env)
├── requester
│   └── custom_requester.py   # Custom HTTP requester with logging
├── tests
│   └── test_film_api.py      # Contains 6 test cases
├── .env                      # Environment variables (not committed)
├── .gitignore                # Files/folders to ignore in git
└── pytest.ini                # Pytest configuration
```

## Notes

This suite is a simple demonstration and includes 6 small tests to validate basic API functionality. The framework can be extended for larger projects with additional API clients and tests.