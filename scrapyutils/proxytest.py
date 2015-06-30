import requests
with open('/home/ubuntu/proxylist.txt') as f:
    for line in f:
        proxies = {
                "http": line.strip(),
                "https": line.strip(),
                }
        http_test = requests.get("http://example.org", proxies=proxies)
        https_test = requests.get("https://example.org", proxies=proxies)
        print http_test
        print https_test


