import datetime
import json
import logging
import pathlib
import re
import time
from contextlib import contextmanager
from typing import Any, Dict, List

import duckdb
import pandas as pd
import pydantic
import requests
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


class SubstackPageScrape(pydantic.BaseModel):
    publication_id: int
    subdomain: str
    contents: dict
    recommendations: List[dict]
    scraped_at: str = datetime.datetime.utcnow().isoformat(timespec="seconds")


class SubstackRecommendation(pydantic.BaseModel):
    recommendation_id: int
    recommending_publication_id: int
    recommended_publication_id: int
    recommending_subdomain: str
    recommended_subdomain: str
    contents: dict


class ScrapeOutput(pydantic.BaseModel):
    substacks: List[dict]
    recommendations: List[dict]


class SubstackClient:
    def __init__(self) -> None:
        self.session = requests.Session()

    def get_stats(self, substack_url):
        r = self.session.get(substack_url)
        return r.json()

    def scrape(self, root_subdomain: str, search_distance: int = 1) -> ScrapeOutput:
        root_page = self._scrape_substack_page(root_subdomain)
        recommendations = self._parse_recommendations(
            root_subdomain, root_page.contents["recommendations"]
        )
        final_output = ScrapeOutput(
            substacks=[root_page], recommendations=recommendations
        )
        logger.info("Found %d recommendations", len(recommendations))

        traversed_distance = 0
        search_subdomains = [r.recommended_subdomain for r in recommendations]
        traversed_subdomains = [root_subdomain]
        while traversed_distance < search_distance:
            next_subdomains = []
            for ii in search_subdomains:
                page = self._scrape_substack_page(ii)
                if page and page.contents.get("recommendations"):
                    recs = self._parse_recommendations(
                        ii, page.contents["recommendations"]
                    )
                    next_subdomains.extend(
                        [
                            r.recommended_subdomain
                            for r in recs
                            if r.recommended_subdomain not in traversed_subdomains
                        ]
                    )
                    final_output.recommendations.extend(recs)
                time.sleep(self.request_backoff)
                final_output.substacks.append(page)
            traversed_subdomains.extend(search_subdomains)
            search_subdomains = next_subdomains
            traversed_distance += 1

        return final_output

    def _scrape_substack_page(self, subdomain) -> SubstackPageScrape:
        r = self.session.get(f"https://{subdomain}.substack.com")
        pattern = re.compile(
            r"window._preloads\s+=\sJSON.parse\((.*)\)", re.MULTILINE | re.DOTALL
        )
        soup = BeautifulSoup(r.text, features="html.parser")
        recs = soup.find("script", string=pattern)
        if not recs:
            return None

        try:
            match = pattern.search(recs.text)
            blob = match.group(1)
            contents = json.loads(json.loads(blob))
        except json.JSONDecodeError:
            logger.error(
                "Failed to parse JSON from %s. Check that the RegEx pattern (%s) is correct.",
                subdomain,
                pattern,
            )
            raise

        logger.info(contents)
        return SubstackPageScrape(
            publication_id=contents["pub"]["id"],
            subdomain=contents["pub"]["subdomain"],
            recommendations=contents["recommendations"],
            scraped_at=datetime.datetime.utcnow().isoformat(timespec="seconds"),
            contents=contents,
        )

    def _parse_recommendations(
        self, subdomain: str, recommendations_list: List[Dict]
    ) -> List[SubstackRecommendation]:
        output = []
        for ii in recommendations_list:
            rec = SubstackRecommendation(
                recommendation_id=ii["id"],
                recommending_publication_id=ii["recommending_publication_id"],
                recommended_publication_id=ii["recommended_publication_id"],
                recommending_subdomain=subdomain,
                recommended_subdomain=ii["recommendedPublication"]["subdomain"],
                contents=ii,
            )
            output.append(rec)
        return output

    def write_scrape_output_json(self, scrape_output: ScrapeOutput, dir: str = "."):
        p = pathlib.Path(dir)
        (p / "recommendations.json").write_text(
            json.dumps(scrape_output.dict()["recommendations"], indent=2)
        )
        (p / "substacks.json").write_text(
            json.dumps(scrape_output.dict()["substacks"], indent=2)
        )

    def write_scrape_output_duckdb(
        self, scrape_output: ScrapeOutput, prefix: str = "tmp", dir: str = "."
    ):
        p = pathlib.Path(dir)

        for ii in ["substacks", "recommendations"]:
            subdir = p / ii
            subdir.mkdir(exist_ok=True)
            fname = f"{prefix}_{ii}.csv" if prefix else f"{ii}.csv"
            out_path = (subdir / fname).as_posix()
            df = pd.DataFrame.from_records(scrape_output.dict()[ii])
            df.to_csv(out_path, index=False)

    def read_recommendations(self, sql="") -> ScrapeOutput:
        df = duckdb.sql("SELECT * FROM 'output/recommendations/*.csv';").df()
        return df
