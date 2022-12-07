# Another-Light Website
Repo for [another-light.com](https://another-light.com).

## Requirements
- Git
- Docker
- Docker Compose

## Build the project (Linux/Mac)
- Clone the repository.

```bash
git clone git@github.com:theabdullahalam/another-light.git
```

- Change directory into the project.

```bash
cd another-light
```
- Create an `.env` file (You can use the existing sample file as a skeleton).
```bash
cp .env.sample .env
```

- `.env` file modifications:

    **Change the `DJANGO_SUPERUSER_USERNAME` and `DJANGO_SUPERUSER_PASSWORD` variables if needed;** those values are used to create a super user when the project is run.

    If `DEBUG` is set to true, the project will use a local sqlite database, and, as such, the `DB_USER`, `DB_PASSWORD` and `DB_HOST` variables are unused.


- Source the `.env` file and build the docker image.
```bash
source .env
docker compose build
```

## First Run
- Run the the docker image:

```bash
docker compose up
```

- Open `http://localhost:8000/` in a browser to check. You will see a DynamicContent error. This means the setup has worked correctly.
- To fix the error,
    - Browse to `http://localhost:8000/admin`.
    - Login with the credentials you entered in the `.env` file.
    - Go to the `Dynamic Content` page and click on `Add Dynamic Content`.
    - Set the key to `home_section_1`, and set the value to anything you like.
    - Similarly, add two more entries, with the keys `home_section_2` and `home_section_3`.
    - The homepage should now load.

## Subsequently Running the Project
- After the above setup, the project should be up and running. `Ctrl+C` will shut down the docker image.
- The project can be started again with `docker compose up`.
- *Note: The docker compose file contains a service that creates a superuser based on the environment variables. If a superuser with that username already exists, it will print `That username is already taken.` in the logs. This is expected; the project should run just fine.*