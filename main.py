import requests
import re
import multiprocessing as mp
import time

from argparse import ArgumentParser
from tqdm import tqdm


def get_start_end_wiki_links() -> tuple[str, str]:
    """Parse args and get user start and end wiki links."""
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

    args = parser.parse_args()
    return args.start, args.end


def get_child_branches(parent_branch: list[str], session: requests.Session) -> list[list[str]]:
    """Get child branches to explore."""
    html = session.get(parent_branch[-1]).text

    wiki_link_re = re.compile("<a href=\"(/wiki/.*?)\"")

    child_branches = []
    for match in wiki_link_re.finditer(html):
        link_part = match.group(1)
        if not good_link_part(link_part):
            continue

        link = "https://en.wikipedia.org" + link_part
        child_branch = parent_branch + [link]
        child_branches.append(child_branch)

    return child_branches


def good_link_part(link_part: str) -> bool:
    """Return true if the link is valid."""
    bad_strs = [".", ":", "Main_Page"]
    for bad_str in bad_strs:
        if bad_str in link_part:
            # Found link to image or main page, skip.
            return False
    return True


if __name__ == "__main__":
    start_time = time.time()

    # Get user start and end wikis.
    start_wiki_link, end_wiki_link = get_start_end_wiki_links()

    # Store past and currently exploring wikis.
    past_wiki_links = set()

    explore_branches = [[start_wiki_link]]
    explore_wiki_links = set(start_wiki_link)

    # Run wiki breadth-first search.
    session = requests.Session()

    n_processes = mp.cpu_count()
    print(f"# cpu proceeses: {n_processes}")
    pool = mp.Pool(n_processes)

    depth = 0
    found = False
    while not found:
        if len(explore_branches) == 0:
            print("Failed to find wiki.")
            break

        print(f"Depth: {depth}")

        async_child_branches = [
            pool.apply_async(get_child_branches, args=(parent_branch, session))
            for parent_branch in explore_branches
        ]
        
        past_wiki_links.update(explore_wiki_links)
        explore_branches.clear()
        explore_wiki_links.clear()

        for i in tqdm(async_child_branches):
            if found: break
            child_branches = i.get()

            for child_branch in child_branches:
                child_link = child_branch[-1]
                if (child_link in past_wiki_links) or (child_link in explore_wiki_links):
                    continue

                if child_link == end_wiki_link:
                    # Found end wiki.
                    print()
                    print("\n".join(child_branch))
                    found = True
                    break

                explore_wiki_links.add(child_link)
                explore_branches.append(child_branch)

        depth += 1

    end_time = time.time()
    print(f"Elapsed time: {end_time - start_time: .4f} seconds")
