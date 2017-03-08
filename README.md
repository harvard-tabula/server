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

# Development tips
* It's pretty convenient to test the API in your browser when developing locally. To do this you'll need to set an alias for `tabula.life` in `/etc/hosts` and then hit the API at `tabula.life:8080/<route>`. This is a bit of a hack around the domain's Google allows you to redirect the user to after receiving oauth.
* Run `python3 manage.py db {migrate | upgrade}` to get your DB up to date. If all hell breaks loose, but you're certain that the current schema is correct, even if alembic doesn't think so, run `python3 manage.py db alembic stamp head`. To populate the tables for local dev run `populate_db.py`. All of these commands need to be run from within the `tabula` container. You can hop on using `docker exec -it 'tabula' bash`.
* Use Postman for local dev of API. https://www.getpostman.com/docs/interceptor_cookies and https://www.getpostman.com/docs/working_with_cookies are relevant.
* To do quick logging, use `import sys; print(variable, file=sys.stderr)`

# Recommended reading 
* https://docs.docker.com/engine/examples/postgresql_service/
* https://realpython.com/blog/python/flask-by-example-part-2-postgres-sqlalchemy-and-alembic/
* https://blog.miguelgrinberg.com/post/designing-a-restful-api-using-flask-restful
* http://bitwiser.in/2015/09/09/add-google-login-in-flask.html
* https://www.postgresql.org/docs/current/static/sql-keywords-appendix.html & http://dba.stackexchange.com/questions/110550/why-cant-i-see-my-table-postgresql-when-i-use-dt-inside-psql
* http://container-solutions.com/understanding-volumes-docker/
* http://alembic.zzzcomputing.com/en/latest/tutorial.html