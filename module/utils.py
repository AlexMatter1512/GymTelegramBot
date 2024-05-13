from telegram import InlineKeyboardMarkup, InlineKeyboardButton

class telegramTimeKeyboards:
    @staticmethod
    def get_week_days_keyboard(end_day: int = 7) -> InlineKeyboardMarkup:
        daysKeyboard = [
            [InlineKeyboardButton("Lunedì", callback_data=1)],
            [InlineKeyboardButton("Martedì", callback_data=2)],
            [InlineKeyboardButton("Mercoledì", callback_data=3)],
            [InlineKeyboardButton("Giovedì", callback_data=4)],
            [InlineKeyboardButton("Venerdì", callback_data=5)],
            [InlineKeyboardButton("Sabato", callback_data=6)],
            [InlineKeyboardButton("Domenica", callback_data=7)],
        ]
        # remove days after end_day
        daysKeyboard = daysKeyboard[:end_day]
        daysKeyboard.append([InlineKeyboardButton("Annulla", callback_data="/cancel")])
        return InlineKeyboardMarkup(daysKeyboard)
    
    @staticmethod
    def get_hours_keyboard(start_hour: int = 0, end_hour: int = 23) -> InlineKeyboardMarkup:
        hoursKeyboard = []
        for hour in range(start_hour, end_hour + 1, 2):
            hoursKeyboard.append([InlineKeyboardButton(f"{hour:02d}", callback_data=f"{hour:02d}"), InlineKeyboardButton(f"{hour + 1:02d}", callback_data=f"{hour + 1:02d}")])
        hoursKeyboard.append([InlineKeyboardButton("Annulla", callback_data="/cancel")])
        return InlineKeyboardMarkup(hoursKeyboard)

    @staticmethod
    def get_hours_partitions_keyboard(step: int) -> InlineKeyboardMarkup:
        # quartersKeyboard = [
        #     [InlineKeyboardButton("00", callback_data="00"), InlineKeyboardButton("15", callback_data="15")], 
        #     [InlineKeyboardButton("30", callback_data="30"), InlineKeyboardButton("45", callback_data="45")]
        # ]
        partitionsKeyboard = []
        for partition in range(0, 60, step):
            partitionsKeyboard.append([InlineKeyboardButton(f"{partition:02d}", callback_data=f"{partition:02d}")])

        partitionsKeyboard.append([InlineKeyboardButton("Annulla", callback_data="/cancel")])
        return InlineKeyboardMarkup(partitionsKeyboard)