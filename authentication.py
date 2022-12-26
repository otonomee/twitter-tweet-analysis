from requests_oauthlib import OAuth1Session

consumer_key = 'KGhVgjlQxnlLg1ed0kpEwNAQL'
consumer_secret = 'sodSedt0j2vSeSZEe4Sit56sfns7UVbWIDfOzbyt0n1GPs2PBq'
access_token = '4457516474-c7qLzTvDCBPzMofk7dv5sKhJtA4W1rOAeymUUkF'
access_secret = '1yJlIluxt2xcSzXRHyQDcz8I3KivX3bzwQUU05nbxEGSU'
bearer_token = f"Bearer AAAAAAAAAAAAAAAAAAAAAJVsawEAAAAAFBxEhB4fNZLfXanFFvNAN3LmS5E%3DYCioDYIcBeuvoUxerkfurUDCjbxOEXqMrrOLjmBQYZDIaBOoaA"

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
