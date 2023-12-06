# Pandera, typing

- Sometimes it is hard to know what data is traveling
- There are some good tools for that.



[Functions](https://gitlab.com/aidiss/va-model/-/blob/main/src/va_model/preprocessing/data/database.py) 

## Notebook

[pandera.ipynb](pandera.ipynb)

[schemas.py](schemas.py)

## Lessons learned

- When dealing with tables. It might be hard to unedrstand what data is actaully being passed.
- Pandera helps with that, not only telling but checking.
- Especially useful in IO operations:
  - Use type when loading data from file/database
  - Use types when storing data from file/database
  - Everything in between could be typed too.