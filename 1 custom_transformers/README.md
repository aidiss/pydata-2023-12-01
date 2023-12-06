# Pipeline and custom transformers

## Intro

Sklearn has Pipeline, Feature Union, Column Transformer, Column Selector

It has possibility to create custom transformers.

## Notebook

[original code](https://gitlab.com/v.gruzauskas/inostart-model-training/-/merge_requests/1/diffs)

[custom_transformers.ipynb](custom_transformers.ipynb)

[real.py](real.py)

## Lessons learned

- It is possible to take notebooks and break it down into custom transformers
- We can make it testable.
- Testable https://gitlab.com/aidiss/va-model/-/blob/main/tests/test_column_selector_transformer.py?ref_type=heads
  - https://gitlab.com/aidiss/va-model/-/blob/main/tests/test_cluster_id_to_region.py?ref_type=heads
- Trying to make it simple can make it complicated, better to keep it complex.

## Notes

https://gitlab.com/aidiss/va-model/-/blob/main/src/va_model/preprocessing/pipelines/indicators_pipe.py?ref_type=heads
https://gitlab.com/v.gruzauskas/InoStart-ML-service/-/commit/0026d3a7695efa30d862a48a4532b9cd38a0965b
https://gitlab.com/v.gruzauskas/InoStart-ML-service
https://gitlab.com/v.gruzauskas/inostart-model-training/-/merge_requests?page=6&scope=all&state=merged
