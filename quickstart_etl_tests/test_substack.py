from quickstart_etl.utils import SubstackClient


def test_client_scrapes_page():
    # given
    subdomain = "stkbailey"
    client = SubstackClient()

    # when
    output = client._scrape_substack_page(subdomain)

    # then
    print(output)
    assert output is not None
