# KILIMANJARO SERVICE
``` Dockerizing```

## Installations

```
Create a .env file in kilimanjaro folder, with basic info from demo.env file.
```

```
cd kilimanjaro
```

```sh
sudo docker-compose -f docker-compose.dev.yml build
sudo docker-compose -f docker-compose.dev.yml run web python manage.py makemigrations
sudo docker-compose -f docker-compose.dev.yml run web python manage.py migrate
sudo docker-compose -f docker-compose.dev.yml run --rm web python manage.py initial_setup
sudo docker-compose -f docker-compose.dev.yml up

Now generate `CLIENTAPIKEY` as a superuser from `/admin/core/clientapikey/` for using in request header
```

## Important commands

```bash
# for package installation 
sudo docker-compose -f docker-compose.dev.yml run --rm web poetry add <package name>
```

```bash
# for package installation only in dev dependencies
sudo docker-compose -f docker-compose.dev.yml run --rm web poetry add -D <package name>
```
## Notes 
- Before writing code check [coding rulse](https://github.com/VaidTech/kilimanjaroBE/blob/milestone-2/docs/coding_rules)
- API [documentation](https://github.com/VaidTech/kilimanjaroBE/blob/chat_and_order/docs/swagger-api.yml)