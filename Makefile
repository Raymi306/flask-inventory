.PHONY: pre
pre:
	ruff format && ruff check

.PHONY: dockerdb-start
dockerdb-start:
	docker start inventory-test-mariadb

.PHONY: dockerdb-run
dockerdb-run:
	docker run --detach --name inventory-test-mariadb --env MARIADB_USER=inventory_test_user\
		--env MARIADB_PASSWORD=inventory_test_password --env MARIADB_DATABASE=inventory_test\
		--env MARIADB_RANDOM_ROOT_PASSWORD=1 -p 3306:3306 mariadb:lts 


.PHONY: dockerdb-stop
dockerdb-stop:
	docker stop inventory-test-mariadb
