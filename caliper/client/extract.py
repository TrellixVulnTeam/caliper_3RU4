__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2020-2021, Vanessa Sochat"
__license__ = "MPL 2.0"

from caliper.metrics import MetricsExtractor
from caliper.managers import get_named_manager
import logging
import os

logger = logging.getLogger("caliper.client")


def main(args, extra):

    # Ensure that all metrics are valid
    client = MetricsExtractor(quiet=True)
    metrics = args.metric.split(",")

    # If asking for all, we will do all regardless of other specifications
    if "all" in metrics:
        metrics = ["all"]

    for metric in metrics:
        if metric == "all":
            continue
        if metric not in client.metrics:
            logger.exit("%s is not a known metric." % metric)

    # prepare top level output directory
    outdir = args.outdir or os.getcwd()

    # Now parse the package names and do the extraction!
    for package in args.packages:
        uri, package = package.split(":")  # pypi:sif
        try:
            manager = get_named_manager(uri, package)
        except NotImplementedError:
            logger.exit("%s is not a valid package manager uri." % package)

        # Create a client to interact with
        client = MetricsExtractor(manager, quiet=True)

        # Do the extraction
        for metric in metrics:
            if metric == "all":
                client.extract_all()
            else:
                client.extract_metric(metric)

        # Save results to files
        client.save_all(outdir, force=args.force)

        # Cleanup, unless disabled
        if not args.no_cleanup:
            client.cleanup(force=True)

    print("Results written to %s" % outdir)
