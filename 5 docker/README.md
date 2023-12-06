# Docker, GPU

- Windows, Linux, Docker GPU
- We want to be able to train, tune things on GPU
- We want to be able to run on servers
- We dont want to pay too much for those


Let's create a docker image that has GPU support and all libs we need.
Let's have different images for training/tuning and serving model.

*A lot of pain with multiple repositories*

The final view. Single docker image that is able to read custom python requirements.

[dockerfile](dockerfile)

```py
# requirements.txt training repo
matplotlib
jupyter
```

```py
# requirements.txt serving repo
fastapi~=0.78.0
uvicorn~=0.15.0
sympy
plotly
xlsxwriter==3.0.3
```

## Lessons learned

- Drivers are breaking https://github.com/microsoft/LightGBM/issues/5572
- Maybe just pay the money? Would it be easier?
- Hooray it can be solved by downgrading a version!
- Downgrade stuff is complicated. https://bbs.archlinux.org/viewtopic.php?pid=2059397#p2059397
- https://wiki.archlinux.org/title/Dynamic_Kernel_Module_Support



https://gitlab.com/v.gruzauskas/inostart-model-training/-/blob/main/requirements.txt?ref_type=heads


