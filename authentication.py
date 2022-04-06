from requests_oauthlib import OAuth1Session

consumer_key = 'hCE0VJnUGZ1iqhAJBaKerMqBo'
consumer_secret = '0oj8dtMUGiWI9b48fL2ylwhXjvP3mEsdFIZ25AQOdocqHBfqbu'
access_token = '4457516474-gstVDBrHwP6fNUrCsljtRgJyyLv55MdBqnyseCP'
access_secret = '58Xx5RmGtLcWQTdaZCbjtw5hYxy9JkxKdbieEmyaO3WPj'
bearer_token = f"Bearer AAAAAAAAAAAAAAAAAAAAAJVsawEAAAAAl6Q8X%2FFRODLD51lX773KlYA9zug%3DO0rYSD1Fhae2PQIPN6HxpW3IcDDxds6Z55AJx8hIzKlQj9galp"

def get_resource_token():
    request_token = OAuth1Session(
        client_key=consumer_key, client_secret=consumer_secret)

    url = 'https://api.twitter.com/oauth/request_token'

    data = request_token.get(url)

    json_file_path = data

    # split the string to get relevant data
    data_token = str.split(data.text, '&')
    ro_key = str.split(data_token[0], '=')
    ro_secret = str.split(data_token[1], '=')
    resource_owner_key = ro_key[1]
    resource_owner_secret = ro_secret[1]
    resource = [resource_owner_key, resource_owner_secret]
    return resource
