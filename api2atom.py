import asyncio
import urllib.request
import json
import os, sys
from pathlib import Path
import time
sys.path.append(os.path.join(os.path.dirname(__file__), "python-feedgen"))
from feedgen.feed import FeedGenerator

base_url = 'https://app.fffutu.re'
api_path = '/api/v1'
ghost_path = '/ghost/api/v3'
ghost_key = 'bdcdb2d50a3077e0543c0da764'

class BadStatusCodeError(Exception):
	pass

async def getJson(url):
	with urllib.request.urlopen(url) as url:
		if url.getcode() in range(200, 299):
			return(json.load(url))
		else:
			raise(BadStatusCodeError("Got Code" + url.getcode()))

async def queryOgs():
	url = base_url + api_path + '/ogs'
	return await getJson(url)

async def queryOg(id):	
	url = base_url + api_path + '/ogs?ogId=' + id
	return await getJson(url)

async def queryStrikes(id):
	url = base_url + api_path + '/strikes?ogId=' + id
	return await getJson(url)

async def queryPosts() :	
	url = base_url + ghost_path + '/content/posts/?include=authors,tags&fields=slug,id,title,feature_imageupdated_at,published_at,url,custom_excerpt&key=' + ghost_key
	return await getJson(url)

async def queryPost(id):	
	url = base_url + ghost_path + '/content/posts/' + id + '?fields=html&key=' + ghost_key
	return await getJson(url)

async def queryPageTitle(name):	
	url = base_url + ghost_path + '/content/pages/slug/' + name + '?fields=title&key=' + ghost_key
	return await getJson(url)

async def queryPage(name):	
	url = base_url + ghost_path + '/content/pages/slug/' + name + '?fields=html&key=' + ghost_key
	return await getJson(url)

async def main(base_path):
	Path(base_path).mkdir(parents=True, exist_ok=True)
	og_list= await queryOgs()
	for i in range(0, og_list['count']):
		generator = FeedGenerator()
		generator.id(og_list['ogs'][i]['ogId'])
		generator.title('OG ' + og_list['ogs'][i]['name'])
		generator.author({
			'name':	og_list['ogs'][i]['name'],
			'email':	og_list['ogs'][i]['email'],
			'uri':	og_list['ogs'][i]['website'],
			'land':	og_list['ogs'][i]['bundesland'],
			'facebook':	og_list['ogs'][i]['facebook'],
			'instagram':	og_list['ogs'][i]['instagram'],
			'lat':	og_list['ogs'][i]['lat'],
			'lon':	og_list['ogs'][i]['lon'],
			'telegram':	og_list['ogs'][i]['telegram'],
			'twitter':	og_list['ogs'][i]['twitter'],
			'whatsapp':	og_list['ogs'][i]['whatsapp'],
			'youtube':	og_list['ogs'][i]['youtube'],
		})
		generator.language('de')

		strike_list = await queryStrikes(og_list['ogs'][i]['ogId'])

		for strike in strike_list['strikes']:
			entry = generator.add_entry()
			entry.id(str(strike['location']) + '_' + str(strike['date']))
			entry.title(strike['name'] + ' ' + time.strftime("%A, %d %b %Y %H:%M", time.gmtime(strike['date'])))
			entry.description(strike['additionalInfo'])
			if strike['eventLink']:
				entry.link(href=strike['eventLink'])

		generator.atom_file(base_path + "/" + og_list['ogs'][i]['ogId'] + ".atom" , pretty=True)
	
	# Get App Team Posts
	generator = FeedGenerator()
	generator.id("AppAGFeed")
	generator.title("Posts der App AG")
	generator.author({
		'name':	"App AG",
		'email':	"app@fridaysforfuture.is",
		'uri':	"https://app.fffutu.re/",
	})
	generator.language('de')

	posts = await queryPosts()

	for post in posts["posts"]:
		entry = generator.add_entry()
		entry.id(post["id"])
		entry.title(post['title'])
		entry.description(post['custom_excerpt'])
		# entry.link(href=strike['url'])
	
	generator.atom_file(base_path + "/" + "AppAGFeed" + ".atom", pretty=True)

if len(sys.argv) < 2:
	base_path = "./fff-feeds/"
else:
	base_path = sys.argv[1]

asyncio.run(main(base_path))
