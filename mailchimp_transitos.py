#!/usr/bin/env python

# https://github.com/charlesthk/python-mailchimp

# API-KEY 1914ca5a76dac8ceb7ced4942452f869-us15

from mailchimp3 import MailChimp
import requests
client = MailChimp('venus.saturno.astro@gmail.com', '1914ca5a76dac8ceb7ced4942452f869-us15')

#print client.lists.all(get_all=True, fields="lists.name,lists.id")
#print client.campaigns.all(get_all=False)

transits = requests.get("http://cursodeastrologia.com.ar:8080/astrolog/transits_mailing")

print "Replicate..."
template_id = "f3338d3ce8"
template_content = client.campaigns.content.get(campaign_id=template_id)

html = template_content["html"]
template_content["html"] = html.replace("##transitos##", transits.text)
template_content["archive_html"] = template_content["html"]
template_content["plain_text"] = "Para ver este correo debe habilitar la vista en html del mismo."

new_campaign = client.campaigns.actions.replicate(campaign_id=template_id)
new_id = new_campaign["id"]
client.campaigns.content.update(campaign_id=new_id, data=template_content)

print "Send..."
client.campaigns.actions.send(campaign_id=new_id)

print "OK"
#print client.campaigns.content.get(campaign_id='213b3d4a30').keys()
#print client.campaigns.content.get(campaign_id='213b3d4a30')["archive_html"]