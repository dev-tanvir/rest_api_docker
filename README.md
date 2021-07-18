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

    Authorization
        -- used ModHeader google chrome extension
        -- add user token - API: /api/user/token/
        -- copy the token, paste in ModHeader ( Request Headers --> Authorization and put in the field { Token 'user_token' })

        N.B. - Use ModHeader carefully, it may impact on other sites i.e. youtube, gmail etc