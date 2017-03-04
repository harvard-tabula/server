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

# Recommended reading 
* https://docs.docker.com/engine/examples/postgresql_service/
* https://realpython.com/blog/python/flask-by-example-part-2-postgres-sqlalchemy-and-alembic/
* https://blog.miguelgrinberg.com/post/designing-a-restful-api-using-flask-restful
* http://bitwiser.in/2015/09/09/add-google-login-in-flask.html
* https://www.postgresql.org/docs/current/static/sql-keywords-appendix.html & http://dba.stackexchange.com/questions/110550/why-cant-i-see-my-table-postgresql-when-i-use-dt-inside-psql
