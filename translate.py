from google.cloud import translate


def translate_from_google(text, target_language, format='text'):

    if (len(text) == 0 or len(target_language) == 0):
        return text
    try:
        client = translate.Client.from_service_account_json(
            './worldnews-280e6c76d336.json')
        result = client.translate(
            text, target_language=target_language, format_=format)
        return result['translatedText']
    except Exception as e:
        print('Failed to translate text: ' + str(e))
        print("Google translate exception")
        return text
