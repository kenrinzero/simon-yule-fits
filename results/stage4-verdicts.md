### chicago (n = 278)

| Model | Params | LL | ΔAIC | X² obs | X² p | KS p | vs Yule | stat | p | verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| yule | ρ = 1.018 | -568.43 | 8.6 | 22.6 | 0.016 | 0.116 | — | — | — | — |
| zeta | s = 1.801 | -573.35 | 18.5 | 29.7 | 0.000 | 0.014 | Vuong | +3.60 | 0.000317 | Yule favoured |
| logseries | θ = 0.9049 | -571.03 | 13.8 | 21.1 | 0.014 | 0.000 | Vuong | +0.39 | 0.694 | indistinguishable |
| sichel | θ = 0.9801 | -569.76 | 11.3 | 31.7 | 0.000 | 0.000 | Vuong | +0.58 | 0.562 | indistinguishable |
| waring | ρ, c = 1.353, 0.62 | -566.14 | 6.1 | 19.4 | 0.016 | 0.044 | LR | +4.59 | 0.0322 | rival favoured |
| cutoff | ρ, b = 0.6156, 0.9674 | -563.42 | 0.6 | 15.2 | 0.076 | 0.552 | LR | +10.03 | 0.000769 | rival favoured |
| enb | r, θ = -0.3019, 0.9532 | -563.11 | 0.0 | 13.9 | 0.092 | 0.814 | Vuong | -2.14 | 0.0321 | rival favoured |
| gigp | ν, α, θ = -0.3019, 1e-06, 0.9532 (bound) | -563.11 | 2.0 | 13.9 | 0.074 | 0.720 | Vuong | -2.14 | 0.0321 | rival favoured |

### chem (n = 6,891)

| Model | Params | LL | ΔAIC | X² obs | X² p | KS p | vs Yule | stat | p | verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| yule | ρ = 1.277 | -11681.29 | 73.3 | 45.2 | 0.000 | 0.000 | — | — | — | — |
| zeta | s = 1.966 | -11705.31 | 121.4 | 28.8 | 0.000 | 0.000 | Vuong | +2.94 | 0.00325 | Yule favoured |
| logseries | θ = 0.8729 | -12247.29 | 1205.3 | 799.4 | 0.000 | 0.000 | Vuong | +9.95 | 2.57e-23 | Yule favoured |
| sichel | θ = 0.9688 | -11647.26 | 5.3 | 11.6 | 0.246 | 0.138 | Vuong | -2.66 | 0.00787 | rival favoured |
| waring | ρ, c = 1.196, -0.104 | -11678.20 | 69.2 | 27.0 | 0.000 | 0.000 | LR | +6.18 | 0.0129 | rival favoured |
| cutoff | ρ, b = 1.178, 0.9927 | -11670.91 | 54.6 | 56.3 | 0.000 | 0.000 | LR | +20.76 | 2.61e-06 | rival favoured |
| enb | r, θ = -0.4924, 0.9675 | -11646.97 | 6.7 | 10.1 | 0.266 | 0.056 | Vuong | -2.65 | 0.00793 | rival favoured |
| gigp | ν, α, θ = -0.5837, 0.2146, 0.974 | -11642.62 | 0.0 | 4.1 | 0.854 | 0.652 | Vuong | -3.97 | 7.05e-05 | rival favoured |

### physicists (n = 1,325)

| Model | Params | LL | ΔAIC | X² obs | X² p | KS p | vs Yule | stat | p | verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| yule | ρ = 1.472 | -2033.15 | 7.2 | 16.0 | 0.064 | 0.028 | — | — | — | — |
| zeta | s = 2.054 | -2047.88 | 36.7 | 35.5 | 0.000 | 0.000 | Vuong | +4.16 | 3.18e-05 | Yule favoured |
| logseries | θ = 0.8097 | -2083.16 | 107.2 | 89.1 | 0.000 | 0.000 | Vuong | +3.61 | 0.000312 | Yule favoured |
| sichel | θ = 0.9413 | -2031.27 | 3.4 | 21.8 | 0.010 | 0.008 | Vuong | -0.53 | 0.596 | indistinguishable |
| waring | ρ, c = 1.624, 0.1654 | -2032.21 | 7.3 | 16.1 | 0.036 | 0.022 | LR | +1.88 | 0.17 | no significant improvement over Yule |
| cutoff | ρ, b = 1.2, 0.9712 | -2028.69 | 0.3 | 14.7 | 0.084 | 0.154 | LR | +8.93 | 0.0014 | rival favoured |
| enb | r, θ = -0.4337, 0.9241 | -2028.55 | 0.0 | 14.4 | 0.080 | 0.042 | Vuong | -1.33 | 0.185 | indistinguishable |
| gigp | ν, α, θ = -0.568, 0.2955, 0.939 | -2027.89 | 0.7 | 13.9 | 0.068 | 0.056 | Vuong | -2.18 | 0.0294 | rival favoured |

### eldridge (n = 6,002)

