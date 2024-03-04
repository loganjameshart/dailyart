import requests
from datetime import datetime
from pathlib import Path
from random import randint
import smtplib
from email.message import EmailMessage
from os import remove

SERVER = ""
PORT = ""
MAIL = ""
PASS = ""
RECIPIENTS = []

DATE = datetime.now().strftime("%m-%d-%y")
IMAGE_SETTINGS = "full/843,/0/default.jpg" #grabbed from art institute's instructions on best formatting
DATA_API_ENDPOINT = r"https://api.artic.edu/api/v1/artworks"
IMAGE_API_ENDPOINT = r"https://www.artic.edu/iiif/2"


def get_artwork_data(page_number: int, selection_number:int ) -> dict:
    """Get relevant artwork data from API and return as dictionary."""
    r = requests.get(f"{DATA_API_ENDPOINT}?page={page_number}")
    response = r.json()
    art_data = {}
    art_data["artwork_id"] = response["data"][selection_number]["image_id"]
    art_data["artwork_title"] = response["data"][selection_number]["title"]
    art_data["artwork_artist"] = response["data"][selection_number]["artist_display"]
    art_data["artwork_date"] = response["data"][selection_number]["date_display"]
    return art_data


def get_filename(art_data: dict) -> str:
     """Function to standardize file name across other functions."""
     return rf"{art_data['artwork_title']} - {art_data['artwork_artist']} ({art_data['artwork_date']}).jpg"


def get_image(art_data: dict) -> None:
    """Uses artwork data from API to download artwork."""
    r = requests.get(f"{IMAGE_API_ENDPOINT}/{art_data['artwork_id']}/{IMAGE_SETTINGS}")
    file_name = get_filename(art_data)

    with open(file_name,'wb') as new_image:
        for chunk in r.iter_content(chunk_size=128):
            new_image.write(chunk)


def create_log(art_data: dict) -> None:
    """Creates a log (or appends one if it already exists) of every piece downloaded and sent."""
    if Path("art_log.txt").exists():
        with open("art_log.txt", "a") as art_log_file:
            art_log_file.write(f"{DATE}: {art_data['artwork_title']} by {art_data['artwork_artist']} - {art_data['artwork_date']}\n\n")
    else:
        with open("art_log.txt", "w") as art_log_file:
            art_log_file.write(f"{DATE}: {art_data['artwork_title']} by {art_data['artwork_artist']} - {art_data['artwork_date']}\n\n")


def send_image(art_data: dict) -> None:
    """Sends image via email."""
    file_name = get_filename(art_data)
    art_message = EmailMessage()
    art_message["Subject"] = f"Daily Artwork - {DATE}"
    art_message["To"] = RECIPIENTS
    art_message["From"] = MAIL

    art_message.set_content(f"{DATE}: {art_data['artwork_title']} by {art_data['artwork_artist']} - ({art_data['artwork_date']})")

    with open(file_name, "rb") as art_file:
        image_data = art_file.read()
        art_message.add_attachment(image_data, maintype='image', subtype='jpg')

    with smtplib.SMTP("smtp.gmail.com", 587) as smtp_connection:
        smtp_connection.starttls()
        smtp_connection.login(MAIL, PASS)
        smtp_connection.ehlo()
        smtp_connection.send_message(art_message, to_addrs=RECIPIENTS)


def main():
    page = randint(1, 10405) # amount of pages in the art institute's api database
    choice = randint(1, 11) # how many results per page
    art_data = get_artwork_data(page, choice)
    get_image(art_data)
    create_log(art_data)
    send_image(art_data)
    remove(get_filename(art_data))

if __name__ == "__main__":
    main()


