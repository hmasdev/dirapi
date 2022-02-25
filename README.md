# DirAPI: Directory to API :open_file_folder:

DirAPI provides a **simple** method to create **an API associated with a directory structure**.

For example, suppose that you want an API to load json files in the following directories:

    - data/
        - datasource1/
            - dataset1.json
            - dataset2.json
        - datasource2/
            - master.json

DirAPI provides a method to create a class like the following class:

```python
class Data:
    class Datasource1:
        class Dataset1:
            def load(self):
                ...
        class Dataset2:
            def load(self):
                ...
    class Datasource2:
        class Master:
            def load(self):
                ...
```

Of course, `load` is a method which you want to use.

## Installation

### Requirements

- Python >= 3.7

### User Instllation

```bash
pip install git+https://github.com/hmasdev/dirapi.git@master
```

### How to use

In the above example case, you can DirAPI as follows.

```python
>>> from dirapi import create_api, help_tree
>>> import json
>>> import os
>>> # the path to data directory
>>> root_path: str = "./data"
>>> # create Data API
>>> Data = creat_api(root_path, {"load": lambda path: json.load(open(path))})
>>> # show the structure of Data
>>> help_tree(Data)
Data
Data.Datasource1
Data.Datasource1.Dataset1
Data.Datasource1.Dataset1.load
Data.Datasource1.Dataset2
Data.Datasource1.Dataset2.load
Data.Datasource2.Master
Data.Datasource2.Master.load
```

There are more information in [./examples](./examples) .

## Contribution Guide

### Requirement

- Python >= 3.7
- pipenv

### Setup

```bash
$ git clone https://github.com/hmasdev/dirapi.git
$ cd dirapi
$ pipenv install --dev
```

### Issues

- For any bugs, use [BUG REPORT](https://github.com/hmasdev/diraapi/issues/new?assignees=&labels=bug&template=bug_report.md&title=%5BBUG%5D) to create an issue.

- For any enhancement, use [FEATURE REQUEST](https://github.com/hmasdev/dirapi/issues/new?assignees=&labels=enhancement&template=feature_request.md&title=) to create an issue.

- For other topics, create an issue with a clear and concise description.

### Pull Request

1. Fork (https://github.com/hmasdev/dirapi/fork);
2. Create your feature branch (git checkout -b feautre/xxxx);
3. Test codes according to Test Subsection;
4. Commit your changes (git commit -am 'Add xxxx feature);
5. Push to the branch (git push origin feature/xxxx);
6. Create new Pull Request

### Test

```bash
$ pipenv run flake8
$ pipenv run mypy .
$ pipenv run pytest
```

## LICENSE

[MIT](https://github.com/hmasdev/dirapi/tree/main/LICENSE)

## Authors

[hmasdev](https://github.com/hmasdev)
