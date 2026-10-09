# IMO #327 — Core1A lesson repair, exact mathematical proof

**Review status:** CANDIDATE, TEST-only; academic acceptance **NOT_GRANTED**. This
proposal is stacked directly on existing [draft #312](https://github.com/reallaksh19/Grade9v3.5/pull/312),
which itself carries over the wholly authored five-step concept in
[draft #308](https://github.com/reallaksh19/Grade9v3.5/pull/308).
Neither predecessor is merged or academically certified. The branch must not
be merged to `main` as a second independent canonical package: the intent is
one reviewed successor of #312, with the old #308/#312 duplicate package
writers serialized.

## Source-level mathematical change

The authored common-base teaching concept `MIC-TEST-IMO-G9-COMMON-BASE-RELATION`
now diagnoses a third, genuinely distinct wrong route **at the inverse step**,
not just at the original exponent/factor transformation and positivity test.

- Given `3^(2x)=81=3^4`, the only warranted exponent equation is **`2x=4`**.
- The wrong inference `x=4` is falsified in the *untransformed* authored
  equation: left **19683**, right **6723**.
- Correct `x=2` checks both sides as **243**.
- This new diagnosis joins the existing teaching construction with
  `misconception_indexes=[0,1,2]`. All five complete teaching steps,
  capability identity and author/source boundaries remain unchanged.

## Independent authored-family oracle

The bounded test proves, for real `x` and integer `a>1`, the authored family

`a^(2x+1) = (a^2)^x + k`.

Set `t=a^(2x)>0`, so `(a-1)t=k`. For `a>1`, only `k>0`
has a real solution; then `x=log_a(k/(a-1))/2` is unique. The
oracle verifies three *distinct*, wholly authored instances against their
untransformed equations and exact numerical witnesses:

| Role | Parameters | Solution | Both sides |
|---|---|---|---|
| Core1A worked anchor | `a=3, k=162` | `x=2` | 243 |
| Core1A fresh exit | `a=2, k=64` | `x=3` | 128 |
| Authored Core2A practice | `a=4, k=192` | `x=3/2` | 256 |

Negative offsets and zero have no real solution in this **a>1 family**
because they imply `t<=0`. This is not falsely generalized to bases in
`(0,1)` or to `a=1`; a test explicitly rejects invalid oracle bases.
Further fractional real inputs verify the exponent-offset factor law.
Mutation tests reject removal of the new diagnostic, wrong inversion
repair and false promotion of authored practice to genuine source Core2.

Run the focused gate with:

```sh
python -m unittest discover -s tests -p 'test_imo_327_core1a_math_proof.py' -v
```

## Actual remaining acceptance barriers

This proves source-level math and candidate-source integrity only.
It **does not** certify project package-schema validation, the renderer,
printed pages, actual interactive attempt/repair, QRT acceptance, human
academic review, accessibility, Owner release, original SOF question
custody/rights or homepage deployment. All source question text/figures
remain absent; the related SOF Q26 research family does NOT become source
Core2. Product role actions on the future Index Laws homepage remain held
until those gates independently pass.

V3.1 remains the active selected protocol and the checked-in #212 lease
disagrees with the closed provider issue. The requested pinned V3.2
pre-materialization graph is [draft #329](https://github.com/reallaksh19/Grade9v3.5/pull/329);
its successful structural precheck is **not** the official Common
`decompose-check`, and no F02 child admission or release authority is implied.
