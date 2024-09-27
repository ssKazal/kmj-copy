sudo docker-compose -f ../docker-compose.dev.yml run web black .
sudo docker-compose -f ../docker-compose.dev.yml run web isort --recursive .
sudo docker-compose -f ../docker-compose.dev.yml run web python3.9 -m flake8 --ignore E501,W291,E121,E251,W503,F401,F402,F403