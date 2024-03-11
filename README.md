A basic web application using Django and GraphQL for managing logistics jobs and vehicles. 


This prototype is for a logistics organisation operating within the US only.


To run the application:

`docker compose up --build`

To create test data:

`docker compose exec web poetry run python manage.py test_data create --vehicles 10 --jobs 100`

To destroy test data:

`docker compose exec web poetry run python manage.py test_data destroy`

To start an interactive shell in Django:

`docker compose exec web poetry run python manage.py shell_plus --ipython`

To run tests:

`docker compose exec web poetry run pytest`