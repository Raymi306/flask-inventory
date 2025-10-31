.PHONY: pre
pre:
	ruff format && ruff check

.PHONY: dockerdb-start-test
dockerdb-start-test:
	docker start inventory-test-mariadb

.PHONY: dockerdb-run-test
dockerdb-run-test:
	docker run --detach --name inventory-test-mariadb --env MARIADB_USER=inventory_test_user\
		--env MARIADB_PASSWORD=inventory_test_password --env MARIADB_DATABASE=inventory_test\
		--env MARIADB_RANDOM_ROOT_PASSWORD=1 -p 3307:3306 mariadb:lts 

.PHONY: dockerdb-stop-test
dockerdb-stop-test:
	docker stop inventory-test-mariadb

.PHONY: dockerdb-start-dev
dockerdb-start-dev:
	docker start inventory-dev-mariadb

.PHONY: dockerdb-run-dev
dockerdb-run-dev:
	docker run --detach --name inventory-dev-mariadb --env MARIADB_USER=inventory_dev_user\
		--env MARIADB_PASSWORD=inventory_dev_password --env MARIADB_DATABASE=inventory_dev\
		--env MARIADB_RANDOM_ROOT_PASSWORD=1 -p 3306:3306 mariadb:lts 

.PHONY: dockerdb-stop-dev
dockerdb-stop-dev:
	docker stop inventory-dev-mariadb

.PHONY: dev
dev:
	flask --app app/app run --debug

.PHONY: test
test:
	coverage run -m pytest
