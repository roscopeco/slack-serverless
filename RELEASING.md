## Steps

```
bumpver update --tag final
python3 -m build
twine upload -r pypi dist/*
bumpver update --tag dev --no-tag-commit
```

