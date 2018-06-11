# -*- coding: utf-8 -*-

from __future__ import absolute_import

from argparse import ArgumentParser

from bot import run_bot


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument("-w", "--webhook",
                        action="store_true", dest="webhook",
                        help="use webhook instead polling")

    args = parser.parse_args()

    run_bot(use_webhook=args.webhook)
