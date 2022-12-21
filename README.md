# Hackernews Stream

Search hacker news terms, then slack them to a webhook.

[Reference](https://github.com/HackerNews/API)

### Getting started

```shell
cp .env.default .env
./run.sh
```

### Deployment

```shell
# setup post-receive hook in a server
git push
```

### Requirements

- python
- [procsd](https://github.com/vifreefly/procsd) for deployment
