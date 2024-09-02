import streamlit as st
import json
import requests
from moviepy.editor import VideoFileClip, ImageClip, CompositeVideoClip
from PIL import Image, ImageDraw, ImageFont
import tempfile
import logging

# Configura il logging
logging.basicConfig(level=logging.INFO)

# Funzione per creare un'immagine di testo usando PIL
def create_text_image(text, font_size, color, bg_color=None, opacity=1.0):
    try:
        # Usa il font di default fornito da PIL
        font = ImageFont.load_default()
        
        # Calcola la dimensione del testo
        img_temp = Image.new('RGBA', (1, 1))
        draw_temp = ImageDraw.Draw(img_temp)
        bbox = draw_temp.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # Crea l'immagine con lo sfondo (se presente)
        img = Image.new('RGBA', (text_width, text_height), (255, 255, 255, 0))
        draw = ImageDraw.Draw(img)
        
        if bg_color:
            bg_img = Image.new('RGBA', (text_width, text_height), bg_color + (int(255 * opacity),))
            img = Image.alpha_composite(bg_img, img)
        
        draw.text((0, 0), text, font=font, fill=color)
        return img
    except Exception as e:
        logging.error(f"Errore nella creazione dell'immagine di testo: {e}")
        raise

# Funzione per generare il video
def create_video(json_data):
    data = json.loads(json_data)
    
    logging.info("Scaricamento del video di sfondo")
    video_url = data["video"]["background"]["url"]
    video_response = requests.get(video_url)
    
    # Salva il video di sfondo localmente
    with open('background_video.mp4', 'wb') as f:
        f.write(video_response.content)
    
    logging.info("Caricamento del video di sfondo")
    clip = VideoFileClip('background_video.mp4').resize(width=640)  # Riduci la risoluzione per evitare problemi
    
    text_clips = []
    for overlay in data["video"]["overlayTexts"]:
        logging.info(f"Creazione dell'immagine del testo per: {overlay['text']}")
        text_img = create_text_image(
            overlay["text"],
            font_size=overlay["size"],
            color=overlay["color"],
            bg_color=overlay["background"]["color"] if "background" in overlay else None,
            opacity=overlay["background"]["opacity"] if "background" in overlay else 0
        )
        
        text_img_path = tempfile.mktemp(suffix='.png')
        text_img.save(text_img_path)
        
        txt_clip = (
            ImageClip(text_img_path)
            .set_position((overlay["position"]["x"], overlay["position"]["y"]))
            .set_duration(clip.duration)
        )
        text_clips.append(txt_clip)
    
    logging.info("Combinazione del video con il testo sovrapposto")
    final_clip = CompositeVideoClip([clip] + text_clips)
    final_clip.write_videofile("output_video.mp4", codec="libx264", fps=24)

# Interfaccia Streamlit
st.title('Generatore di Video con Testo Sovrapposto')

json_input = st.text_area("Inserisci il JSON per il video", height=300, value='''
{
    "video": {
        "background": {
            "type": "video",
            "url": "https://videos.pexels.com/video-files/1034068/1034068-hd_1920_1080_25fps.mp4"
        },
        "overlayTexts": [
            {
                "text": "Testo Sovrapposto 1",
                "position": {
                    "x": "50%",
                    "y": "20%"
                },
                "font": "Arial",
                "size": 30,
                "color": "#FFFFFF",
                "background": {
                    "color": "#000000",
                    "opacity": 0.6
                }
            },
            {
                "text": "Testo Sovrapposto 2",
                "position": {
                    "x": "50%",
                    "y": "80%"
                },
                "font": "Arial",
                "size": 25,
                "color": "#FFFFFF",
                "background": {
                    "color": "#000000",
                    "opacity": 0.6
                }
            }
        ]
    }
}
''')

if st.button("Crea Video"):
    if json_input:
        try:
            create_video(json_input)
            st.success("Video creato con successo!")
            st.video("output_video.mp4")
        except Exception as e:
            st.error(f"Si è verificato un errore: {e}")
            logging.error(f"Errore durante la creazione del video: {e}")
    else:
        st.warning("Per favore, inserisci un JSON valido.")
