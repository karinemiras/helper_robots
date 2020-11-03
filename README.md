Installation
============

- Install SIC: https://socialrobotics.atlassian.net/wiki/spaces/CBSR/pages/260276225/SIR+Manual
- Request kikoagent-iajdfl-9d037d057933.json from the VU server and save the file in the miscellaneous folder
- Install Postgresql: https://www.postgresql.org/download/
- Install psycopg2 and inflect
- Create a new database called kikoagent in Postgresql
- Load the Postgresql backup located in miscellaneous:
     /usr/local/opt/libpq/bin/pg_restore -U postgres -d kikoagent postgres_structure.dump
- Update the table corona_info inside kikoagent with up-to-date information
- Use the script experiment_1.py to run and test the system