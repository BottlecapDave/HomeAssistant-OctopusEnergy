

## asdf

We use `asdf` to manage plugins. 

```bash
asdf plugin-add nodejs
asdf plugin-add python
sudo apt update & sudo apt upgrade
sudo apt install libffi-dev libncurses5-dev zlib1g zlib1g-dev libssl-dev libreadline-dev libbz2-dev libsqlite3-dev
```

## Python

We use pip to manage dependencies. These are needed in order to run tests

```bash
pip install -r requirements.test.txt
```

## Tests

Included are a few unit tests, located in `./tests`. To run them

```bash
API_KEY=<<OCTOPUS_API_KEY>> python -m pytest tests
```