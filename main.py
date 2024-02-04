from __future__ import annotations

import requests
import re
import multiprocessing as mp
import time

from dataclasses import dataclass
from argparse import ArgumentParser
from tqdm import tqdm


@dataclass
class Wiki:
    parents: list[Wiki]
    link: str


def good_link_part(link_part: str) -> bool:
    bad_strs = [".", ":", "Main_Page"]
    for bad_str in bad_strs:
        if bad_str in link_part:
            # Found link to image or main page, skip.
            return False
    return True


def get_wiki_branches(wiki: Wiki, session: requests.Session) -> list[Wiki]:
    html = session.get(wiki.link).text

    wiki_link_re = re.compile("<a href=\"(/wiki/.*?)\"")

    wiki_branches = []
    for match in wiki_link_re.finditer(html):
        link_part = match.group(1)
        if not good_link_part(link_part):
            continue

        link = "https://en.wikipedia.org" + link_part
        wiki_branch = Wiki(wiki.parents + [wiki], link)
        wiki_branches.append(wiki_branch)

    return wiki_branches


if __name__ == "__main__":
    # Create arg parser.
    parser = ArgumentParser()
    parser.add_argument(
        "-s", "--start",
        default="https://en.wikipedia.org/wiki/Toilet_paper_orientation",
        help="starting wikipedia link"
    )
    parser.add_argument(
        "-e", "--end",
        default="https://en.wikipedia.org/wiki/Adolf_Hitler",
        help="ending wikipedia link"
    )

    # Parse args.
    args = parser.parse_args()
    
    start_wiki = Wiki(parents=[], link=args.start)
    end_wiki_link = args.end

    start_time = time.time()

    # Store past and currently exploring wikis.
    past_wiki_links = set()

    explore_wikis = [start_wiki]
    explore_wiki_links = set(start_wiki.link)

    # Run wiki breadth-first search.
    session = requests.Session()
    pool = mp.Pool()

    depth = 0
    found = False
    while not found:
        if len(explore_wikis) == 0:
            # No more wikis to explore. Impossible wiki route.
            print("Failed to find wiki.")
            break

        print(f"Depth: {depth}")

        async_wiki_branches = [
            pool.apply_async(get_wiki_branches, args=(wiki, session))
            for wiki in explore_wikis
        ]
        
        past_wiki_links.update(explore_wiki_links)
        explore_wikis = []
        explore_wiki_links = set()

        for i in tqdm(async_wiki_branches):
            if found: break
            wiki_branches = i.get()

            for wiki in wiki_branches:
                if found: break
                if (wiki.link not in past_wiki_links) and (wiki.link not in explore_wiki_links):
                    if wiki.link == end_wiki_link:
                        # Found end wiki.
                        for parent in wiki.parents:
                            print(parent.link)
                        print(end_wiki_link)
                        found = True
                        break

                    explore_wiki_links.add(wiki.link)
                    explore_wikis.append(wiki)

        depth += 1

    end_time = time.time()
    print(f"Elapsed time: {end_time - start_time: .4f} seconds")
