import os
import io
import json
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google_auth_oauthlib.flow import InstalledAppFlow
from speechkit import configure_credentials, creds
from speechkit import model_repository
from speechkit.stt import AudioProcessingType
import openai
import pickle
from google.auth.transport.requests import Request
import tempfile

# Настройка Yandex SpeechKit и OpenAI
configure_credentials(
    yandex_credentials=creds.YandexCredentials(api_key='AQVNxIyv0F-53CoDcODWiQwApo2K0JCVwdniZkw5')
)
openai.api_key = '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'

# Настройка Google API
SCOPES = ['https://www.googleapis.com/auth/drive', 'https://www.googleapis.com/auth/spreadsheets']
CLIENT_SECRET_FILE = 'client_secret_990092097767-63r637h5n8ba4btc2spt17ju8htdb9ed.apps.googleusercontent.com.json'
TOKEN_PICKLE_FILE = 'token.pickle'

def authenticate_google_services():
    creds = None
    if os.path.exists(TOKEN_PICKLE_FILE):
        with open(TOKEN_PICKLE_FILE, 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(CLIENT_SECRET_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_PICKLE_FILE, 'wb') as token:
            pickle.dump(creds, token)
    return build('drive', 'v3', credentials=creds), build('sheets', 'v4', credentials=creds)

def analyze_call(transcript):
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"Ты оцениваешь разговор менеджера компании Nova med с клиентом. Проанализируй текст развора между менеджером компании Nova med с собеседником. Нужно оценить диалог на предмет выполнения скрипта менеджером, вот скрипт: 1. Менеджер должен установить контакт, представиться, обозначить цель звонка и спросить ИИН пациента. 2. Менеджер должен взять инициативу переговоров в свои руки. 3. Менеджер должен выявить потребность, задав следующие вопросы: Что беспокоит пациента? На предмет чего необходимо пройти то или иное исследование? Уточняет необходимость введения контрастного вещества на услуги МРТ и КТ? Есть ли направление от врача? На базе выявленной потребности, менеджер должен предложить записаться на услугу. Озвучить стоимость услуги. Оцени тональность менеджера, был ли он уверен в себе, был ли он уверен в услуге, смог ли он наладить контакт с клиентом? В конце выдай объективную оценку от 1 до 10. Также посмотри и исправь грамматические ошибки. И имей в виду, что это один диалог: канал 0 - это клиент, канал 1 - это менеджер по продажам, так что воспринимай это как один диалог и анализируй это как один диалог соответственно и можешь вывести без разделения на каналы сразу только один текст с исправленными грамматическими ошибками. Вот делай по этому примеру ### Оценка диалога #### Контакт и представление Менеджер + (Сюда вставь Имя Менеджера) корректно приветствует клиента, представляясь на двух языках и указывая клинику: **«сәлеметсіз бе сіз ново клиникасымен байланыстасыз... здравствуйте вы позвонили в медицинский центр ново...»**. #### Инициатива в переговорах Менеджер берет инициативу, уточняет город клиента и предоставляет информацию о доступных услугах. Однако, это могло быть выполнено более последовательно. #### Выявление потребностей Менеджер задает следующие вопросы для выявления потребностей: - **«А кт к сожалению не снимаем...»** - **«вам с контрастным или без контраста надо?»** - **«у вас есть направление?»** После уточнения, менеджер предлагает подходящую услугу, озвучивает её стоимость и время работы: **«пояснично отдел шестого поясничное кольцово отдел позвоночника будет стоить двадцать одна тысяча девятьсот тенге...»**. #### Предложение услуги Менеджер предлагает услугу после определения потребностей, озвучивает цену и наличие скидок: **«в ночное время с двадцати двух до шести ой двадцати двух до шести утра идет скидка восемнадцать тысяч тенге...»**. #### Уверенность и тональность Менеджер говорит спокойно и уверенно, но в речи есть некоторая неясность и многословие, что может снижать восприимчивость информации клиентом. ### Оценка по скрипту На основе выполненных шагов: 1. Установление контакта, представление и обозначение цели звонка: **8/10** 2. Взятие инициативы: **6/10** 3. Выявление потребностей: **7/10** 4. Предложение услуги и озвучивание стоимости: **7/10** 5. Общая уверенность и тональность: **7/10** ### Объективная оценка Я оцениваю диалог на **7 из 10**. ### Исправления грамматических ошибок #### Исключены определенные слова и добавлено больше ясности: 1. **Клиент:** - **\"А здравствуйте, меня зовут Александр. У вас можно делать КТ в Алматы?\"** - **\"Нет, у вас прям стоит КТ или МРТ? Вы снимаете поясничный отдел?\"** - **\"А где вы находитесь на Достык или Желтоксан (бывшая Мира)?\"** - **\"Мы просто, родственник приехал и хочет сделать МРТ.\"** - **\"А сколько стоит МРТ пояснично-кресцового отдела позвоночника?\"** - **\"Вы круглосуточно работаете или только днем?\"** - **\"Не порекомендуете, где можно сделать КТ?\"** - **\"Спасибо, до свидания.\"** 2. **Менеджер:** - **\"Сәлеметсіз бе, вы позвонили в медицинский центр 'Ново'. Для выбора русского языка нажмите два.\"** - **\"Колл-центр, меня зовут Пролага, чем могу вам помочь?\"** - **\"Здравствуйте, из какого вы города?\"** - **\"В Алматы, к сожалению, КТ не делаем. У нас есть МРТ, можем сделать поясничный отдел на Желтоксан, 62 (угол улицы Макатаева) или со стороны Абылай хана, 53.\"** - **\"С правой стороны от главного входа, вторая дверь. В этом здании находится 'Ново мед'. Есть необходимость ввода контраста? У вас есть направление?\"** - **\"Пояснично-кресцовый отдел позвоночника стоит 21,900 тенге. В ночное время с 22:00 до 06:00 скидка — 18,000 тенге.\"** - **\"Спасибо за обращение, до свидания.\"** ### Итог Можно сказать, что менеджер выполнил большинство пунктов скрипта, но в некоторых местах ему не хватило уверенности и четкости в ответах.:\n{transcript}"}

        ],
        max_tokens=1000
    )
    return response.choices[0].message['content'].strip()

