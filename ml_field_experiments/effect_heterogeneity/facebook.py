import argparse
from pathlib import Path

import pandas as pd

from ml_field_experiments.datasets import Facebook
from ml_field_experiments.effect_heterogeneity.methods.gp import (
    GPTest,
)
from ml_field_experiments.effect_heterogeneity.methods.ols import (
    OLSTest,
    OLSLassoTest,
    OLSInteractTest,
    OLSInteractLassoTest,
    FTest,
)
from ml_field_experiments.effect_heterogeneity.methods.nn import NNTest
from ml_field_experiments.effect_heterogeneity.methods.grf import GRFTest
from ml_field_experiments.effect_heterogeneity.methods.svm import SVRTest

METHODS = {
    "GP": GPTest,
    "OLS": OLSTest,
    "OLS-Lasso": OLSLassoTest,
    "OLS-Interact": OLSInteractTest,
    "OLS-Interact-Lasso": OLSInteractLassoTest,
    "SVM": SVRTest,
    "GRF": GRFTest,
    "NN": NNTest,
    "FTest": FTest,
}


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--method",
        type=str,
        required=True,
        help="ATE estimation method",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="experiments/",
        help="base directory to write results",
    )
    parser.add_argument(
        "--data-dir",
        type=str,
        default="data/",
        help="location of dataset",
    )
    parser.add_argument(
        "--n",
        type=int,
        default=1660,
        help="size of sample",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=1331,
        help="random seed",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    r = {
        "method": [],
        "n": [],
        "p(t)": [],
        "ate": [],
        "p-val-ate": [],
        "p-val-het": [],
    }
    method = METHODS[args.method](w_hat=1 / 3)
    dataset = Facebook(
        data_dir=args.data_dir,
        n=args.n,
    )
    x, z, y = dataset.sample(seed=args.seed)
    results = method.run(x=x, z=z, y=y)
    r["method"].append(args.method)
    r["n"].append(args.n)
    r["p(t)"].append(1 / 3)
    r["ate"].append(results["ate"])
    r["p-val-ate"].append(results["p-val-ate"])
    r["p-val-het"].append(results["p-val-het"])

    df = pd.DataFrame(r)
    exp_str = f"n={args.n}_seed={args.seed}"
    output_dir = (
        Path(args.output_dir) / "CATE" / "Facebook" / f"{args.method}" / exp_str
    )
    output_dir.mkdir(exist_ok=True, parents=True)
    df.to_csv(output_dir / "results.csv")


if __name__ == "__main__":
    main()
