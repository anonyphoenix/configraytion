from telethon import Button
import i18n

def paginate(data_prefix, current_page=1, total_pages=1, delimiter=':', before=None, after=None):
    data_prefix += delimiter
    keyboard = []
    if total_pages > current_page + 1:
        keyboard.append(Button.inline(i18n.get('LAST'), str.encode(data_prefix + str(total_pages))))
    if total_pages > current_page:
        keyboard.append(Button.inline(i18n.get('NEXT'), str.encode(data_prefix + str(current_page + 1))))
    if total_pages > 1:
        keyboard.append(Button.inline(str(current_page) + ' ' + i18n.get('FROM') + ' ' + str(total_pages)))
    if current_page > 1:
        keyboard.append(Button.inline(i18n.get('PREVIOUS'), str.encode(data_prefix + str(current_page - 1))))
    if current_page > 2:
        keyboard.append(Button.inline(i18n.get('FIRST'), str.encode(data_prefix + '1')))
    if before or after:
        keyboard = [keyboard]
    if before:
        keyboard = before + keyboard
    if after:
        keyboard.append(after)
    return keyboard