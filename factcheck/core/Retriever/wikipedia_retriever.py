from factcheck.utils.logger import CustomLogger
import wikipedia
logger = CustomLogger(__name__).getlog()
import pdb
import requests

wiki_session = requests.Session()

wiki_url = "https://en.wikipedia.org/w/api.php"

def wiki_search(query_term, limit=1):
    params = {
        "action": "opensearch",
        "namespace": "0",
        "search": query_term,
        "limit": str(limit),
        "format": "json"
    }

    results = wiki_session.get(url=wiki_url, params=params)
    data = results.json()
    return {"page_title": data[1], "url": data[3]}


class WikipediaEvidenceRetriever:
    def __init__(self, llm_client, api_config: dict = None):
        """Initialize the WikipediaEvidenceRetriever class"""
        self.lang = "en"
        self.llm_client = llm_client

    def retrieve_evidence(self, claim_queries_dict, top_k: int = 3, snippet_extend_flag: bool = True):
        """Retrieve evidences for the given claims

        Args:
            claim_queries_dict (dict): a dictionary of claims and their corresponding queries.
            top_k (int, optional): the number of top relevant results to retrieve. Defaults to 3.
            snippet_extend_flag (bool, optional): whether to extend the snippet. Defaults to True.

        Returns:
            dict: a dictionary of claims and their corresponding evidences.
        """
        logger.info("Collecting evidences ...")
        query_list = [y for x in claim_queries_dict.items() for y in x[1]]
        evidence_list = self._retrieve_evidence_4_all_claim(
            query_list=query_list, top_k=top_k, snippet_extend_flag=snippet_extend_flag
        )

        i = 0
        claim_evidence_dict = {}
        for claim, queries in claim_queries_dict.items():
            evidences_per_query_L = evidence_list[i : i + len(queries)]
            claim_evidence_dict[claim] = [e for evidences in evidences_per_query_L for e in evidences]
            i += len(queries)
        assert i == len(evidence_list)
        logger.info("Collect evidences done!")
        return claim_evidence_dict

    def _retrieve_evidence_4_all_claim(
        self, query_list: list[str], top_k: int = 3, snippet_extend_flag: bool = True
    ) -> list[list[str]]:
        """Retrieve evidences for the given queries

        Args:
            query_list (list[str]): a list of queries to retrieve evidences for.
            top_k (int, optional): the number of top relevant results to retrieve. Defaults to 3.
            snippet_extend_flag (bool, optional): whether to extend the snippet. Defaults to True.

        Returns:
            list[list[]]: a list of [a list of evidences for each given query].
        """

        # init the evidence list with None
        # evidences = [[] for _ in query_list]
        evidences = []

        # # get the response from serper
        # wikipedia_responses = []
        # for i in range(0, len(query_list), 100):
        #     batch_query_list = query_list[i : i + 100]
        #     batch_response = self._request_wikipedia_api(batch_query_list)
        #     if batch_response is None:
        #         logger.error("Wikipedia API request error!")
        #         return evidences
        #     else:
        #         wikipedia_responses += batch_response.json()

        for query in query_list:
            evidences += [self._wikipedia_search(query, top_k=top_k, snippet_extend_flag=snippet_extend_flag)]

        return evidences

    def _wikipedia_search(self, query, top_k, snippet_extend_flag):
        """Request the serper api

        Args:
            questions (list): a list of questions to request the serper api.

        Returns:
            web response: the response from the serper api
        """
        query_results = []

        try:
            # Search for pages related to the query
            # search_results = wikipedia.search(query, results=top_k)
            search_results = wiki_search(query)
            page_titles = search_results["page_title"]

            
            # no pages found
            # if not search_results:
            if not page_titles:
                print(f"No Wikipedia page found for the {query}.")
                return []

            # top_results = search_results[:top_k]
            # use first search result
            page_title = page_titles[0]

            # for page_title in search_results:
            wiki_page = wikipedia.page(title=page_title)

        except wikipedia.exceptions.DisambiguationError as e:
            # Handle cases where the search term is ambiguous
            print(f"The term '{query}' is ambiguous. Possible options: {', '.join(e.options[:5])}.")
            print(f"Using option {e.options[0]}.")
            # breakpoint()
            # wiki_page = wikipedia.page(e.options[0])
            return []


        except wikipedia.exceptions.PageError:
            # Handle cases where the page does not exist
            print(f"The Wikipedia page for '{query}' does not exist.")
            return []

        # page_summary = wikipedia.summary(page_title, sentences=3)  # Limit to 3 sentences for brevity            
        if snippet_extend_flag:
            page_content = wiki_page.content
            # query_results.append(f"{page_title}: {page_content}")
            query_results.append({"text": f"{page_title}: {page_content}", "url": ""})

        else:
            page_summary = wiki_page.summary
            # query_results.append(f"{page_title}: {page_summary}")
            query_results.append({"text": f"{page_title}: {page_summary}", "url": ""})

    
        return query_results

        
        # except Exception as e:
        #     # Catch other exceptions
        #     print(f"An error occurred: {e}")
        #     return []



