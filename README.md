# backend-websocket-pool
Scalable solution for broadcasting jobs from nodes to workers and transferring solutions from workers to nodes.

## Architecture

### node_server
Node connects to the `node_server`.

Connection opening its own Kafka consumer (`solution` topic) to read solutions data and send it to the node (if eligible).

Job received from node transfers to RabbitMQ (`job` exchange).

### process_job_worker
Job is being processed by `process_job_worker` (`job.persist_and_broadcast` queue).

Job stores to Postgres database (`job` table) and (if it was not processed yet) transfers to Kafka (`job` topic).

### worker_server
Worker connects to the `worker_server`.

Connection waits for `welcome` package from worker to store its data to Postgres database (`worker` table).

Connection opening its own Kafka consumer (`job` topic) to read jobs data and send it to the worker (if eligible).

Solution received from worker transfers to RabbitMQ (`solution` exchange).

### process_solution_worker
Solution is being processed by `process_solution_worker` (`solution.persist_and_broadcast` queue).

Solution stores to Postgres database (`solution` table) and (if it was not processed yet) transfers to Kafka (`solution` topic).

## Environment
Python 3.10+ only.

Possible environment organization is described in `docker-compose.yml`. 
Please note that the config of `kafka` service should be adjusted for your needs.

Dockerfiles and requirements for each app are stored at `_etc` folder.

Tests and management scripts (such as db migrations runner) are stored at `misc` folder.

### Local development example scenario
- set up python, create virtual environment, set up required packages (`_etc/full_requirements.txt`)
- run `docker-compose --profile environment up` to run environment in compose
- run `misc/setup_local_environment.py`
- copy `.env.local_e2e_test` to the root folder, rename it to `.env`
- run any server and check it is working

### Running local_e2e_test
- set up python, create virtual environment, set up required packages (`_etc/full_requirements.txt`)
- run `docker-compose --profile environment up` to run environment in compose
- run `misc/setup_local_environment.py`
- run `misc/local_e2e_test.py`

## TODO
- update kafka producer/consumer code with SSL cert usage
- add non-root user for docker containers
- persist worker connection and disconnection by separate agent, not in `worker_server`.
- determine "hanged" worker connections (more than one stored connection without "disconnected_at") and finish the oldest ones by setting up "disconnected_at" to the time of the latest (but earlier than the next connection time) solution of this worker
