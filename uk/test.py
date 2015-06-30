import requests
user_agent = {'User-agent': 'Mozilla/5.0'}
test = requests.get('http://www.thomsonlocal.com/Accountants/UK/', headers=user_agent)
import pdb; pdb.set_trace()
