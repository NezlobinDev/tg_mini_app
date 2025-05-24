from aiogram import types


async def send_user_url_button(
        bot, user_id, btn_url,
        mess='Вам отправлена кнопка',
        btn_mess='button',
):
    """ Отправить пользователю кнопку(ссылку) """
    keyboard = types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text=btn_mess, web_app=types.WebAppInfo(url=btn_url))]],
        resize_keyboard=True,
    )
    return await bot.send_message(
        chat_id=user_id,
        text=mess,
        reply_markup=keyboard
    )
