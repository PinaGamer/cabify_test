# Let's play!

In order to launch the server, please execute the following instructions:

1. Create a virtual environment and install the dependencies:

```bash
$ virtualenv -p python3 venv/
$ source venv/bin/activate
$ pip install -r requirements.txt
```

2. Run the server:

```bash
$ cd cabify_test/
$ python manage.py runserver
```

3. Play!

# Admin site

To access to admin site go to the following URL: (http://localhost:8000/admin)
And introduce these credentials:
   * User: *admin*
   * Pass: *c4b1fyr0cks*

There the admin user can add new products to the shop and specify discounts related to those products (only one type of discount per product is available)

# Testing

To run tests execute the following command (you must be under `cabify_test` folder):
```bash
$ python manage.py tests checkout_app
```