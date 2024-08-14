import json
import os
import pickle
import base64
import zlib
import email
from email.parser import BytesParser, Parser
from email.policy import default
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from base64 import urlsafe_b64decode, urlsafe_b64encode
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from email.mime.audio import MIMEAudio
from email.mime.base import MIMEBase
from mimetypes import guess_type as guess_mime_type

SCOPES = ['https://mail.google.com/']
our_email = 'mathlouthisiwar01@gmail.com'


def gmail_authenticate():
    creds = None

    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'cert.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)
    return build('gmail', 'v1', credentials=creds)


def get_decoded_email_body(message):
    message_raw = message
    message_bytes = base64.urlsafe_b64decode(message_raw.encode('ASCII'))
    mime_msg = email.message_from_bytes(message_bytes, policy=default)

    def get_first_text_part(msg):
        maintype = msg.get_content_maintype()
        if maintype == 'multipart':
            for part in msg.get_payload():
                if part.get_content_maintype() == 'text':
                    return part.get_payload(decode=True)
        elif maintype == 'text':
            return msg.get_payload(decode=True)

    text = get_first_text_part(mime_msg)
    charset = mime_msg.get_content_charset('utf-8')
    decoded_text = text.decode(charset, 'replace')
    return decoded_text



def search_messages(service, query):
    result = service.users().messages().list(userId='me', q=query).execute()
    messages = []
    if 'messages' in result:
        messages.extend(result['messages'])
    while 'nextPageToken' in result:
        page_token = result['nextPageToken']
        result = service.users().messages().list(
            userId='me', q=query, pageToken=page_token).execute()
        if 'messages' in result:
            messages.extend(result['messages'])
    return messages



def get_size_format(b, factor=1024, suffix="B"):
  
    for unit in ["", "K", "M", "G", "T", "P", "E", "Z"]:
        if b < factor:
            return f"{b:.2f}{unit}{suffix}"
        b /= factor
    return f"{b:.2f}Y{suffix}"


def parse_parts(service, parts,body ,folder_name, message):
    if parts:
        for part in parts:
            filename = part.get("filename")
            mimeType = part.get("mimeType")
            body = part.get("body")
            data = body.get("data")
            file_size = body.get("size")
            part_headers = part.get("headers")


            if part.get("parts"):
               
                parse_parts(service, part.get("parts"), folder_name, message)
            if mimeType == "text/plain":
                print("text")
                if data:
                    text = urlsafe_b64decode(data).decode()
                    print(text)
            elif mimeType == "text/html":
                print("html")
                if not filename:
                    filename = "index.html"
                filepath = os.path.join(folder_name, filename)
                print("Saving HTML to", filepath)
                with open(filepath, "wb") as f:
                    f.write(urlsafe_b64decode(data))
            else:
                for part_header in part_headers:
                    part_header_name = part_header.get("name")
                    part_header_value = part_header.get("value")
                    if part_header_name == "Content-Disposition":
                        if "attachment" in part_header_value:
                           
                            print("Saving the file:", filename,
                                  "size:", get_size_format(file_size))
                            attachment_id = body.get("attachmentId")
                            attachment = service.users().messages() \
                                .attachments().get(id=attachment_id, userId='me', messageId=message['id']).execute()
                            data = attachment.get("data")
                            filepath = os.path.join(folder_name, filename)
                            if data:
                                with open(filepath, "wb") as f:
                                    f.write(urlsafe_b64decode(data))
    if body: 
        decoded_data = get_decoded_email_body (body)
        filename = "index.html"
        filepath = os.path.join(folder_name, filename)
        encoded_data = decoded_data.encode('utf-8')

        with open(filepath, "wb") as f:
            f.write(encoded_data)
        
        


def clean(text):
    return "./data/"+"".join(c if c.isalnum() else "_" for c in text)


def read_message(service, message):
 
    msg = service.users().messages().get(
        userId='me', id=message['id'], format='full').execute()
    payload = msg['payload']
    headers = payload.get("headers")
    parts = payload.get("parts")
    bodys =payload.get('body')
    body = str(bodys.get('data'))
    print(body)
        # fichier.write(str(payload.get('body')))
    folder_name = "email"
    has_subject = False
    if headers:
        for header in headers:
            name = header.get("name")
            value = header.get("value")
            if name.lower() == 'from':
                print("From:", value)
            if name.lower() == "to":
                print("To:", value)
            if name.lower() == "subject":
                has_subject = True
                folder_name = clean(value)
                folder_counter = 0
                while os.path.isdir(folder_name):
                    folder_counter += 1
                    if folder_name[-1].isdigit() and folder_name[-2] == "_":
                        folder_name = f"{folder_name[:-2]}_{folder_counter}"
                    elif folder_name[-2:].isdigit() and folder_name[-3] == "_":
                        folder_name = f"{folder_name[:-3]}_{folder_counter}"
                    else:
                        folder_name = f"{folder_name}_{folder_counter}"
                os.mkdir(folder_name)
                print("Subject:", value)
            if name.lower() == "date":
                print("Date:", value)
    if not has_subject:
        if not os.path.isdir(folder_name):
            os.mkdir(folder_name)
    parse_parts(service, parts, body,folder_name, message)
    print("="*50)


service = gmail_authenticate()
results = search_messages(service, "bilel.grami@etap.com.tn")
print(f"Found {len(results)} results.")

for msg in results:
    read_message(service, msg)
