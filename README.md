# Website Name

## Overview

This is a sample website built with Flask that allows users to browse courses, projects, and more. Users can also register and log in to access additional features like adding items to the shopping cart, viewing the cart, and checking out.

## Features

### Public Routes

- `/`: Home page that provides an overview of the website.
- `/about`: Information about the website and its purpose.
- `/courses`: Browse available courses.
- `/portfolioprojects`: View various portfolio projects.
- `/cs`: Information related to computer science topics.
- `/more`: Additional resources and information.
- `/project1.html`, `/project2.html`, `/project3.html`: Individual pages for specific projects.

### Secure Routes

- `/buy`: Allows logged-in users to add items to the shopping cart and proceed to checkout.
- `/cart`: Displays the user's shopping cart with the option to remove items.
- `/history`: Shows the history of transactions for the logged-in user.

### User Authentication

- `/register`: Allows new users to register an account by providing a username and password.
- `/login`: Existing users can log in using their credentials.
- `/logout`: Logs out the user and redirects them to the home page.

### Forgotten Password

- `/forgottenpassword`: Allows users to reset their forgotten password. A temporary password or token is sent to the user's email for resetting the password.

## Prerequisites

- Python 3.x
- Flask web framework
- SQLite database

## Getting Started

1. Clone the repository: `git clone https://github.com/your_username/website.git`
2. Navigate to the project directory: `cd website`
3. Install the required packages: `pip install -r requirements.txt`
4. Set environment variables (if required) or update the `app.secret_key` in `app.py`.
5. Run the application: `python app.py`
6. Access the website in your web browser: `http://localhost:5000`

## Database

The website uses a SQLite database to store user information, inventory, and transaction history.

## Acknowledgements

This website is built with Flask and uses the CS50 library for SQLite database integration.

## License

This project is licensed under the [cs50 license](https://github.com/