def download_file(service, file_id):
    request = service.files().get_media(fileId=file_id)
    fh = io.BytesIO()
    downloader = MediaIoBaseDownload(fh, request)
    done = False
    while not done:
        _, done = downloader.next_chunk()
    fh.seek(0)
    return fh

def write_to_sheet(sheets_service, spreadsheet_id, range_name, values):
    body = {'values': values}
    result = sheets_service.spreadsheets().values().append(
        spreadsheetId=spreadsheet_id, range=range_name,
        valueInputOption='USER_ENTERED', body=body).execute()
    print(f'{result.get("updates").get("updatedRows")} rows updated.')

def process_audio_files(folder_id, spreadsheet_id):
    drive_service, sheets_service = authenticate_google_services()
    files = drive_service.files().list(q=f"'{folder_id}' in parents", fields="files(id, name)").execute().get('files', [])
    values = []

    # Process up to 10 files
    for i, file in enumerate(files[:10]):
        print(f"Processing {file['name']}")
        audio_content = download_file(drive_service, file['id'])
        
        # Save the audio content to a temporary file
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(audio_content.read())
            temp_file_path = temp_file.name

        # Speech recognition
        model = model_repository.recognition_model()
        model.model = 'general'
        model.language = 'auto'
        model.audio_processing_type = AudioProcessingType.Full
        result = model.transcribe_file(temp_file_path)
        combined_text = ""
        for c, res in enumerate(result):
            combined_text += f'channel: {c}\nraw_text: {res.raw_text}\nnorm_text: {res.normalized_text}\n'
        
        print(combined_text)

        # Analyze the transcript
        analysis_result = analyze_call(combined_text)
        values.append([file['name'], analysis_result])

        # Delete the temporary file
        os.remove(temp_file_path)

    # Write results to Google Sheets
    if values:
        write_to_sheet(sheets_service, spreadsheet_id, f'Лист1!A1', values)

# Google Drive and Sheets parameters
folder_id = '1zdeSBOOluR-MN0xeytxoRlIH2zQzoF5Z'
spreadsheet_id = '1v57Bcs9CCDPs5x2miP_tiYR2Q4ef-88NVrMFEsmCHvg'

# Start processing
if __name__ == '__main__':
    process_audio_files(folder_id, spreadsheet_id)
