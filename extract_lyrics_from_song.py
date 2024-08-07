
#Fetch information (Title of the song, artist and lyrics) with starting letter of the artist
import requests
from bs4 import BeautifulSoup
import pandas as pd
import string
import tkinter as tk
from tkinter import messagebox, scrolledtext

data = []

def fetch_lyrics(song_url):
    lyrics_page = requests.get(song_url)
    lyrics_soup = BeautifulSoup(lyrics_page.text, "html.parser")

    # Assuming lyrics are in a <pre> or <div> with specific class, you may need to inspect and adjust accordingly
    lyrics_div = lyrics_soup.find("div", id="lyrics_text")  # Example: correct to actual tag containing lyrics
    return lyrics_div.text.strip() if lyrics_div else "Lyrics not found"


def scrape_artist_page(artist_letter):
    url = f"https://www.lyricsmode.com/lyrics/{artist_letter}"
    page = requests.get(url)
    soup = BeautifulSoup(page.text, "html.parser")

    # Check if the page does not exist
    oops_message = soup.find("div", class_="song_name fs32")
    if oops_message and "Oops! This page doesn't exist!" in oops_message.text:
        return

    artists = soup.find_all("a", class_="lm-link lm-link--secondary")
    for artist_tag in artists:
        artist_name = artist_tag.text.strip()
        artist_link = artist_tag.attrs["href"]
        scrape_songs_for_artist(artist_name, artist_link)


def scrape_songs_for_artist(artist_name, artist_link):
    url = "https://www.lyricsmode.com" + artist_link
    page = requests.get(url)
    soup = BeautifulSoup(page.text, "html.parser")

    # Adjusted selector based on your input
    songs = soup.find_all("a", class_="lm-link lm-link--primary")
    for song_tag in songs:
        song_title = song_tag.text.strip()
        song_link = song_tag.attrs["href"]
        lyrics = fetch_lyrics("https://www.lyricsmode.com" + song_link)

        item = {
            'Title': song_title,
            'Artist': artist_name,
            'Lyrics': lyrics
        }

        data.append(item)
        update_display(item)


def update_display(item):
    display_text.insert(tk.END, f"Title: {item['Title']}\n")
    display_text.insert(tk.END, f"Artist: {item['Artist']}\n")
    display_text.insert(tk.END, f"Lyrics: {item['Lyrics'][:60]}...\n\n")


def start_scraping():
    letter = letter_entry.get().lower()
    if letter not in string.ascii_lowercase:
        messagebox.showerror("Error", "Please enter a valid letter from a to z.")
        return

    global data
    data = []
    display_text.delete(1.0, tk.END)

    scrape_artist_page(letter)

    if data:
        df = pd.DataFrame(data)
        df.to_csv('lyrics_data.csv', index=False)
        messagebox.showinfo("Info", "Scraping complete. Data saved to lyrics_data.csv")
    else:
        messagebox.showwarning("Warning", "No data scraped. Please check the website structure and your selectors.")


# Setting up the GUI
root = tk.Tk()
root.title("Lyrics Scraper")

tk.Label(root, text="Enter Artist Starting Letter:").grid(row=0, column=0, padx=10, pady=10)
letter_entry = tk.Entry(root)
letter_entry.grid(row=0, column=1, padx=10, pady=10)

scrape_button = tk.Button(root, text="Start Scraping", command=start_scraping)
scrape_button.grid(row=1, column=0, columnspan=2, padx=10, pady=10)

display_text = scrolledtext.ScrolledText(root, width=60, height=20)
display_text.grid(row=2, column=0, columnspan=2, padx=10, pady=10)

root.mainloop()

