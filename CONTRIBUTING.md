

## asdf

We use `asdf` to manage plugins. 

```
asdf plugin-add nodejs
asdf plugin-add python
sudo apt update & sudo apt upgrade
sudo apt install libffi-dev libncurses5-dev zlib1g zlib1g-dev libssl-dev libreadline-dev libbz2-dev libsqlite3-dev
```

## Tests

Included are a few unit tests, located in `./tests`. To run them

```
API_KEY=<<OCTOPUS_API_KEY>> python -m pytest tests
```