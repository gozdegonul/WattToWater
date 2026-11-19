"""Command line: python -m watttowater [demo|regions|report] ..."""

import argparse
import sys


def main(argv=None):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv or argv[0].startswith("-"):
        argv = ["demo"] + argv            # `python -m watttowater` runs the demo

    p = argparse.ArgumentParser(prog="python -m watttowater",
                                description="Water footprint of compute jobs")
    sub = p.add_subparsers(dest="cmd", required=True)

    d = sub.add_parser("demo", help="train a model live and compare 11 regions")
    d.add_argument("--trees", type=int, default=200, help="number of trees (default 200)")
    d.add_argument("--scale", type=int, default=0, help="also show the total for N runs")
    d.add_argument("--max-stress", type=float, default=None,
                   help="recommend only regions with water stress <= this (0-5)")

    g = sub.add_parser("regions", help="rank regions by water per kWh (policy view)")
    g.add_argument("--max-stress", type=float, default=None,
                   help="policy limit on water stress (0-5)")
    g.add_argument("--kwh", type=float, default=1.0, help="energy of the job (default 1)")

    r = sub.add_parser("report", help="summarise a water log as Markdown")
    r.add_argument("log", nargs="?", default="water_log.csv")
    r.add_argument("--region", default=None, help="region you deploy to")

    args = p.parse_args(argv)

    if args.cmd == "demo":
        from .demo import run
        run(trees=args.trees, scale=args.scale, max_stress=args.max_stress)
    elif args.cmd == "regions":
        from .advisor import print_regions
        print_regions(args.kwh, args.max_stress, unit="L")
    elif args.cmd == "report":
        from .report import summarize, write_github_summary
        md = summarize(args.log, args.region)
        print(md)
        if write_github_summary(md):
            print("\n(written to the GitHub Actions job summary)")


if __name__ == "__main__":
    main()
