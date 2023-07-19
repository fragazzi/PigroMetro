import streamlit as st
import pandas as pd
import whisper

from tempfile import NamedTemporaryFile

from utils import *


@st.cache
def convert_df_to_csv(df):
 # IMPORTANT: Cache the conversion to prevent computation on every rerun
  return df.to_csv().encode('utf-8')


st.title("PigroMetro    :flag-it:")
st.header("L'app per chi lavora viaggiando  :car:")
st.markdown("Caricando delle registrazioni **audio** con le informazioni del viaggio fatto, l'app "
            "automaticamente calcolerà il chilometraggio. Una registrazione deve avere la seguente struttura:")
st.markdown("*data*   **'partenza'**   *luogo di partenza*   **'arrivo'**   *luogo di arrivo*")
st.markdown("Dove le parole **'partenza'** e **'arrivo'** devo essere presenti obbligatoriamente.")
st.markdown("Un esempio di registrazione corretta è:")
st.markdown("8 giugno 2023 **partenza**  Via Paolo Ferrari 85 Modena **arrivo** Via di San Luca 36 Bologna")

model_selected = 'base'
    
#Sidebar
with st.sidebar:
    st.title("Seleziona un modello:")
    model_selected = st.selectbox(
        'Modelli disponibili:',
        ('tiny', 'base', 'small', 'medium', 'large'),
        index=1
    )
        
    
# Load whisper model
whisper_model = whisper.load_model(model_selected)
    
# Upload files
uploaded_files = st.file_uploader(
    "Seleziona file audio", 
    type=["ogg", "mp3"], 
    accept_multiple_files=True
)

# Data lists for table
id_list, date_list, dep_list, arr_list, km_list = [], [], [], [], []

st.text(f"Modello usato: {model_selected}")
with st.spinner('Calcolo delle distanze...'):
    
    for file in uploaded_files:
        if file is not None: 
            with NamedTemporaryFile(suffix="ogg") as temp:
                temp.write(file.getvalue())
                temp.seek(0)
        
                # result = model.transcribe(temp.name)
                
                trip_text = whisper_model.transcribe(temp.name)["text"]
            
            tokens = trip_text.split(" ")
            tokens = [t for t in tokens if t != '']
            
            id_list.append(file.id)
        
            date_tks = [tokens[0], tokens[1], tokens[2]]
            date = transform_date(date_tks)

            index_dep = tokens.index("partenza")
            index_arr = tokens.index("arrivo")

            departure_tks = tokens[index_dep + 1:index_arr]
            arrival_tks = tokens[index_arr + 1:]

            departure = " ".join(departure_tks[:-1])
            arrival = " ".join(arrival_tks)

            lat1, lon1 = geocode_place(departure)
            lat2, lon2 = geocode_place(arrival)

            distance = None
            if lat1 is not None and lon1 is not None and lat2 is not None and lon2 is not None:
                distance = round(calculate_distance(lat1, lon1, lat2, lon2), 2)

            date_list.append(date[:-1])
            dep_list.append(departure[:-1])
            arr_list.append(arrival[:-1])
            km_list.append(distance)

data_dict = {
    'ID': id_list,
    'Data': date_list,
    'Partenza': dep_list,
    'Arrivo': arr_list,
    'Distanza (km)': km_list
}

df = pd.DataFrame(data_dict)
if not df.empty:
    st.data_editor(
        df,
        disabled=["ID", "Data"],
        hide_index=True
    )

    st.download_button(
        label="Salva tabella",
        data=convert_df_to_csv(df),
        file_name='Percorsi.csv',
        mime='text/csv',
    )
    
    # if st.button("Download excel"):
    #     with st.spinner("Download in corso..."):
    #         try:
    #             df.to_excel("Percorsi.xlsx", index=False)
    #         finally:
    #             st.text("Tabella scaricata!")
