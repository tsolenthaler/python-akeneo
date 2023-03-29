import json
import requests
import mimetypes
import urllib3
import base64
import collections
import mimetypes
from oauthlib.oauth2 import LegacyApplicationClient
from requests_oauthlib import OAuth2Session

class Akeneo:
    def __init__(self, host, clientid, secret, user, passwd):
        self.host = host
        self.clientid = clientid
        self.secret = secret
        self.user = user
        self.passwd = passwd
        self.accessToken = self.getAccessToken()

    def getAccessToken(self):
        oauth = OAuth2Session(client=LegacyApplicationClient(self.clientid))
        token = oauth.fetch_token(token_url=self.host+'/api/oauth/v1/token',
                username=self.user, password=self.passwd, client_id=self.clientid,
                client_secret=self.secret)
        return token['access_token']

    def getRequest(self, query):
        url = self.host + query
        headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer '+ self.accessToken}
        r = requests.get(url, headers=headers) #data=payload, 
        if r:
            return r.json()
        else:
            print('An error has occurred.')
            print(r.status_code)
            return False
        r.close()

    def getMediaFileBody(self, file, sku, attribute, scope=None, local=None):
        product_data = json.dumps({
            "identifier": sku,
            "attribute": attribute,
            "scope": scope,
            "locale": local
        })
        image_base64 = base64.b64encode(file)
        mimetype = mimetypes.guess_type(base64.b64decode(file))[0]
        payload = collections.OrderedDict({
            'product': str(product_data),
            'file': (mimetype.replace("/", "."), base64.b64decode(image_base64))
        })
        return payload

    def postMediaRequest(self, query, data):
        url = self.host + query
        (content, content_type) = urllib3.filepost.encode_multipart_formdata(data)
        headers = {'Content-Type': content_type, 'Authorization': 'Bearer '+ self.accessToken}
        r = requests.post(url, headers=headers, data=data)
        if r:
            return r.status_code
        else:
            print('An error has occurred.')
            print(r.status_code)
            print(r.json())
            return False
        r.close()
    
    def patchRequest(self, query, data, contentType):
        url = self.host+query
        if contentType == 'application/json':
            body = json.dumps(data)
        if contentType == 'application/vnd.akeneo.collection+json':
            body = data
        headers = {'Content-Type': contentType, 'Authorization': 'Bearer '+ self.accessToken}
        r = requests.patch(url, data=body, headers=headers) #data=payload,
        if r:
            return r.status_code
        else:
            print('PATCH: An error has occurred.')
            print(r.status_code)
            print(r.json())
            return False
        r.close()

    def deleteRequest(self, query):
        url = self.host+query
        contentType = 'application/json'
        headers = {'Content-Type': contentType, 'Authorization': 'Bearer '+ self.accessToken}
        r = requests.delete(url, headers=headers) #data=payload,
        if r:
            return r.status_code
        else:
            print('DELETE: An error has occurred.')
            print(r.status_code)
            print(r.json())
            return False
        r.close()

    def getProduct(self, query):
        url = self.host+query
        headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer '+ self.accessToken}
        r = requests.get(url, headers=headers)

        if r:
            return r.json()
        else:
            print('An error has occurred.')
            print(r.status_code)
            return False
        r.close()
    
    # Get Products
    # https://api.akeneo.com/api-reference.html#get_products
    def getProducts(self, search=''):
        nextPage = True
        items = []
        headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer '+ self.accessToken}
        nextLink = ''
        starturl = '/api/rest/v1/products'
        starturl += '?pagination_type=search_after&limit=100'
        if len(search) > 2:
            starturl += '&search='+search
        while nextPage:
            if not nextLink:
                url = self.host+starturl
            else:
                url = nextLink
            print(url)
            r = requests.get(url, headers=headers)
            if r:
                itemList = r.json()['_embedded']['items']
                for item in itemList:
                    items.append(item)
                data = r.json()['_links']
                if 'next' in data:
                    nextLink = data['next']['href']
                else:
                    nextPage = False
            else:
                print('An error has occurred.')
                print(r.status_code)
            r.close()
        return items

    # Get Product by Code
    # https://api.akeneo.com/api-reference.html#get_products__code_
    def getProductByCode(self, code):
        query = '/api/rest/v1/products/' + str(code)
        return self.getRequest(query)
    
    # Patch Product by Code
    # https://api.akeneo.com/api-reference.html#patch_products__code_
    def patchProductByCode(self, code, body):
        query = '/api/rest/v1/products/' + str(code)
        return self.patchRequest(query, body, 'application/json')

    # Not Allowed by Akeneo
    def removeProductByCode(self, code):
        query = '/api/rest/v1/products/' + str(code)
        return self.deleteRequest(query)

    def getCategories(self):
        query = '/api/rest/v1/categories?limit=100'
        return self.getRequest(query)

    def patchCategories(self):
        query = '/api/rest/v1/categories'
        return self.patchRequest(query, 'application/json')

    def getCategoryByCode(self, code):
        query = '/api/rest/v1/categories/'+ str(code)
        return self.getRequest(query)

    def getCategoryByParentCateory(self, code):
        query = '/api/rest/v1/categories?search={"parent":[{"operator":"=","value":"'+ str(code) +'"}]}'
        return self.getRequest(query)

    def getFamily(self):
        query = '/api/rest/v1/families/'
        return self.getRequest(query)

    def getFamilyByCode(self, code):
        query = '/api/rest/v1/families/'+ str(code)
        return self.getRequest(query)

    def patchFamily(self, code, body):
        query = '/api/rest/v1/families/'+ str(code)
        return self.patchRequest(query, body, 'application/json')
    
    def getAttributByCode(self):
        query = '/api/rest/v1/attributes/'
        return self.getRequest(query)

    def getAttributByCode(self, code):
        query = '/api/rest/v1/attributes/'+ str(code)
        return self.getRequest(query)

    def patchAttribut(self, code, body):
        query = '/api/rest/v1/attributes/'+ str(code)
        return self.patchRequest(query, body, 'application/json')

    def removeAttributByCode(self, code):
        query = '/api/rest/v1/attributes/'+ str(code)
        return self.deleteRequest(query)

    def getAttributOption(self, attribut):
        query = '/api/rest/v1/attributes/'+ str(attribut)+'/options?limit=100'
        return self.getRequest(query)

    def getAttributOptionByCode(self, code, attribut):
        query = '/api/rest/v1/attributes/'+ str(attribut)+'/options/'+ str(code)
        return self.getRequest(query,'application/json')

    def patchAttributOption(self, attribut, body):
        query = '/api/rest/v1/attributes/'+ str(attribut)+'/options'
        return self.patchRequest(query, body, 'application/vnd.akeneo.collection+json')

    def patchAttributOptionByCode(self, code, attribut, body):
        query = '/api/rest/v1/attributes/'+ str(attribut)+'/options/'+ str(code)
        return self.patchRequest(query, body, 'application/json')

    def getAttributeGroups(self):
        query = '/api/rest/v1/attribute-groups/'
        return self.getRequest(query)

    def getAttributeGroupsbyCode(self, code):
        query = '/api/rest/v1/attribute-groups/'+ str(code)
        return self.getRequest(query)

    def patchAttributeGroupsbyCode(self, code, body):
        query = '/api/rest/v1/attribute-groups/'+ str(code)
        return self.patchRequest(query, body, 'application/json')

    def getAssociationTypesByCode(self, code):
        query = '/api/rest/v1/association-types/'+ str(code)
        return self.getRequest(query)

    def patchAssociationTypesByCode(self, code, body):
        query = '/api/rest/v1/association-types/'+ str(code)
        return self.patchRequest(query, body, 'application/json')

    def getMeasureFamilyByCode(self, code):
        query = '/api/rest/v1/measure-families/'+ str(code)
        return self.getRequest(query)

    def getMeasurementFamily(self):
        query = '/api/rest/v1/measurement-families/'
        return self.getRequest(query)

    def patchMeasurementFamily(self, body):
        query = '/api/rest/v1/measurement-families'
        return self.patchRequest(query, body, 'application/json')

    # Patch Products
    # https://api.akeneo.com/api-reference.html#patch_products
    def patchProducts(self, body):
        query = '/api/rest/v1/products'
        return self.patchList(query, body)
    
    # POST Media File
    # https://api.akeneo.com/api-reference.html#post_media_files
    def postMediaFileProduct(self, file, sku, attribute, locale, scope):
        body = self.getMediaFileBody(file, sku, attribute, locale, scope)
        query = '/api/rest/v1/media-files'
        return self.postMediaRequest(query, body)

    def patchList(self, query, body):
        url = self.host+query
        headers = {'Content-Type': 'application/vnd.akeneo.collection+json', 'Authorization': 'Bearer '+ self.getAccessToken()}
        r = requests.patch(url, data=body, headers=headers) #data=payload, 
        if r:
            return r.status_code
        else:
            print('An error has occurred.')
            print(r.status_code)
            return False
        r.close()