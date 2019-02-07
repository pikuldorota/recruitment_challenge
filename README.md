# About

This is repository with solutions to recruiting challenges. There were two tasks to perform and for each I've created a separate file with solution. They are to be found in source folder. There is also requirements.txt file with list of packages used to solve problems. Data folder consists of example csv used for testing and pictures used in this file.

# CSV report processing

### About

Solution for this problem is script CSV_report_processing.py. It runs directly from the shell. If run with -h option it shows below help output.

![Alt text](./data/csv_help_output.png)

Required options include input and output file. Input file is the one with unprocessed data and output is the place where processed data should be saved. There is additional option verbose for more informative output. With this options all warnings and errors are put on standard output and to stderr but there is also some information show. This information are for user to know where the script is with processing data.

### Warnings and errors

There are several warnings and errors possible. Below is a list with justification why they are recognized as either warning or critical error.

##### Warnings

- **N rows were removed during filtering** - as file may come corrupted, some rows may be removed from dataset because of that. However stopping execution because some rows are corrupted seems too much so it is a warning.

- **State xyz not found** - it's been stated that it is not an error in the task description but I think it deserves a warning. If there are too many unknown states then it may corrupt further analysis of data so this warnings may be good to find out that somewhere someone makes spelling error with some state.

- **Input and output file is the same file** - it's a warning as it may be wrong to save to the same place where data are purchased from as we can lose them in their original form. However with big amounts of data saving the space is more important and that's why I decided to make it a warning

##### Errors

- **Input file doesn't exist: file_name** - although it's stated that the standard input is a file, someone may make a simple spelling error when using the script. As without input file further execution makes no sense it is a critical error

- **Output file exists and is not empty** - if output file exists and is not empty it may corrupt some already valuable data. That's why I think it's a critical error. Note that this won't occur when input and output files are the same file

# Web crawler

### About

Solution is in file web_crawler.py and it consists of main site_map(url) function but also some helper function for reaching higher readability of code. It goes as deep as it is possible looping as long as there are new unexplored links. For each link there may be:
- a link that is not a subsite to given url domain - it is simple omitted
- a link that is a subsite and is unreachable - it is added to the dictionary with note "Page not reachable"
- a link that is a subsite and is reachable - it is added to the dictionary with info about it's title and links on it