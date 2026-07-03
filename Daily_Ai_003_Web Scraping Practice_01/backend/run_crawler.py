#!/usr/bin/env python3
import argparse
import logging
import sys

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("run_crawler")


def main():
    parser = argparse.ArgumentParser(description="PTT Joke Board Crawler")
    parser.add_argument(
        "--pages",
        type=int,
        default=1,
        help="Number of pages to crawl (max 3, default 1)",
    )
    parser.add_argument(
        "--delay",
        type=int,
        default=2,
        help="Delay between requests in seconds (default 2)",
    )
    args = parser.parse_args()

    if args.pages < 1:
        logger.error("Pages must be at least 1")
        sys.exit(1)
    if args.pages > 3:
        logger.error("Maximum pages allowed is 3, got %d", args.pages)
        sys.exit(1)

    logger.info("Crawler started: pages=%d, delay=%ds", args.pages, args.delay)

    from app.database.init_db import init_db
    from app.services.crawler_service import run_crawler

    init_db()

    result = run_crawler(pages=args.pages, delay=args.delay)

    logger.info(
        "Crawler completed: status=%s, new_articles=%d, new_images=%d, error=%s",
        result["status"],
        result["new_articles"],
        result["new_images"],
        result.get("error_message") or "none",
    )


if __name__ == "__main__":
    main()
