# Вопрос №3 См по ссылке. Ответ сделай в своей ссылке. https://docs.google.com/document/d/1flxM012OkJ_uzXW7Z2FTprLocLSbcbDZKa5Y7jrRSEY/edit?usp=sharing 

# Откомментируйте код прямо в тексте:

##  все ***_ в именах переменных заменил на xxx_
import xml.etree.ElementTree as XmlElementTree
import httplib2
import uuid
from config import xxx
 
xxx_HOST = '***' # некий хост с api перевода аудио в текст
xxx_PATH = '/***_xml' # некий endpoint
CHUNK_SIZE = 1024 ** 2 # размер кусочков которыми будетм передавать файл.
 
def speech_to_text(filename=None, bytes=None, request_id=uuid.uuid4().hex, topic='notes', lang='ru-RU', key=xxx_API_KEY):

    if filename: # если дано имя файла; (логичнее 'if filename is None', файл с именем '0' не пройдет)
        with open(filename, 'br') as file: # открыть файл для чтения в бинарном виде
            bytes = file.read() # прочитать все содержимое в переменную
        # закрыли файл
    if not bytes: # если в файле пусто или имя файла не предоставили
        raise Exception('Neither file name nor bytes provided.') # выкинуть исключение


    bytes = convert_to_pcm16b16000r(in_bytes=bytes) # ? какая-то конвертация, по всей видимости в audio/x-pcm;bit=16;rate=16000
    ## ? convert_to_pcm16b16000r не определена (import)

    ##########

    url = xxx_PATH + '?uuid=%s&key=%s&topic=%s&lang=%s' % (
        request_id,
        key,
        topic,
        lang
    ) # объединяем путь из переменных
    
    ##########

    chunks = read_chunks(CHUNK_SIZE, bytes) # разделяем bytes на куусочки по CHUNK_SIZE = 1024 ** 2 байт
    ## ? read_chunks не определена (import)
    
    ##########

    connection = httplib2.HTTPConnectionWithTimeout(xxx_HOST) # создаем соединение к xxx

    connection.connect() # соединяемся
    connection.putrequest('POST', url) # посылаем POST запрос на url (host/url)
    connection.putheader('Transfer-Encoding', 'chunked') # посылаем заголовок (данные разбиты на кусочки)
    connection.putheader('Content-Type', 'audio/x-pcm;bit=16;rate=16000') # посылаем и еще один (тип посылаемых даннвх)
    connection.endheaders() # больше заголовков не будет


    for chunk in chunks:
        connection.send(('%s\r\n' % hex(len(chunk))[2:]).encode()) # переводим размер кусочка в hex убираем '0x' добавляем перевод строки и все переводим строку в байты; и наконец шлем
        connection.send(chunk) # шлем сам кусочек
        connection.send('\r\n'.encode()) # шлем перевод строки

    connection.send('0\r\n\r\n'.encode()) # шлём 0 и два перевода строки (по всей видимости означает конец данных?)
    response = connection.getresponse() # получаем ответ.

    ##########
    
    if response.code == 200: # если ответ ОК
        response_text = response.read() # читаем ответ
        xml = XmlElementTree.fromstring(response_text) # формируем xml

        ##########

        if int(xml.attrib['success']) == 1: # если успех
            max_confidence = - float("inf") # изначальная уверенность минимальная
            text = '' # пустой текст

            for child in xml:
                #берем тот  текст в котором больше уверенность
                if float(child.attrib['confidence']) > max_confidence:
                    text = child.text
                    max_confidence = float(child.attrib['confidence'])

            if max_confidence != - float("inf"): # если есть хоть какая-то уверенность
                return text # вернуть текст
            else:
                # иначе выкинуть исключение, что тект не найден
                raise SpeechException('No text found.\n\nResponse:\n%s' % (response_text))
        else:
            # иначе выкинуть исключение, что тект не найден
            raise SpeechException('No text found.\n\nResponse:\n%s' % (response_text))
    else:
        # иначе выкинуть исключение, с неизвестной ошибкой
        raise SpeechException('Unknown error.\nCode: %s\n\n%s' % (response.code, response.read()))


class SpeechException(Exception):
    """Выкиyть при ошибках перевода аудио в текст."""
    pass
