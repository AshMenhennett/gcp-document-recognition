## GCP Vision API Document Recognition (Demo)

Simple interaction with GCP Vision API to provide a Document Recognition Service.

The aim of this project is to simply display some of the capabilities of the GCP Vision API

Currently supported documents:
- Victorian Driver's Licence

Additional documents can be supported by contributing to the `templates` available in the code base, which are list of tuples, describing the position of each bounding vertex of a textual component of the document,
```VIC_LICENCE_NUMBER = [(77.34, 21.27), (95.74, 21.27), (96.06, 27.63), (78.72,  27.13)]```
The above template translates to vertices (top-left, top-right, bottom-right, bottom-left) in which the licence number is located on a Victorian Driver Licence.

### Install Dependencies
TODO

### Set GCP Client Credentials
Be sure to create an account with GCP and obtain your credentials in JSON format and add them to your Terminal session:
```export GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json```

### Run the Application
```python3 api.py```

### Upload Image to Recognize
Request:
```
POST /documentRecognitions HTTP/1.1
Host: 127.0.0.1:5000
Cache-Control: no-cache
Content-Type: multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW

------WebKitFormBoundary7MA4YWxkTrZu0gW
Content-Disposition: form-data; name="image"; filename="vic_licence.jpg"
Content-Type: image/jpeg


------WebKitFormBoundary7MA4YWxkTrZu0gW--
```

Response:
```
[
    {
        "VIC_LICENCE_NUMBER": "123456789"
    },
    {
        "VIC_LICENCE_EXPIRY": "12-04-2021"
    }
]
```