# References

* [Compose file reference](https://docs.docker.com/compose/compose-file/)
* [Dockerfile reference](https://docs.docker.com/engine/reference/builder/)

# Usage

```
# build container
docker-compose build

# start container, run default CMD
docker-compose up

# start container, run bash instead of default CMD
docker-compose run --rm web bash
```

# Debugging tips
```
# get onto the box 
docker exec -it "tabula" bash

# install other deps ... e.g.
apt-get install libpq-dev
pip3 install psycopg2
```