| Model | Params | LL | ΔAIC | X² obs | X² p | KS p | vs Yule | stat | p | verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| yule | ρ = 1.054 | -11848.43 | 8.3 | 23.5 | 0.006 | 0.000 | — | — | — | — |
| zeta | s = 1.832 | -11908.44 | 128.4 | 125.3 | 0.000 | 0.000 | Vuong | +7.51 | 6.14e-14 | Yule favoured |
| logseries | θ = 0.959 | -13321.15 | 2953.8 | 1539.2 | 0.000 | 0.000 | Vuong | +6.73 | 1.74e-11 | Yule favoured |
| sichel | θ = 0.9946 | -12038.80 | 389.1 | 282.5 | 0.000 | 0.000 | Vuong | +7.21 | 5.6e-13 | Yule favoured |
| waring | ρ, c = 1.141, 0.1485 | -11843.26 | 0.0 | 11.2 | 0.212 | 0.454 | LR | +10.34 | 0.0013 | rival favoured |
| cutoff | ρ, b = 1.051, 0.9999 | -11848.20 | 9.9 | 23.2 | 0.012 | 0.002 | LR | +0.45 | 0.25 | no significant improvement over Yule |
| enb | r, θ = -0.5122, 0.9951 | -12037.52 | 388.5 | 296.1 | 0.000 | 0.000 | Vuong | +7.73 | 1.08e-14 | Yule favoured |
| gigp | ν, α, θ = -0.9309, 1.04, 0.9998 | -11848.14 | 11.8 | 22.5 | 0.006 | 0.004 | Vuong | -0.05 | 0.957 | indistinguishable |

### econometrica (n = 721)

| Model | Params | LL | ΔAIC | X² obs | X² p | KS p | vs Yule | stat | p | verdict |
|---|---|---|---|---|---|---|---|---|---|---|
| yule | ρ = 1.518 | -997.74 | 0.2 | 28.5 | 0.006 | — | — | — | — | — |
| zeta | s = 2.07 | -1003.46 | 11.6 | 41.5 | 0.000 | — | Vuong | +2.05 | 0.0401 | Yule favoured |
| logseries | θ = 0.7693 | -1013.32 | 31.3 | 60.7 | 0.000 | — | Vuong | +2.18 | 0.0294 | Yule favoured |
| sichel | θ = 0.9306 | -998.65 | 2.0 | 28.4 | 0.004 | — | Vuong | +0.42 | 0.672 | indistinguishable |
| waring | ρ, c = 1.614, 0.09434 | -997.59 | 1.9 | 27.9 | 0.000 | — | LR | +0.30 | 0.585 | no significant improvement over Yule |
| cutoff | ρ, b = 1.303, 0.9742 | -997.23 | 1.2 | 26.0 | 0.002 | — | LR | +1.01 | 0.158 | no significant improvement over Yule |
| enb | r, θ = -0.4067, 0.8992 | -996.65 | 0.0 | 22.7 | 0.008 | — | Vuong | -0.58 | 0.564 | indistinguishable |
| gigp | ν, α, θ = -0.4068, 1e-06, 0.8991 (bound) | -996.65 | 2.0 | 22.7 | 0.006 | — | Vuong | -0.58 | 0.564 | indistinguishable |

```json
{
 "predictions": {
  "P7a": {
   "holds": false,
   "aic_enb": 23297.942860999075,
   "aic_yule": 23364.572288216386,
   "enb_params": [
    -0.4924242355193899,
    0.9675204877629645
   ]
  },
  "P12": {
   "holds": true,
   "z": {
    "chem": 2.942641337626946,
    "physicists": 4.1604442472125145
   }
  },
  "P13": {
   "holds": true,
   "x2_p": 0.0
  },
  "P14": {
   "holds": true,
   "theta_mle": 0.9687590057528902,
   "theta_mean_match": 0.9687590045432841,
   "target": 0.96876,
   "grade_mle": "reproduced",
   "grade_mean_match": "reproduced",
   "grade": "reproduced",
   "exploratory_x2": {
    "cells": 32,
    "last_single_cell": 31,
    "x2": 21.194377279181406,
    "dof": 30,
    "p": 0.8817115275291968
   }
  },
  "P15": {
   "holds": true,
   "best": "gigp"
  }
 },
 "reasonably_good": {
  "chicago": {
   "yule_x2_p": 0.016,
   "reasonably_good": "fails",
   "yule_daic": 8.64929013778169,
   "yule_within_2_of_best": false,
   "best": "enb"
  },
  "chem": {
   "yule_x2_p": 0.0,
   "reasonably_good": "fails",
   "yule_daic": 73.3412377734603,
   "yule_within_2_of_best": false,
   "best": "gigp"
  },
  "physicists": {
   "yule_x2_p": 0.064,
   "reasonably_good": "holds",
   "yule_daic": 7.207424668046315,
   "yule_within_2_of_best": false,
   "best": "enb"
  },
  "econometrica": {
   "yule_x2_p": 0.006,
   "reasonably_good": "fails",
   "yule_daic": 0.17147967772621087,
   "yule_within_2_of_best": true,
   "best": "enb"
  }
 },
 "bootstrap_failures": {
  "chicago": {},
  "chem": {},
  "physicists": {},
  "eldridge": {},
  "econometrica": {}
 }
}
```
