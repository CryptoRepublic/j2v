import streamlit as st
import json
import requests
from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip
from PIL import Image, ImageDraw, ImageFont
import tempfile

# Funzione per creare un'immagine di testo usando PIL
def create_text_image(text, font_size, color, bg_color=None):
    font = ImageFont.truetype("arial.ttf", font_size)  # Assicurati che arial.ttf sia disponibile su Streamlit Cloud
    size = font.getsize(text)
    img = Image.new('RGBA', size, bg_color if bg_color else (255, 255, 255, 0))
    draw = ImageDraw.Draw(img)
    draw.text((0, 0), text, font=font, fill=color)
    return img

# Funzione per generare il video
def create_video(json_data):
    data = json.loads(json_data)

    # Scarica il video di sfondo
    video_url = data["video"]["background"]["url"]
    video_response = requests.get(video_url)

    # Salva il video di sfondo localmente
    with open('background_video.mp4', 'wb') as f:
        f.write(video_response.content)

    # Carica il video di sfondo
    clip = VideoFileClip('background_video.mp4')

    # Crea clip dei testi come immagini sovrapposte
    text_clips = []
    for overlay in data["video"]["overlayTexts"]:
        # Crea l'immagine del testo
        text_img = create_text_image(overlay["text"], overlay["size"], overlay["color"])

        # Salva temporaneamente l'immagine del testo
        text_img_path = tempfile.mktemp(suffix='.png')
        text_img.save(text_img_path)
        
        # Crea un ImageClip dal file PNG
        txt_clip = (
            ImageClip(text_img_path)
            .set_position((overlay["position"]["x"], overlay["position"]["y"]))
            .set_duration(clip.duration)
        )

        text_clips.append(txt_clip)

    # Combina il video di sfondo con i testi sovrapposti
    final_clip = CompositeVideoClip([clip] + text_clips)
    final_clip.write_videofile("output_video.mp4", codec="libx264", fps=24)

# Interfaccia Streamlit
st.title('Generatore di Video con Testo Sovrapposto')

# Input JSON
json_input = st.text_area("Inserisci il JSON per il video", height=300)

if st.button("Crea Video"):
    if json_input:
        try:
            create_video(json_input)
            st.success("Video creato con successo!")
            st.video("output_video.mp4")  # Mostra il video generato
            
        except Exception as e:
            st.error(f"Si è verificato un errore: {e}")
    else:
        st.warning("Per favore, inserisci un JSON valido.")
