# document-analyser
Python back-end REST API to extract data from uploaded resumes.

Install python 3.11.6: [https://www.python.org/downloads/](https://www.python.org/downloads/release/python-3116/)
Make sure to use this version (3.11.6), newer versions give conflicts with some of the depencendies.

Install pip (package manager): [https://pip.pypa.io/en/stable/installation/](https://pip.pypa.io/en/stable/installation/)

## Setup virtual environment
Setup the virtual environment for this repository so that on each instance the same libraries are used.
More info, see [online documentation](https://docs.python.org/3/library/venv.html).

#### Create
Create the initial required files for a virtual environment.
run command: `python -m venv .venv`

#### Activate 
Activate the virtual environment, this is required for installing libraries or running the application.
The exact commands differ per OS and terminal, find the correct command to run [here](https://docs.python.org/3/library/venv.html#how-venvs-work).

## Pip libraries
The libraries needed for this project are specified in the [requirements file](\requirements.txt). 

### Install or Update
When first checking out the repository, or when the requirements are changed, these libraries will need to be installed. For this run the command:
`pip install -r requirements.txt`

### Edit
When installing a new library or or changing the version, update the requirements.txt file by running:
`pip freeze > requirements.txt`

### Pre-commit

Execute `pre-commit install` to install git hooks in your .git/ directory. 
After installation, two pre-commit hooks will be triggered on each commit:
- [black](https://black.readthedocs.io/en/stable/): Automatic Code Formatter
- [flake8](https://flake8.pycqa.org/en/latest/): Style Guide Enforcement

More information is available on their [website](https://pre-commit.com/).

## Run application

### Development Server
To run the development server execute the command:
`python run_server.py -m -v -p 5000`
The main difference here is that it will not communicate with the azure services.
This allows for the application to be executed without the necessary environment variables.

For more info about the command line arguments, run:
`python run_server.py --help`

##### DO NOT USE:
`flask --app document_analyzer/api run`
Running the application with this command is not compatible with `argparser`. Causing the application to fail when it tries to determine the argument values.

### Production Server

Run `python run_server.py`

#### Environment variables
In order to run the application in production mode, some environment variables will need to be set. 
These being: 
- `AZURE_COGS_KEY`: The key from the azure cognitive services subscription.
- `OPENAI_API_KEY`: the key from the azure openai subscription. 

They are necessary for communication with the azure resources.
Restart might be required for these environment variables to be detected by python.

### Docker

#### Stub

For a stubbed configured container go to `/docker/stub` and run:

    docker compose up -d

#### Azure

For an azure configured container. Go to `/docker/azure` and apply following setup:

Create under project root a file named `.azure`, with following content.
    
    AZURE_COGS_KEY=
    OPENAI_API_KEY=

The keys for azure cognitive service (_AZURE_COGS_KEY_) and azure openai api (_OPENAI_API_KEY_) can be requested, contact Technical Product Owner (Martijn Haex) or the DevOps team (Maxim Rudenko, Martijn Haex or Bjorn Monnens).

    docker compose up -d

## Execute tests
To run the tests, make sure the virtual environment is activated first. 
Once activated, run the command:
`pytest` or `python -m pytest`
This will discover the tests recursively based on naming conventions.
For test files this means they have to be prepended with 'test_' or appended with '\_test'.
For test methods this means they have to be prepended with 'test_'.

### Include coverage
Run `coverage run -m pytest`.

For getting a HTML report, run `coverage html`. The report will be available in `htmlcov/index.html`.