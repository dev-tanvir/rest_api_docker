REST API using DRF with Docker and Travis-CI using TDD

A project where you can synthesize planetary life using different elemnets! -  Not really!! We are just building API Endpoints


Commands:

    Database migration
        -- docker-compose run --rm app sh -c "python manage.py makemigrations"

    Running Unit tests
        -- docker-compose run --rm app sh -c "python manage.py test"

    Docker

        -- docker-compose build
        -- docker-compose up