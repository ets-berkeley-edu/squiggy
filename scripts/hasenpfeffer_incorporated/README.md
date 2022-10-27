# Copy Squiggy data from prod to a test environment

![Laverne and Shirley at work](../../src/assets/hasenpfeffer_incorporated.jpg)

Real-world data, from production, in a test environment promotes effective testing.

## Pull data from production

```
./scripts/hasenpfeffer_incorporated/pull-data.sh -d db_connection [-c canvas_hostname [-r replacement_canvas_hostname]] [-a]
```

### Available options
```
     -d      Database connection information in the form 'host:port:database:username'. Required.
     -a      Pull all database tables including the canvas table. Optional.
     -c      Hostname of the Canvas instance for which SuiteC course data should be pulled. Optional, defaults to all instances.
     -r      If provided, all references to Canvas-hosted resources will be changed to this hostname. Optional, requires -c.
```
### Fun facts about _pull-data.sh_

* CSV files are written to the _scripts/hasenpfeffer_incorporated/csv_files_ directory.

## Push data to test environment

```
./scripts/hasenpfeffer_incorporated/push-data.sh -d db_connection [-a] [-i]
```

### Available options
```
     -d      Database connection information in the form 'host:port:database:username'. Required.
     -a      Push all database tables including the canvas table. Optional.
     -i      Mark all courses as inactive after push (may be desirable when populating a test environment). Optional.
```
