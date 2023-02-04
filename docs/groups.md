# Groups

## Garbage Hierarchy

When making your own metrics for this app, it is useful to know how it internally organizes the data and the tests ran against it. The program operates on three levels, organized from largest to smallest.

### 1. Logs

The base level is the logs that come directly from your robot and converted into a python-friendly [pandas](https://pandas.pydata.org/) dataframe, which is a table like format. This table consists of an index column, along with two other columns. Each row in the table is one log entry. The first index column is the microsecond timestamp included in the log. The second and third columns are the log key and its value, respectivly.

### 2. Groups

Once the log file has been processed, the program will scan a chosen directory (`./groups/` by default) for `.py` files. Each .py file in this directoty is known as a group. A group is similar to the subsystems on your robot in that they act as containers for the "hardware" (metrics) underneath. In fact, having one group for each of the subsystems on your robot is a great way to organize the groups that you make.

Every group must have a function named `defineMetrics()` that takes no arguments and returns an object of type `Dict[str, Callable[[pd.DataFrame], Tuple[int, str]]]`. This dictionary services as a mapping between the names of the metrics in this group and the functions that compute them.

### 3. Metrics

A metric is an individual test that is ran against your log file. All metrics are functions that take a `pd.DataFrame` as its only input and returns a tuple with type `Tuple[int, str]`. The `int` part of the tuple should be a number 0-2 representing the severity level of this metric to be displayed on the dashboard:

0. Green. No action is needed.
1. Yellow. Action should be taken.
2. Red. Action is needed.

The second part of a tuple is a string that reprenents the value of this metric. This can be whatever you want it to be: a number with a unit, additional help information, or anything that can be put into a string.

## Creating Your Own Groups/Metrics

A good idea would be to copy one of the existing groups in this repo's `groups` folder and modify it to suit your needs. Take note of the following:

- The `defineMetrics()` function at the top of the file.
- How to filter out one key from the whole table by using `robotTelemetry[robotTelemetry["Key"] == "name_of_key"]`
- That using `["Value"]` on the dataframe from above is needed to get just the values.
- How metrics check to make sure that keys exist by checking `pd.DataFrame.empty` and returning `-1, "metric_not_implemented"` if it's true.
- How conversion functions are often needed to turn the `object` type data into a different type.
- How to create new columns by accessing the dataframe like a dictionary.
- The extensive use of [pandas](https://pandas.pydata.org/), [numpy](https://numpy.org/), and [scipy](https://scipy.org/) to make calculations.
